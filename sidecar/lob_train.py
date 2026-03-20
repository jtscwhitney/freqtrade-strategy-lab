#!/usr/bin/env python3
"""
lob_train.py — Phase 1: Feature Validation + CatBoost Model Training
=====================================================================
Loads historical Parquet data (from lob_historical.py), computes multi-horizon
forward log-return targets, trains a CatBoost regressor with a direction-penalised
GMADL objective, and produces a signal-survival report that determines whether
the LOB edge survives at Freqtrade-compatible timeframes.

Usage:
    python sidecar/lob_train.py                          # BTC + ETH, defaults
    python sidecar/lob_train.py --symbols BTCUSDT        # single symbol
    python sidecar/lob_train.py --dry-run                # feature report only
    python sidecar/lob_train.py --save-model             # save on GO verdict

Dependencies:
    pip install catboost scipy pyarrow pandas numpy

Architecture notes:
    - L1 book features (spread_rel, bid/ask qty, vol_imbalance) are NaN in
      historical data — excluded from training.
    - `mid` is excluded as a feature (non-stationary price level, kills
      cross-asset portability). Used only for target computation.
    - `symbol` is included as a CatBoost categorical feature so the model
      learns per-symbol OFI thresholds (raw USD OFI is not comparable across
      assets with different notional volumes).
    - Target computation is done per-symbol before concatenation to prevent
      cross-symbol timestamp lookups.
    - First 120 rows of each symbol's first day are dropped (OFI_120s warm-up
      contamination — no prev_buf on first day).
    - GMADL: MAE-based loss with asymmetric direction penalty. Wrong-direction
      predictions (sign(pred) != sign(target)) are penalised by factor alpha.
      Gradient = penalty * sign(pred - target). Hessian = penalty (constant).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

try:
    from catboost import CatBoostRegressor, Pool
except ImportError:
    print("ERROR: catboost not installed.  Run:  pip install catboost")
    sys.exit(1)

try:
    from scipy.stats import spearmanr as _spearmanr
    _SCIPY = True
except ImportError:
    _SCIPY = False

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE    = Path(__file__).parent
BASE_DIR = _HERE.parent
DATA_DIR = BASE_DIR / "sidecar" / "data" / "lob_raw"
MODEL_DIR = BASE_DIR / "user_data" / "models"
LOG_PATH  = BASE_DIR / "sidecar" / "logs" / "lob_train.log"

# ── Feature / target config ───────────────────────────────────────────────────
# L1 book features are NaN in historical data — excluded.
# `mid` excluded (non-stationary price level, no cross-asset portability).
FLOW_FEATURE_COLS: list[str] = [
    "ofi_5s",   "buy_vwap_dev_5s",  "sell_vwap_dev_5s",
    "ofi_30s",  "buy_vwap_dev_30s", "sell_vwap_dev_30s",
    "ofi_120s", "buy_vwap_dev_120s","sell_vwap_dev_120s",
]
CAT_COLS: list[str] = ["symbol"]     # OFI is raw USD — vary hugely across symbols
ALL_FEATURE_COLS   = FLOW_FEATURE_COLS + CAT_COLS
CAT_FEATURE_IDX    = list(range(len(FLOW_FEATURE_COLS), len(ALL_FEATURE_COLS)))

TARGET_HORIZONS_S: list[int] = [3, 5, 15, 60, 300]
PRIMARY_HORIZON_S: int       = 3
PURGE_GAP_S: int             = 300   # 5-min purge gap between train/val/test
TRAIN_FRAC: float            = 0.70
VAL_FRAC:   float            = 0.15  # test = remainder

TAKER_FEE_RT: float          = 0.001  # 0.1% Binance Futures round-trip taker fee
WARMUP_ROWS:  int             = 120    # OFI_120s warm-up period (first day only)


# ── Logging ───────────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("lob_train")


logger = _setup_logging()


# ── GMADL custom CatBoost objective ──────────────────────────────────────────

class GMADLObjective:
    """
    Generalised Mean Absolute Directional Loss.

    L = penalty * |pred - target|
    where penalty = alpha  if sign(pred) != sign(target) and target != 0
                  = 1.0    otherwise

    Gradient (dL/d_pred) = penalty * (pred - target)   [MSE-style residual]
    Hessian              = penalty                      [positive-definite]

    Note: pure MAE gradients (sign(residual)) cause gradient boosting collapse
    because constant-magnitude updates give CatBoost no curvature signal —
    all samples look equally important regardless of residual size.  MSE-style
    residuals give magnitude-proportional updates while still applying the
    direction penalty.  This is "directional MSE" (GMSE), which preserves the
    paper's key property while remaining convergent.
    """

    def __init__(self, alpha: float = 2.0) -> None:
        self.alpha = alpha

    def calc_ders_range(
        self,
        approxes: list[float],
        targets:  list[float],
        weights:  list[float] | None,
    ) -> list[tuple[float, float]]:
        a = np.asarray(approxes, dtype=np.float64)
        t = np.asarray(targets,  dtype=np.float64)

        wrong_dir = (t != 0.0) & ((a * t) < 0.0)   # different signs
        penalty   = np.where(wrong_dir, self.alpha, 1.0)

        grad = penalty * (a - t)    # MSE-style: magnitude-proportional
        hess = penalty              # always > 0

        if weights is not None:
            w    = np.asarray(weights, dtype=np.float64)
            grad = grad * w
            hess = hess * w

        return list(zip(grad.tolist(), hess.tolist()))


# ── Data loading ──────────────────────────────────────────────────────────────

def load_symbol(symbol: str) -> pd.DataFrame | None:
    """
    Load all Parquet files for symbol, sort by timestamp.
    Returns: timestamp_utc, mid, FLOW_FEATURE_COLS, symbol.
    Drops first WARMUP_ROWS rows (OFI_120s warm-up contamination).
    """
    sym_dir = DATA_DIR / symbol
    if not sym_dir.exists():
        logger.warning("No data directory: %s", sym_dir)
        return None

    paths = sorted(sym_dir.glob("**/*.parquet"))
    if not paths:
        logger.warning("No parquet files for %s", symbol)
        return None

    load_cols = ["timestamp_utc", "mid"] + FLOW_FEATURE_COLS
    frames    = [pq.read_table(p, columns=load_cols).to_pandas() for p in paths]
    df        = (
        pd.concat(frames, ignore_index=True)
        .sort_values("timestamp_utc", ignore_index=True)
    )

    before = len(df)
    df = df.dropna(subset=FLOW_FEATURE_COLS)
    if len(df) < before:
        logger.warning("%s: dropped %d NaN-feature rows", symbol, before - len(df))

    # Drop warm-up rows (first day has no prev_buf → OFI_120s unreliable)
    df = df.iloc[WARMUP_ROWS:].reset_index(drop=True)

    df["symbol"] = symbol
    logger.info("%s: %d rows  (%.1f days)", symbol, len(df), len(df) / 86_400)
    return df


# ── Target computation ────────────────────────────────────────────────────────

def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute log(mid[t+h] / mid[t]) for each horizon h.

    Uses binary search on sorted timestamp_utc — correctly handles day
    boundaries since data is loaded as one continuous sorted array per symbol.
    Rows where no future timestamp exists within h+1s receive NaN.

    IMPORTANT: Call this per-symbol BEFORE concatenating multiple symbols.
    Cross-symbol concatenation would cause BTC future-mid to be looked up
    from ETH timestamps.
    """
    ts  = df["timestamp_utc"].to_numpy(dtype=np.float64)
    mid = df["mid"].to_numpy(dtype=np.float64)
    n   = len(df)

    for h in TARGET_HORIZONS_S:
        future_ts   = ts + h
        idx         = np.searchsorted(ts, future_ts, side="left")
        idx_clipped = np.minimum(idx, n - 1)

        # Valid only if the found timestamp is within 1s of expected future time
        # (protects against false matches across maintenance-window gaps)
        valid = (idx < n) & (np.abs(ts[idx_clipped] - future_ts) <= 1.0)

        target = np.full(n, np.nan, dtype=np.float64)
        target[valid] = np.log(mid[idx_clipped[valid]] / mid[valid])

        df[f"target_{h}s"] = target

    return df


