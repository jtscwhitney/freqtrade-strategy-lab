"""
CointPairs Phase 0 — Cointegration Validation Script (v4)

Changes from v3:
    - Sweeps TIMEFRAMES ["1h", "4h"] — tests strategy at its natural timescale.
      All windows (OLS, z-score) and time stops defined in calendar days/hours
      and converted to candles per timeframe.
    - MAX_HOLD increased: 1h → 168h (7d), 4h → 1440h (60d).
      At 4h with 60d hold, P(ETH/BTC reversion) ≈ 64% vs 5% at 1h/72h.
    - Pair universe expanded: adds BNB/ETH and BNB/BTC.
      Missing data files are skipped gracefully (download BNB separately if needed).
    - Go/no-go half-life check replaced with P(reversion within MAX_HOLD) > 20%.
      This is timeframe-agnostic and directly relevant to trading viability.
    - Cross-pair/cross-timeframe summary table at the end.

Download BNB data (optional):
    docker compose run --rm freqtrade download-data \\
        --config config/config_cointpairs_V01.json \\
        --pairs BNB/USDT:USDT --timerange 20220101-20251231 --timeframes 1h 4h

Usage:
    docker compose run --rm --entrypoint python freqtrade \\
        user_data/scripts/cointpairs_phase0_validation.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from statsmodels.tsa.stattools import adfuller, coint
    from statsmodels.tsa.vector_ar.vecm import coint_johansen
except ModuleNotFoundError:
    subprocess.run([sys.executable, "-m", "pip", "install", "statsmodels", "-q"], check=True)
    from statsmodels.tsa.stattools import adfuller, coint
    from statsmodels.tsa.vector_ar.vecm import coint_johansen

import numpy as np
import pandas as pd


# ── Config ────────────────────────────────────────────────────────────────────

DATA_DIR        = Path("/freqtrade/user_data/data/binance/futures")
TIMERANGE_START = "2022-01-01"
TIMERANGE_END   = "2025-12-31"
TRAIN_RATIO     = 0.67

# Timeframes to test. All window parameters are in days/hours and converted.
TIMEFRAMES = ["1h", "4h"]

# Windows defined in calendar days — converted to candles per timeframe
OLS_WINDOW_DAYS      = 30          # hedge ratio lookback
ZSCORE_WINDOW_DAYS   = [7, 14, 30] # z-score normalisation windows

# Time stop per timeframe (hours) — drives P(reversion) calculation
MAX_HOLD_HOURS = {
    "1h": 168,   # 7 days — longer than v3's 72h; still conservative
    "4h": 1440,  # 60 days — aligned with ~2× ETH/BTC half-life
}

# Fee economics
FEE_BPS_RT     = 10.0  # 5 bps/side retail round-trip
FEE_FLOOR_MULT = 3.0   # target mean_net > 30 bps
TIME_STOP_MAX  = 0.50  # require < 50% exits via time stop

ENTRY_THRESHOLDS = [1.5, 2.0, 2.5, 3.0]
EXIT_THRESHOLDS  = [0.0, 0.3, 0.5]

# Half-life go/no-go: require P(reversion within MAX_HOLD) > this
MIN_REVERSION_PROB = 0.20

# Pairs: (traded, anchor). Missing data files are skipped — no sys.exit.
PAIRS = [
    ("ETH/USDT:USDT", "BTC/USDT:USDT"),
    ("SOL/USDT:USDT", "ETH/USDT:USDT"),
    ("SOL/USDT:USDT", "BTC/USDT:USDT"),
    ("BNB/USDT:USDT", "ETH/USDT:USDT"),
    ("BNB/USDT:USDT", "BTC/USDT:USDT"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_close(symbol: str, timeframe: str) -> pd.Series | None:
    fname = f"{symbol.replace('/', '_').replace(':', '_')}-{timeframe}-futures.feather"
    path  = DATA_DIR / fname
    if not path.exists():
        return None
    df = pd.read_feather(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.set_index("date").sort_index()
    s = df.loc[TIMERANGE_START:TIMERANGE_END, "close"].rename(symbol)
    return s if len(s) > 500 else None


def rolling_beta(y: np.ndarray, x: np.ndarray, window: int) -> np.ndarray:
    n     = len(y)
    betas = np.full(n, np.nan)
    for i in range(window - 1, n):
        yw = y[i - window + 1 : i + 1]
        xw = x[i - window + 1 : i + 1]
        if np.any(np.isnan(yw)) or np.any(np.isnan(xw)):
            continue
        xd = xw - xw.mean()
        vx = np.dot(xd, xd)
        if vx < 1e-12:
            continue
        betas[i] = np.dot(xd, yw - yw.mean()) / vx
    return betas


def zscore(spread: np.ndarray, window: int) -> np.ndarray:
    s  = pd.Series(spread)
    mu = s.rolling(window).mean()
    sd = s.rolling(window).std().replace(0, np.nan)
    return ((s - mu) / sd).values


def hurst(ts: np.ndarray, max_lag: int = 100) -> float:
    ts   = ts[~np.isnan(ts)]
    lags = range(2, min(max_lag, len(ts) // 4))
    tau  = [np.sqrt(np.nanstd(ts[l:] - ts[:-l])) for l in lags]
    return np.polyfit(np.log(list(lags)), np.log(tau), 1)[0]


def ou_halflife_candles(spread: np.ndarray) -> float:
    """Half-life in candles (multiply by candle_hours to get hours)."""
    s  = pd.Series(spread).dropna()
    df = pd.concat([s.diff(), s.shift(1)], axis=1).dropna()
    df.columns = ["d", "l"]
    b = np.polyfit(df["l"].values, df["d"].values, 1)[0]
    return np.inf if b >= 0 else np.log(2) / (-b)


def fee_sweep(
    traded_price: pd.Series,
    z: np.ndarray,
    fee: float,
    max_hold_candles: int,
) -> pd.DataFrame:
    rows = []
    pv   = traded_price.values
    zv   = z.copy()
    n    = len(pv)

    for ez in ENTRY_THRESHOLDS:
        for xz in EXIT_THRESHOLDS:
            for d in ("long", "short"):
                trades, in_t = [], False
                ei = ep = None
                for i in range(1, n):
                    if np.isnan(zv[i]):
                        continue
                    if not in_t:
                        if   d == "long"  and zv[i] < -ez:
                            in_t, ei, ep = True, i, pv[i]
                        elif d == "short" and zv[i] >  ez:
                            in_t, ei, ep = True, i, pv[i]
                    else:
                        hold   = i - ei
                        z_exit = ((d == "long"  and zv[i] > -xz) or
                                  (d == "short" and zv[i] <  xz))
                        t_stop = hold >= max_hold_candles
                        if z_exit or t_stop:
                            r = ((pv[i] - ep) / ep if d == "long"
                                 else (ep - pv[i]) / ep) * 10000
                            trades.append({"net": r - fee, "h": hold, "ts": t_stop})
                            in_t = False
                if not trades:
                    continue
                df = pd.DataFrame(trades)
                rows.append({
                    "ez": ez, "xz": xz, "dir": d,
                    "n":        len(df),
                    "wr":       (df["net"] > 0).mean(),
                    "mean_net": df["net"].mean(),
                    "med_h":    df["h"].median(),
                    "ts_pct":   df["ts"].mean(),
                })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("mean_net", ascending=False)


def banner(title: str) -> None:
    print(f"\n  {'─'*60}")
    print(f"  {title}")
    print(f"  {'─'*60}")


# ── Per (pair, timeframe) analysis ────────────────────────────────────────────

def analyse(
    traded_sym: str,
    anchor_sym: str,
    traded:     pd.Series,
    anchor:     pd.Series,
    timeframe:  str,
    candle_h:   int,
) -> dict | None:

    label = (f"{traded_sym.split('/')[0]}/{anchor_sym.split('/')[0]}"
             f"@{timeframe}")
    n     = len(traded)
    split = int(n * TRAIN_RATIO)
    ols_w = OLS_WINDOW_DAYS * 24 // candle_h
    zs_ws = [max(10, d * 24 // candle_h) for d in ZSCORE_WINDOW_DAYS]
    max_h_c = MAX_HOLD_HOURS[timeframe] // candle_h   # in candles

    print(f"\n{'#'*65}")
    print(f"# {label}  |  {n:,} candles  "
          f"({traded.index[0].date()} – {traded.index[-1].date()})")
    print(f"# OLS={ols_w}c={OLS_WINDOW_DAYS}d  "
          f"ZSCORE_WINDOWS={zs_ws}c  MAX_HOLD={max_h_c}c={MAX_HOLD_HOURS[timeframe]}h")
    print('#'*65)

    tr_y = np.log(traded.iloc[:split].values.astype(float))
    tr_x = np.log(anchor.iloc[:split].values.astype(float))
    val_traded = traded.iloc[split:]

    # ADF
    banner("ADF on log prices (expect p > 0.05)")
    adf_pass = {}
    for nm, arr in [(traded_sym.split('/')[0], tr_y),
                    (anchor_sym.split('/')[0], tr_x)]:
        _, p, lags = adfuller(arr, autolag="AIC")[:3]
        adf_pass[nm] = p > 0.05
        print(f"  log({nm}): p={p:.4f}  lags={lags}  "
              f"→ {'PASS' if p > 0.05 else 'FAIL'}")

    # Static β
    xd     = tr_x - tr_x.mean()
    beta_s = np.dot(xd, tr_y - tr_y.mean()) / np.dot(xd, xd)
    print(f"\n  Static β_log = {beta_s:.4f}  (expect 0.4–2.0)")

    # EG
    banner("Engle-Granger (expect p < 0.05)")
    _, eg_p, _ = coint(tr_y, tr_x)
    eg_pass = eg_p < 0.05
    print(f"  EG p={eg_p:.4f}  → {'PASS' if eg_pass else 'FAIL'}")

    # Johansen
    banner("Johansen (expect reject r=0)")
    jres   = coint_johansen(np.column_stack([tr_y, tr_x]), det_order=0, k_ar_diff=1)
    trace  = jres.lr1;  cv95 = jres.cvt[:, 1]
    j_pass = trace[0] > cv95[0]
    print(f"  Trace r=0: {trace[0]:.4f}  (cv95: {cv95[0]:.4f})  "
          f"→ {'REJECT r=0 (PASS)' if j_pass else 'FAIL'}")

    # Hurst + half-life
    sp_train = tr_y - beta_s * tr_x
    H    = hurst(sp_train)
    hl_c = ou_halflife_candles(sp_train)          # in candles
    hl_h = hl_c * candle_h if not np.isinf(hl_c) else np.inf  # in hours
    p_rev = (0.0 if np.isinf(hl_h)
             else min(1.0, 1 - 0.5 ** (MAX_HOLD_HOURS[timeframe] / hl_h)))
    hl_pass = p_rev >= MIN_REVERSION_PROB
    print(f"\n  Hurst H={H:.4f}  "
          f"{'MEAN-REVERTING' if H < 0.5 else 'TRENDING/RANDOM'}")
    print(f"  Half-life = {hl_h:.0f}h ({hl_c:.0f}c)  "
          f"P(revert in {MAX_HOLD_HOURS[timeframe]}h) = {p_rev:.1%}  "
          f"→ {'PASS' if hl_pass else 'FAIL'} (min {MIN_REVERSION_PROB:.0%})")

    # Rolling β stability (val set)
    ly_full = np.log(traded.values.astype(float))
    lx_full = np.log(anchor.values.astype(float))
    rb      = rolling_beta(ly_full, lx_full, ols_w)
    vb      = rb[split:]
    beta_stable = np.nanstd(vb) < 0.30
    print(f"  Rolling β val: mean={np.nanmean(vb):.3f}  "
          f"std={np.nanstd(vb):.3f}  "
          f"min={np.nanmin(vb):.3f}  max={np.nanmax(vb):.3f}  "
          f"→ {'STABLE' if beta_stable else 'UNSTABLE'}")

    # Z-score sweeps
    lsp_full  = ly_full - rb * lx_full
    sweep_results = []

    for zw in zs_ws:
        days_label = zw * candle_h // 24
        z_full = zscore(lsp_full, zw)
        val_z  = z_full[split:]
        vz     = val_z[~np.isnan(val_z)]

        print(f"\n  ── ZSCORE_WINDOW={zw}c ({days_label}d) ──")
        print(f"  z dist: mean={np.nanmean(val_z):.3f}  std={np.nanstd(val_z):.3f}  "
              f"|z|>1.5:{(np.abs(vz)>1.5).mean()*100:.1f}%  "
              f"|z|>2.0:{(np.abs(vz)>2.0).mean()*100:.1f}%")

        sw = fee_sweep(val_traded, val_z, FEE_BPS_RT, max_h_c)
        if sw.empty:
            print("  No trades generated.")
            sweep_results.append({"zw_days": days_label, "status": "NO TRADES",
                                   "mean_net": np.nan, "ts_pct": np.nan, "n": 0})
            continue

        target   = FEE_BPS_RT * FEE_FLOOR_MULT
        good     = sw[(sw["mean_net"] > target) & (sw["ts_pct"] < TIME_STOP_MAX)]
        marginal = sw[sw["mean_net"] > target]

        pd.set_option("display.float_format", "{:.2f}".format)
        print(sw.head(6).to_string(index=False))

        if not good.empty:
            b = good.iloc[0]
            status = "PASS"
            print(f"  ✓ PASS ez={b['ez']} xz={b['xz']} {b['dir']}  "
                  f"net={b['mean_net']:.0f}bps  n={int(b['n'])}  "
                  f"wr={b['wr']:.0%}  ts={b['ts_pct']:.0%}")
        elif not marginal.empty:
            b = marginal.iloc[0]
            status = "MARGINAL"
            print(f"  ~ MARGINAL profitable but ts={b['ts_pct']:.0%} ≥ {TIME_STOP_MAX:.0%}")
        else:
            b = sw.iloc[0]
            status = "FAIL"
            print(f"  ✗ FAIL best={b['mean_net']:.0f}bps")

        sweep_results.append({
            "zw_days": days_label, "status": status,
            "mean_net": b["mean_net"], "ts_pct": b["ts_pct"],
            "n": int(b["n"]),
        })

    # Per-combo go/no-go
    banner(f"Go / No-Go — {label}")
    checks = {
        f"log({traded_sym.split('/')[0]}) non-stationary": list(adf_pass.values())[0],
        f"log({anchor_sym.split('/')[0]}) non-stationary": list(adf_pass.values())[1],
        "Engle-Granger (p<0.05)":                          eg_pass,
        "Johansen confirms cointegration":                  j_pass,
        "Hurst H < 0.5":                                   H < 0.5,
        f"P(revert in {MAX_HOLD_HOURS[timeframe]}h) ≥ {MIN_REVERSION_PROB:.0%}": hl_pass,
        "Rolling β stable (std < 0.30)":                   beta_stable,
        "Fee sweep PASS (net>30bps, ts<50%)":
            any(r["status"] == "PASS" for r in sweep_results),
    }
    passes = sum(checks.values())
    for crit, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {crit}")

    overall = "GO" if passes >= 6 else ("MARGINAL" if passes >= 4 else "NO GO")
    print(f"\n  {passes}/8  →  {overall}")

    return {
        "label":     label,
        "tf":        timeframe,
        "pair":      f"{traded_sym.split('/')[0]}/{anchor_sym.split('/')[0]}",
        "n":         n,
        "beta_s":    round(beta_s, 3),
        "beta_std":  round(np.nanstd(vb), 3),
        "eg_p":      round(eg_p, 4),
        "j":         "PASS" if j_pass else "FAIL",
        "H":         round(H, 3),
        "hl_h":      round(hl_h, 0) if not np.isinf(hl_h) else 9999,
        "p_rev":     round(p_rev, 2),
        "sweep":     next((r["status"] for r in sorted(
                        sweep_results,
                        key=lambda r: r.get("mean_net", -9999) or -9999,
                        reverse=True)), "N/A"),
        "passes":    passes,
        "overall":   overall,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("CointPairs Phase 0 — Multi-Pair / Multi-Timeframe Validation (v4)")
    print(f"Timeframes: {TIMEFRAMES}  |  Pairs: "
          f"{', '.join(f'{t.split(chr(47))[0]}/{a.split(chr(47))[0]}' for t,a in PAIRS)}")

    # Load all unique (symbol, timeframe) combos upfront
    symbols = {s for pair in PAIRS for s in pair}
    cache: dict[tuple, pd.Series | None] = {}
    for tf in TIMEFRAMES:
        candle_h = int(tf.replace("h", ""))
        for sym in sorted(symbols):
            key = (sym, tf)
            s = load_close(sym, tf)
            cache[key] = s
            if s is None:
                print(f"  [SKIP] {sym} @ {tf} — file not found "
                      f"(download and re-run to include)")
            else:
                print(f"  Loaded {sym} @ {tf}: {len(s):,} candles")

    all_results = []
    for tf in TIMEFRAMES:
        candle_h = int(tf.replace("h", ""))
        print(f"\n\n{'='*65}")
        print(f"  TIMEFRAME: {tf}  |  MAX_HOLD: {MAX_HOLD_HOURS[tf]}h")
        print('='*65)
        for traded_sym, anchor_sym in PAIRS:
            t = cache.get((traded_sym, tf))
            a = cache.get((anchor_sym, tf))
            if t is None or a is None:
                print(f"\n  [SKIP] {traded_sym.split('/')[0]}/"
                      f"{anchor_sym.split('/')[0]} @ {tf} — data missing")
                continue
            idx = t.index.intersection(a.index)
            if len(idx) < 1000:
                print(f"\n  [SKIP] {traded_sym}/{anchor_sym} @ {tf} — "
                      f"insufficient overlap ({len(idx)} candles)")
                continue
            result = analyse(traded_sym, anchor_sym,
                             t.loc[idx], a.loc[idx], tf, candle_h)
            if result:
                all_results.append(result)

    # Cross-pair / cross-timeframe summary
    print(f"\n\n{'='*65}")
    print("  FINAL SUMMARY")
    print('='*65)
    if not all_results:
        print("  No results — check data availability.")
        return

    df = pd.DataFrame(all_results)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 130)
    pd.set_option("display.float_format", "{:.3f}".format)
    cols = ["label", "eg_p", "j", "H", "hl_h", "p_rev",
            "beta_std", "sweep", "passes", "overall"]
    print(df[cols].to_string(index=False))

    passed = df[df["overall"] == "GO"]
    marginal = df[df["overall"] == "MARGINAL"]

    print()
    if not passed.empty:
        best = passed.sort_values("passes", ascending=False).iloc[0]
        print(f"  ✓ GO candidate: {best['label']}  ({best['passes']}/8)")
        print(f"    Recommend Phase 1 backtest with this pair/timeframe.")
    elif not marginal.empty:
        best = marginal.sort_values("passes", ascending=False).iloc[0]
        print(f"  ~ Best MARGINAL: {best['label']}  ({best['passes']}/8)")
        print(f"    Review diagnostics — potentially viable with parameter tuning.")
    else:
        print("  ✗ No GO or MARGINAL result across all pairs and timeframes.")
        print("  Consider: archive Candidate F, proceed to Candidate E (Path Signatures).")


if __name__ == "__main__":
    main()
