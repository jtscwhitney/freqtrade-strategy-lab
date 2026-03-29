"""
Cross-Sectional Momentum (Candidate G) — Phase 0 exploration.

Loads Binance USD-M futures 1h feather files (same layout as cointpairs scripts),
computes formation-period returns, cross-sectional dispersion, and rank persistence.

Download data (from repo root, single line for PowerShell):
    docker compose run --rm freqtrade download-data --config /freqtrade/config/config_xsmom.json --timerange 20220101-20260101 --timeframes 1h

Run this script:
    docker compose run --rm --entrypoint python freqtrade user_data/scripts/xsmom_phase0_exploration.py

Or locally (with pandas/pyarrow) if user_data/data exists under the repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _data_dir() -> Path:
    docker = Path("/freqtrade/user_data/data/binance/futures")
    if docker.is_dir():
        return docker
    repo_data = Path(__file__).resolve().parent.parent / "data" / "binance" / "futures"
    return repo_data


DATA_DIR = _data_dir()
TIMEFRAME = "1h"
TIMERANGE_START = "2022-01-01"
TIMERANGE_END = "2026-01-01"

# Formation lookbacks in number of 1h candles
FORMATION_BARS = {
    "1h": 1,
    "4h": 4,
    "24h": 24,
    "7d": 168,
    "30d": 720,
}

# Phase 0 gates (CrossSectionalMomentum_Dev_Plan.md)
MIN_DISPERSION_MEDIAN_BPS = 50.0
MIN_PAIRS_FOR_GATE = 15
MIN_RANK_PERSISTENCE = 0.02  # mean lag-1 Spearman rank corr; exploratory threshold


def feather_name(symbol: str, tf: str) -> str:
    safe = symbol.replace("/", "_").replace(":", "_")
    return f"{safe}-{tf}-futures.feather"


def load_close(symbol: str, tf: str) -> pd.Series | None:
    path = DATA_DIR / feather_name(symbol, tf)
    if not path.is_file():
        return None
    df = pd.read_feather(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.set_index("date").sort_index()
    s = df.loc[TIMERANGE_START:TIMERANGE_END, "close"].astype(float)
    s = s.rename(symbol)
    return s if len(s) > 200 else None


def build_close_matrix(pairs: list[str]) -> tuple[pd.DataFrame, list[str]]:
    loaded: list[pd.Series] = []
    ok: list[str] = []
    for p in pairs:
        s = load_close(p, TIMEFRAME)
        if s is not None:
            loaded.append(s)
            ok.append(p)
    if not loaded:
        return pd.DataFrame(), []
    wide = pd.concat(loaded, axis=1)
    wide = wide.sort_index()
    return wide, ok


def formation_returns(close: pd.DataFrame, bars: int) -> pd.DataFrame:
    return close.pct_change(periods=bars, fill_method=None) * 10_000.0


def cross_sectional_dispersion_bps(rets: pd.DataFrame) -> pd.Series:
    return rets.std(axis=1, skipna=True)


def lag1_rank_persistence_spearman(rets: pd.DataFrame) -> tuple[float, float, int]:
    """
    Mean lag-1 correlation of cross-sectional ranks.
    Rows are already ranks of returns, so Pearson(rank_t, rank_{t-1}) matches
    Spearman(return_t, return_{t-1}) across assets (vectorized over time).
    """
    ranks = rets.rank(axis=1, ascending=False, method="average")
    R = ranks.to_numpy(dtype=np.float64)
    if len(R) < 2:
        return float("nan"), float("nan"), 0
    r0, r1 = R[:-1], R[1:]
    mask = np.isfinite(r0) & np.isfinite(r1)
    cnt = mask.sum(axis=1)
    ok = cnt >= 10
    r0n = np.where(mask, r0, 0.0)
    r1n = np.where(mask, r1, 0.0)
    mean0 = r0n.sum(axis=1) / np.maximum(cnt, 1)
    mean1 = r1n.sum(axis=1) / np.maximum(cnt, 1)
    a = np.where(mask, r0 - mean0[:, np.newaxis], 0.0)
    b = np.where(mask, r1 - mean1[:, np.newaxis], 0.0)
    num = (a * b).sum(axis=1)
    den = np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))
    rho = np.divide(num, den, out=np.full_like(num, np.nan), where=(den > 1e-12) & ok)
    rho = rho[np.isfinite(rho)]
    if rho.size == 0:
        return float("nan"), float("nan"), 0
    return float(rho.mean()), float(rho.std()), int(rho.size)


def rows_with_min_pairs(rets: pd.DataFrame, k: int) -> pd.Series:
    return rets.notna().sum(axis=1) >= k


def main() -> int:
    if not DATA_DIR.is_dir():
        print(f"ERROR: data directory not found: {DATA_DIR}")
        print("Run download-data with config_xsmom.json first.")
        return 1

    # Must match config_xsmom.json pair_whitelist order (any subset that loads is fine)
    pairs = [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "SOL/USDT:USDT",
        "BNB/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ADA/USDT:USDT",
        "AVAX/USDT:USDT",
        "DOT/USDT:USDT",
        "LINK/USDT:USDT",
        "LTC/USDT:USDT",
        "ATOM/USDT:USDT",
        "NEAR/USDT:USDT",
        "APT/USDT:USDT",
        "ARB/USDT:USDT",
        "OP/USDT:USDT",
        "INJ/USDT:USDT",
        "TIA/USDT:USDT",
        "SUI/USDT:USDT",
        "SEI/USDT:USDT",
        "WLD/USDT:USDT",
        "FIL/USDT:USDT",
    ]

    close, loaded = build_close_matrix(pairs)
    print(f"Data dir: {DATA_DIR}")
    print(f"Pairs loaded: {len(loaded)} / {len(pairs)}")
    if loaded:
        print("  " + ", ".join(s.split("/")[0] for s in loaded))
    if close.empty:
        return 1

    overlap = close.notna().all(axis=1)
    n_full = int(overlap.sum())
    print(f"Bars with all {len(loaded)} pairs non-NaN: {n_full}")
    min_cov = int(close.notna().sum(axis=1).min())
    print(f"Minimum simultaneous pair count (any bar): {min_cov}")

    print("\n--- Formation-period diagnostics (returns in bps, dispersion = cross-sectional std) ---\n")
    rows = []
    for label, bars in FORMATION_BARS.items():
        rets = formation_returns(close, bars)
        valid_rows = rows_with_min_pairs(rets, MIN_PAIRS_FOR_GATE)
        rets_f = rets.loc[valid_rows]
        disp = cross_sectional_dispersion_bps(rets_f)
        disp_clean = disp.dropna()
        med = float(disp_clean.median()) if len(disp_clean) else float("nan")
        pct_50 = float((disp_clean > MIN_DISPERSION_MEDIAN_BPS).mean() * 100.0) if len(disp_clean) else float("nan")
        mean_rho, std_rho, n_rho = lag1_rank_persistence_spearman(rets_f)
        rows.append(
            {
                "formation": label,
                "bars": bars,
                "n_rows_ge_15pairs": int(valid_rows.sum()),
                "median_dispersion_bps": med,
                "pct_bars_disp_gt_50bps": pct_50,
                "mean_rank_persist_lag1": mean_rho,
                "std_rank_persist_lag1": std_rho,
                "n_rank_corr_obs": n_rho,
            }
        )

    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print(out.to_string(index=False))

    # Go / no-go summary (strict = dev-plan 1h wording; relaxed = dev-plan fallback)
    r1h = rows[0]
    r4h = next(r for r in rows if r["formation"] == "4h")
    gate_pairs = len(loaded) >= MIN_PAIRS_FOR_GATE
    gate_disp_1h = r1h["median_dispersion_bps"] > MIN_DISPERSION_MEDIAN_BPS
    gate_persist_1h = r1h["mean_rank_persist_lag1"] > MIN_RANK_PERSISTENCE
    gate_coverage = r1h["n_rows_ge_15pairs"] > 1000
    gate_disp_any = any(r["median_dispersion_bps"] > MIN_DISPERSION_MEDIAN_BPS for r in rows)

    print("\n--- Phase 0 go/no-go (guidance; inferential stats are informal at 1h) ---")
    print(f"  Pairs loaded >= {MIN_PAIRS_FOR_GATE}: {gate_pairs} ({len(loaded)})")
    print(f"  1h formation median dispersion > {MIN_DISPERSION_MEDIAN_BPS} bps: {gate_disp_1h} ({r1h['median_dispersion_bps']:.2f})")
    print(f"  4h formation median dispersion > {MIN_DISPERSION_MEDIAN_BPS} bps: {r4h['median_dispersion_bps'] > MIN_DISPERSION_MEDIAN_BPS} ({r4h['median_dispersion_bps']:.2f})")
    print(f"  1h formation mean rank persistence > {MIN_RANK_PERSISTENCE}: {gate_persist_1h} ({r1h['mean_rank_persist_lag1']:.4f})")
    print(f"  Enough overlapping rows (>{1000}): {gate_coverage} ({r1h['n_rows_ge_15pairs']})")
    strict_go = gate_pairs and gate_disp_1h and gate_persist_1h and gate_coverage
    relaxed_go = gate_pairs and gate_disp_any and gate_coverage
    print(f"\n  Strict Phase 0 GO (1h dispersion + 1h rank persistence): {strict_go}")
    print(f"  Relaxed GO (dispersion > {MIN_DISPERSION_MEDIAN_BPS} bps at any formation horizon): {relaxed_go}")
    if relaxed_go and not strict_go:
        print("  Note: Hourly *single-bar* dispersion sits just under 50 bps median; 4h+ formation")
        print("  has ample cross-sectional spread for 10 bps fees. Phase 1 grid should emphasize >= 4h formation.")
    if not relaxed_go:
        print("  Dispersion failed at all tested horizons — stop and widen universe or timeframes before Phase 1.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