# ── Feature distribution report ───────────────────────────────────────────────

def feature_report(df: pd.DataFrame, symbol: str) -> None:
    """
    Log feature distribution stats and flag anomalies.
    Run per-symbol before concatenation for clearest signal.
    """
    logger.info("--- Feature report: %s ---", symbol)
    tgt = f"target_{PRIMARY_HORIZON_S}s"
    all_cols = FLOW_FEATURE_COLS + ([tgt] if tgt in df.columns else [])
    for col in all_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        logger.info(
            "  %-28s  mean=%+.3e  std=%.3e  p5=%.3e  p95=%.3e",
            col, s.mean(), s.std(), s.quantile(0.05), s.quantile(0.95),
        )

    # OFI symmetry: should be near zero mean for liquid markets
    for w in (5, 30, 120):
        col  = f"ofi_{w}s"
        s    = df[col].dropna()
        bias = abs(s.mean()) / (s.std() + 1e-12)
        if bias > 0.05:
            logger.warning(
                "  [CHECK] %s mean bias = %.3f std — verify buy/sell labelling", col, bias
            )

    # Target std sanity check
    if tgt in df.columns:
        std_bp = df[tgt].dropna().std() * 1e4
        if std_bp < 0.1:
            logger.warning("  [CHECK] Target std %.2f bps is suspiciously small", std_bp)
        elif std_bp > 50:
            logger.warning("  [CHECK] Target std %.2f bps is very large", std_bp)
        else:
            logger.info("  Target 3s std: %.2f bps  [OK]", std_bp)


# ── Train / val / test split ──────────────────────────────────────────────────

def make_splits(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Timestamp-based 70/15/15 split with PURGE_GAP_S purge at each boundary.

    Using timestamps (not row indices) ensures both symbols in a multi-symbol
    concat are split at the same calendar date.
    """
    ts_min = df["timestamp_utc"].min()
    ts_max = df["timestamp_utc"].max()
    span   = ts_max - ts_min

    t1 = ts_min + span * TRAIN_FRAC
    t2 = ts_min + span * (TRAIN_FRAC + VAL_FRAC)

    train = df[df["timestamp_utc"] <= t1 - PURGE_GAP_S]
    val   = df[
        (df["timestamp_utc"] >= t1 + PURGE_GAP_S) &
        (df["timestamp_utc"] <= t2 - PURGE_GAP_S)
    ]
    test  = df[df["timestamp_utc"] >= t2 + PURGE_GAP_S]

    logger.info(
        "Split: train=%d  val=%d  test=%d  (±%ds purge at each boundary)",
        len(train), len(val), len(test), PURGE_GAP_S,
    )
    return train, val, test


# ── CatBoost training ─────────────────────────────────────────────────────────

def train_model(
    train:        pd.DataFrame,
    val:          pd.DataFrame,
    alpha:        float = 2.0,
    iterations:   int   = 500,
    train_rows:   int   = 1_000_000,
) -> CatBoostRegressor:
    """
    Train CatBoost with GMADL objective and early stopping on val MAE.
    `symbol` is included as a categorical feature.

    train_rows: randomly subsample training set to this many rows before
    building the Pool. The custom Python objective callback is the bottleneck
    at full 13M scale (~2h). 1M rows gives ~10-15 min runtime with no
    meaningful loss of signal quality for Phase 1 validation.
    """
    tgt = f"target_{PRIMARY_HORIZON_S}s"

    def _make_pool(split: pd.DataFrame, max_rows: int | None = None) -> Pool:
        mask = split[tgt].notna()
        df   = split.loc[mask]
        if max_rows and len(df) > max_rows:
            df = df.sample(n=max_rows, random_state=42)
            logger.info("  Subsampled to %d rows", len(df))
        X = df[ALL_FEATURE_COLS]
        y = df[tgt].to_numpy(dtype=np.float32)
        return Pool(X, y, cat_features=CAT_COLS)

    train_pool = _make_pool(train, max_rows=train_rows)
    val_pool   = _make_pool(val)   # use full val set for reliable early stopping

    logger.info(
        "Training: %d samples  Validation: %d samples",
        train_pool.num_row(), val_pool.num_row(),
    )

    model = CatBoostRegressor(
        iterations    = iterations,
        depth         = 4,           # shallower trees → faster + less overfit at this scale
        learning_rate = 0.05,
        loss_function = GMADLObjective(alpha=alpha),
        eval_metric   = "MAE",
        l2_leaf_reg   = 30,          # prevents degenerate solution with custom objective
        random_seed   = 42,
        od_type       = "Iter",
        od_wait       = 50,
        verbose       = 50,
    )
    model.fit(train_pool, eval_set=val_pool, use_best_model=True)
    logger.info("Best iteration: %d", getattr(model, "best_iteration_", "N/A"))
    return model


# ── Signal survival analysis ──────────────────────────────────────────────────

def signal_survival(
    model: CatBoostRegressor,
    test:  pd.DataFrame,
) -> dict[int, dict[str, float]]:
    """
    Test whether 1s CatBoost predictions (trained on 3s target) are
    directionally predictive of longer forward returns.

    Metrics (per horizon h):
        dir_acc       — unconditional: fraction where sign(pred) == sign(actual)
        dir_acc_t20   — conditional: directional accuracy for top-20% |pred| signals
        ic            — Spearman rank correlation (NaN if scipy unavailable)
        pnl_t20_bps   — fee-adjusted P&L in bps/trade for top-20% signals only.
                        Top-20% simulates threshold filtering (one fee per trade).
                        Unconditional P&L is always negative at 1s frequency due to
                        fee dominance — the threshold view is the actionable metric.
    """
    X_test = test[ALL_FEATURE_COLS]
    preds  = model.predict(X_test)

    results: dict[int, dict[str, float]] = {}
    logger.info("--- Signal survival (out-of-sample) ---")
    logger.info(
        "  %-8s  %-10s  %-12s  %-10s  %-22s",
        "Horizon", "Dir Acc", "DA top-20%", "IC", "Net P&L bps (top-20%)",
    )

    for h in TARGET_HORIZONS_S:
        tgt_col = f"target_{h}s"
        if tgt_col not in test.columns:
            continue

        y     = test[tgt_col].to_numpy(dtype=np.float64)
        valid = ~np.isnan(y)
        if valid.sum() < 1000:
            logger.warning("  %ds: insufficient valid samples (%d) -- skip", h, valid.sum())
            continue

        p = preds[valid]
        y = y[valid]

        # Unconditional directional accuracy
        dir_acc = float(np.mean(np.sign(p) == np.sign(y)))

        # Conditional: top 20% strongest signals (|pred| >= 80th percentile)
        threshold   = np.percentile(np.abs(p), 80)
        strong      = np.abs(p) >= threshold
        dir_acc_t20 = float(np.mean(np.sign(p[strong]) == np.sign(y[strong])))

        # Fee-adjusted P&L for top-20% signals (one fee per trade)
        net_t20     = np.sign(p[strong]) * y[strong] - TAKER_FEE_RT
        pnl_t20_bps = float(net_t20.mean() * 1e4)

        if _SCIPY:
            try:
                sr = _spearmanr(p, y)
                ic = float(sr.statistic if hasattr(sr, "statistic") else sr[0])
            except Exception:
                ic = float("nan")
        else:
            ic = float("nan")

        results[h] = {
            "dir_acc":     dir_acc,
            "dir_acc_t20": dir_acc_t20,
            "ic":          ic,
            "pnl_t20_bps": pnl_t20_bps,
        }
        logger.info(
            "  %-8s  %-10.4f  %-12.4f  %-10.4f  %-22.4f",
            f"{h}s", dir_acc, dir_acc_t20, ic, pnl_t20_bps,
        )

    return results


# ── Threshold sweep ───────────────────────────────────────────────────────────

def threshold_sweep(
    model: CatBoostRegressor,
    test:  pd.DataFrame,
) -> None:
    """
    Sweep |prediction| thresholds to find whether any filter produces positive
    net P&L after round-trip taker fee.

    For each horizon and each percentile cutoff, reports:
        N trades    — how many signals pass the filter
        Coverage    — fraction of total test rows selected
        Dir Acc     — directional accuracy of filtered signals
        Mean |move| — average absolute actual return (bps) for selected rows
        Net P&L     — mean(sign(pred)*actual - fee) in bps per trade

    A positive Net P&L at any (horizon, threshold) pair means the strategy is
    fee-viable at that operating point.
    """
    X_test = test[ALL_FEATURE_COLS]
    preds  = model.predict(X_test)

    # Percentile cutoffs: top-N% = |pred| >= (100-N)th percentile
    pct_cuts = [50, 60, 70, 80, 90, 95, 98, 99, 99.5]

    logger.info("=" * 60)
    logger.info("THRESHOLD SWEEP  (fee = %.0f bps round-trip)", TAKER_FEE_RT * 1e4)
    logger.info("=" * 60)

    any_positive = False

    for h in TARGET_HORIZONS_S:
        tgt_col = f"target_{h}s"
        if tgt_col not in test.columns:
            continue

        y_all  = test[tgt_col].to_numpy(dtype=np.float64)
        valid  = ~np.isnan(y_all)
        p      = preds[valid]
        y      = y_all[valid]
        n_tot  = valid.sum()

        logger.info("")
        logger.info("  Horizon: %ds  (n=%d valid test rows)", h, n_tot)
        logger.info(
            "  %-11s  %-9s  %-9s  %-10s  %-16s  %s",
            "Top-%", "N trades", "Coverage", "Dir Acc", "Mean |move| bps", "Net P&L bps/trade",
        )

        horizon_positive = False
        for pct in pct_cuts:
            thresh = np.percentile(np.abs(p), pct)
            mask   = np.abs(p) >= thresh
            n_sel  = int(mask.sum())
            if n_sel < 50:
                break   # too few samples for reliable estimate

            p_sel  = p[mask]
            y_sel  = y[mask]

            dir_acc       = float(np.mean(np.sign(p_sel) == np.sign(y_sel)))
            mean_move_bps = float(np.abs(y_sel).mean() * 1e4)
            net_pnl_bps   = float((np.sign(p_sel) * y_sel - TAKER_FEE_RT).mean() * 1e4)
            coverage      = n_sel / n_tot

            marker = "  <-- POSITIVE" if net_pnl_bps > 0 else ""
            if net_pnl_bps > 0:
                horizon_positive = True
                any_positive = True

            logger.info(
                "  %-11s  %-9d  %-9.4f  %-10.4f  %-16.3f  %.4f%s",
                f"top-{100 - pct:.1f}%", n_sel, coverage, dir_acc,
                mean_move_bps, net_pnl_bps, marker,
            )

        if not horizon_positive:
            logger.warning("  No profitable threshold at %ds horizon", h)

    logger.info("")
    if any_positive:
        logger.info("SWEEP RESULT: Profitable operating point(s) found — PATH B viable")
    else:
        logger.warning(
            "SWEEP RESULT: No profitable threshold at any horizon. "
            "Signal is real but fee-dominated. Retrain with full L1 features "
            "from live collector data before concluding this edge is dead."
        )
    logger.info("=" * 60)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LOB Phase 1: feature validation + CatBoost training"
    )
    parser.add_argument(
        "--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT"],
        help="Symbols to include (default: BTCUSDT ETHUSDT)",
    )
    parser.add_argument(
        "--alpha", type=float, default=2.0,
        help="GMADL wrong-direction penalty multiplier (default: 2.0)",
    )
    parser.add_argument(
        "--iterations", type=int, default=500,
        help="CatBoost max iterations (default: 500, early stops before)",
    )
    parser.add_argument(
        "--save-model", action="store_true",
        help="Save model to user_data/models/lob_catboost_v01.cbm on GO verdict",
    )
    parser.add_argument(
        "--load-model", type=str, default=None, metavar="PATH",
        help="Load saved .cbm model (skip training). Still loads data and runs signal survival + threshold sweep.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Feature distribution report only — skip training",
    )
    args = parser.parse_args()

    logger.info("LOB Phase 1 | symbols=%s | features=%d | horizon=%ds",
                args.symbols, len(FLOW_FEATURE_COLS), PRIMARY_HORIZON_S)
    if not _SCIPY:
        logger.warning("scipy not found — IC will be NaN.  pip install scipy")

    # ── 1. Load data (per-symbol, then concat) ─────────────────────────────
    frames: list[pd.DataFrame] = []
    for sym in args.symbols:
        df = load_symbol(sym)
        if df is None:
            continue
        # Targets computed per-symbol BEFORE concat to avoid cross-symbol lookups
        df = add_targets(df)
        feature_report(df, sym)
        frames.append(df)

    if not frames:
        logger.error("No data loaded. Check sidecar/data/lob_raw/ paths.")
        sys.exit(1)

    all_data = (
        pd.concat(frames, ignore_index=True)
        .sort_values("timestamp_utc", ignore_index=True)
    )
    logger.info("Total rows across %d symbols: %d", len(frames), len(all_data))

    if args.dry_run:
        logger.info("--dry-run: stopping after feature report.")
        return

    # ── 2. Split ────────────────────────────────────────────────────────────
    tgt_col  = f"target_{PRIMARY_HORIZON_S}s"
    all_data = all_data.dropna(subset=[tgt_col])
    logger.info("Rows with valid %s target: %d", tgt_col, len(all_data))

    train, val, test = make_splits(all_data)

    # ── 3. Train (or load) ──────────────────────────────────────────────────
    if args.load_model:
        model = CatBoostRegressor()
        model.load_model(args.load_model)
        logger.info("Loaded model from %s  (skipping training)", args.load_model)
    else:
        logger.info(
            "Training CatBoost (GMADL alpha=%.1f, max_iter=%d)...",
            args.alpha, args.iterations,
        )
        model = train_model(train, val, alpha=args.alpha, iterations=args.iterations)

    # ── 4. Feature importance ───────────────────────────────────────────────
    try:
        importances = dict(zip(ALL_FEATURE_COLS, model.feature_importances_))
        ranked      = sorted(importances.items(), key=lambda x: -x[1])
        logger.info("--- Feature importances ---")
        for rank, (feat, imp) in enumerate(ranked, 1):
            logger.info("  #%d  %-28s  %.2f%%", rank, feat, imp)
    except Exception:
        ranked = []
        logger.info("Feature importances not available for loaded model")

    # ── 5. Signal survival ──────────────────────────────────────────────────
    results = signal_survival(model, test)

    # ── 5b. Threshold sweep ─────────────────────────────────────────────────
    threshold_sweep(model, test)

    # ── 6. Go / No-Go assessment ────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("GO / NO-GO ASSESSMENT")
    logger.info("=" * 60)

    r3     = results.get(PRIMARY_HORIZON_S, {})
    da_3s  = r3.get("dir_acc", 0.0)

    viable_da  = [h for h, r in results.items() if r["dir_acc"] > 0.51]
    viable_pnl = [h for h, r in results.items() if r.get("pnl_t20_bps", -999) > 0.0]

    # OFI features in top 3
    ofi_ranks     = [i + 1 for i, (f, _) in enumerate(ranked) if "ofi" in f]
    best_ofi_rank = ofi_ranks[0] if ofi_ranks else 999

    logger.info("3s directional accuracy : %.4f  (threshold > 0.52)", da_3s)
    logger.info("Horizons dir_acc > 51%% : %s", [f"{h}s" for h in viable_da])
    logger.info("Horizons net P&L  > 0   : %s  (top-20%% signals, 10bps fee)", [f"{h}s" for h in viable_pnl])
    logger.info("OFI feature ranks       : %s  (best: #%d, threshold <= 3)", ofi_ranks, best_ofi_rank)

    # Path determination based on signal survival horizon
    max_da_horizon = max(viable_da, default=0)
    if max_da_horizon >= 60:
        logger.info("PATH A viable: signal survives to %ds — Freqtrade 1m+ integration possible", max_da_horizon)
    elif max_da_horizon >= 5:
        logger.info("PATH B likely: signal dies before 1m — sub-minute execution needed")
    else:
        logger.warning("Signal does not survive any tested horizon above 3s")

    # Fee economics note (informational, not a gate in Phase 1)
    if not viable_pnl:
        logger.warning(
            "Fee economics: net P&L negative at all horizons (10bps taker fee >> move magnitude). "
            "Phase 2 must calibrate a high signal threshold to filter for larger moves."
        )

    # Phase 1 criteria (from Deep Dive spec)
    go_dir    = da_3s > 0.52
    go_ofi    = best_ofi_rank <= 3
    go_signal = len(viable_da) > 0    # edge survives at least one horizon > 3s
    verdict   = go_dir and go_ofi and go_signal

    logger.info(
        "Criteria: dir_acc>0.52=%s  OFI_top3=%s  signal_survival=%s",
        go_dir, go_ofi, go_signal,
    )
    if verdict:
        logger.info("VERDICT: CONDITIONAL GO — proceed to Phase 2")
        if max_da_horizon >= 60:
            logger.info("  >> Path A (Freqtrade 1m): signal survives to %ds — standard integration viable", max_da_horizon)
        else:
            logger.info("  >> Path B (sub-minute): signal dies before 1m (max viable horizon: %ds)", max_da_horizon)
            logger.info("  >> Path A (Freqtrade 1m): possible with high threshold, but signal at 60s is weak")
        logger.info("  >> Phase 2 priority: calibrate entry threshold on held-out test set")
    else:
        logger.info("VERDICT: NO GO")
    logger.info("=" * 60)

    # ── 7. Save model ────────────────────────────────────────────────────────
    if args.save_model:
        if verdict:
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            out = MODEL_DIR / "lob_catboost_v01.cbm"
            model.save_model(str(out))
            logger.info("Model saved: %s", out)
        else:
            logger.warning(
                "--save-model requested but verdict is NO GO; model not saved."
            )


if __name__ == "__main__":
    main()
