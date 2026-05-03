"""
Hoyle & Shephard (2018) empirical test on realized strategy PnL.
Computes whether vol scaling would improve Sharpe for a given return series.

Reference: Hoyle & Shephard 2018, SSRN 3279787.
Crypto context: Yuyama et al. 2023, SSRN 4548964.

Usage: python user_data/scripts/hs_empirical_test.py
"""

import csv
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


COLUMNS = [
    "strategy", "pair", "is_short", "close_profit", "close_profit_abs",
    "stake_amount", "open_date", "close_date", "exit_reason",
]


def load_trades(csv_path: str) -> pd.DataFrame:
    # Detect header: if first row starts with 'strategy', use it as header
    with open(csv_path) as f:
        first = f.readline().strip()
    has_header = first.startswith("strategy") or first.startswith('"strategy')
    if has_header:
        df = pd.read_csv(csv_path)
        df.columns = COLUMNS
    else:
        df = pd.read_csv(csv_path, names=COLUMNS, header=None)
    df["is_short"] = df["is_short"].astype(int).astype(bool)
    df["close_profit"] = df["close_profit"].astype(float)
    df["close_profit_abs"] = df["close_profit_abs"].astype(float)
    df["stake_amount"] = df["stake_amount"].astype(float)
    df["close_date"] = pd.to_datetime(df["close_date"])
    df["open_date"] = pd.to_datetime(df["open_date"])
    df["trade_return"] = df["close_profit"]
    return df


def ewma_vol(returns: np.ndarray, half_life: float) -> np.ndarray:
    """Compute EWMA volatility process with given half-life in data points.
    Per Hoyle & Shephard S4: EWMA with 12-day half-life as baseline.
    For per-trade returns, we use half-life in number of trades.
    """
    alpha = 1 - math.exp(math.log(0.5) / half_life)
    n = len(returns)
    var = np.zeros(n)
    if n == 0:
        return np.zeros(0)
    # Initialize with variance of first few observations
    init_window = min(int(half_life), n)
    var[0] = np.var(returns[:init_window]) if init_window > 1 else returns[0] ** 2
    if var[0] == 0:
        var[0] = 1e-10
    for t in range(1, n):
        var[t] = alpha * returns[t - 1] ** 2 + (1 - alpha) * var[t - 1]
    return np.sqrt(np.maximum(var, 1e-12))


def rolling_vol(returns: np.ndarray, window: int) -> np.ndarray:
    """Compute rolling standard deviation with given window."""
    s = pd.Series(returns)
    vol = s.rolling(window=window, min_periods=max(2, window // 2)).std()
    vol = vol.fillna(vol[vol > 0].iloc[0] if (vol > 0).any() else np.std(returns))
    return vol.values


def compute_hs_quantities(
    returns: np.ndarray,
    sigma_t: np.ndarray,
    unconditional_mu: float,
    conditional_mu: np.ndarray | None = None,
) -> dict:
    """
    Compute Hoyle & Shephard quantities.

    returns: per-trade returns (r_t)
    sigma_t: conditional vol at time t
    unconditional_mu: unconditional mean return (mu)
    conditional_mu: conditional mean return (mu_t). If None, uses unconditional mu for all t.
    """
    n = len(returns)
    sigma = np.std(returns)  # unconditional vol
    mu = unconditional_mu

    if conditional_mu is None:
        # Constant mu case (HS S3.3): mu_t = mu for all t
        mu_t = np.full(n, mu)
    else:
        mu_t = conditional_mu

    # Ratios
    sigma_ratio = sigma / sigma_t  # sigma / sigma_t per HS notation
    mu_ratio = mu_t / mu if mu != 0 else np.ones(n)

    # Key quantities
    xi_0 = np.mean(sigma_ratio)  # E[sigma/sigma_t] - convexity term
    xi_1 = np.cov(sigma_ratio, mu_ratio, ddof=0)[0, 1] if n > 1 else 0.0  # Cov term
    gamma_1 = xi_0 + xi_1
    gamma_2 = np.var(sigma_ratio * mu_ratio, ddof=0) if n > 1 else 0.0
    S = mu / sigma if sigma > 0 else 0.0  # buy-and-hold Sharpe

    # HS test: vol scaling improves Sharpe if gamma_1 >= sqrt(1 + S^2 * gamma_2)
    hs_threshold = math.sqrt(max(0, 1 + S**2 * gamma_2))
    hs_result = gamma_1 >= hs_threshold

    # S_sigma (vol-scaled Sharpe)
    # Per HS Theorem 1, S_sigma = gamma_1 * S / sqrt(1 + S^2 * gamma_2)
    if S**2 * gamma_2 < 1e12:  # numerical guard
        S_sigma = gamma_1 * S / math.sqrt(max(1e-12, 1 + S**2 * gamma_2))
    else:
        S_sigma = 0.0

    # Approximation: S_sigma_approx = S * gamma_1 (when gamma_2 is small)
    S_sigma_approx = S * gamma_1

    return {
        "n_trades": n,
        "mu": mu,
        "sigma": sigma,
        "S_buyhold": S,
        "xi_0": xi_0,
        "xi_1": xi_1,
        "gamma_1": gamma_1,
        "gamma_2": gamma_2,
        "hs_threshold": hs_threshold,
        "hs_passes": hs_result,
        "S_sigma": S_sigma,
        "S_sigma_approx": S_sigma_approx,
        "S_sigma_vs_S": S_sigma - S,
        "approx_error": S_sigma - S_sigma_approx,
    }


def analyze_series(name: str, returns: np.ndarray, trade_dates: pd.DatetimeIndex) -> dict:
    """Run full H&S analysis on a return series."""
    n = len(returns)
    if n < 10:
        return {"error": f"Only {n} trades — insufficient for H&S test", "n_trades": n}

    mu = np.mean(returns)
    sigma = np.std(returns)

    # EWMA vol with 12-day half-life (HS baseline)
    # For per-trade returns, we need to map days to trade count
    # If trades span D days, half-life in trades = 12 * (n / D)
    if len(trade_dates) >= 2:
        total_days = (trade_dates.max() - trade_dates.min()).days
        total_days = max(total_days, 1)
        trades_per_day = n / total_days
        hl_trades = max(5, int(12 * trades_per_day))
    else:
        hl_trades = 12

    sigma_ewma = ewma_vol(returns, hl_trades)

    # 30-day rolling std (robustness check)
    if len(trade_dates) >= 2:
        hl_trades_30 = max(5, int(30 * trades_per_day))
    else:
        hl_trades_30 = 30
    sigma_roll = rolling_vol(returns, hl_trades_30)

    results = {}

    # --- Constant mu case (simpler, per HS S3.3) ---
    r_const = compute_hs_quantities(returns, sigma_ewma, mu, None)
    results["constant_mu_ewma"] = r_const

    # --- Rolling conditional mu ---
    # Use rolling mean over EWMA half-life window
    mu_rolling = (
        pd.Series(returns)
        .rolling(window=max(3, hl_trades), min_periods=max(3, hl_trades))
        .mean()
    )
    mu_rolling = mu_rolling.fillna(mu).values
    r_rolling = compute_hs_quantities(returns, sigma_ewma, mu, mu_rolling)
    results["rolling_mu_ewma"] = r_rolling

    # --- Robustness: 30-day rolling vol with constant mu ---
    r_const_30 = compute_hs_quantities(returns, sigma_roll, mu, None)
    results["constant_mu_roll30"] = r_const_30

    # --- Robustness: 30-day rolling vol with rolling mu ---
    mu_rolling_30 = (
        pd.Series(returns)
        .rolling(window=max(3, hl_trades_30), min_periods=max(3, hl_trades_30))
        .mean()
    )
    mu_rolling_30 = mu_rolling_30.fillna(mu).values
    r_rolling_30 = compute_hs_quantities(returns, sigma_roll, mu, mu_rolling_30)
    results["rolling_mu_roll30"] = r_rolling_30

    return results


def print_result(label: str, r: dict):
    if "error" in r:
        print(f"  ** {label}: {r['error']}")
        return
    n = r["n_trades"]
    print(f"  --- {label} (n={n}) ---")
    print(f"  mu (mean trade return):     {r['mu']:.6f}")
    print(f"  sigma (unconditional std):  {r['sigma']:.6f}")
    print(f"  S (buy-and-hold Sharpe):    {r['S_buyhold']:.4f}")
    print(f"  xi_0 (convexity term):      {r['xi_0']:.4f}")
    print(f"  xi_1 (covariance term):     {r['xi_1']:.6f}")
    print(f"  gamma_1 = xi_0 + xi_1:      {r['gamma_1']:.4f}")
    print(f"  gamma_2:                    {r['gamma_2']:.6f}")
    print(f"  HS threshold:               {r['hs_threshold']:.4f}")
    print(f"  HS test (gamma_1 >= thld):  {r['hs_passes']}")
    print(f"  S_sigma (vol-scaled SR):    {r['S_sigma']:.4f}")
    print(f"  S_sigma_approx (S*gamma_1): {r['S_sigma_approx']:.4f}")
    print(f"  S_sigma - S:                {r['S_sigma_vs_S']:+.4f}")
    print(f"  Approx error:               {r['approx_error']:.6f}")
    print()


def main():
    base = Path(__file__).parent.parent  # user_data/

    # ---- LiqCascade ----
    lc_path = base / "temp_liqcascade_trades.csv"
    if lc_path.exists():
        df_lc = load_trades(str(lc_path))
        print(f"\n{'='*60}")
        print(f"LiqCascade: {len(df_lc)} closed trades")
        print(f"Strategies: {df_lc['strategy'].unique()}")
        print(f"Pairs: {df_lc['pair'].unique()}")
        print(f"Date range: {df_lc['close_date'].min()} to {df_lc['close_date'].max()}")
        print(f"{'='*60}")

        # V04+V05 combined (the ~752 trade Phase 3.5 dataset)
        returns_all = df_lc["trade_return"].values
        results_all = analyze_series("LiqCascade V04+V05 (all)", returns_all, df_lc["close_date"])
        for label, r in results_all.items():
            print_result(label, r)

        # Split by strategy
        for strat in sorted(df_lc["strategy"].unique()):
            df_s = df_lc[df_lc["strategy"] == strat]
            returns_s = df_s["trade_return"].values
            print(f"\n  >>> {strat}: {len(df_s)} trades")
            results_s = analyze_series(strat, returns_s, df_s["close_date"])
            for label, r in results_s.items():
                print_result(label, r)

        # Split by is_short
        for label, mask in [("LONGS", ~df_lc["is_short"]), ("SHORTS", df_lc["is_short"])]:
            df_dir = df_lc[mask]
            returns_dir = df_dir["trade_return"].values
            print(f"\n  >>> {label}: {len(df_dir)} trades")
            results_dir = analyze_series(label, returns_dir, df_dir["close_date"])
            for rlabel, r in results_dir.items():
                print_result(rlabel, r)
    else:
        print("LiqCascade trade file not found")

    # ---- OracleSurfer ----
    os_path = base / "temp_oraclesurfer_trades.csv"
    if os_path.exists():
        df_os = load_trades(str(os_path))
        print(f"\n{'='*60}")
        print(f"OracleSurfer: {len(df_os)} closed trades")
        print(f"Strategies: {df_os['strategy'].unique()}")
        print(f"Date range: {df_os['close_date'].min()} to {df_os['close_date'].max()}")
        print(f"{'='*60}")

        returns_os = df_os["trade_return"].values
        if len(returns_os) >= 10:
            results_os = analyze_series("OracleSurfer (combined)", returns_os, df_os["close_date"])
            for label, r in results_os.items():
                print_result(label, r)
        else:
            print(f"\n  ** OracleSurfer has only {len(returns_os)} closed trades — ")
            print(f"     far below the ~50-trade minimum for a clean read.")
            print(f"     Per-trade returns: {returns_os}")
            print(f"     Mean return: {np.mean(returns_os):.6f}")
            print(f"     Std return:  {np.std(returns_os):.6f}")
            print(f"     Sharpe:      {np.mean(returns_os)/np.std(returns_os):.4f}" if np.std(returns_os) > 0 else "")
            print()
            # Run anyway for completeness but flag heavily
            if len(returns_os) >= 5:
                results_os = analyze_series("OracleSurfer (thin)", returns_os, df_os["close_date"])
                for label, r in results_os.items():
                    print_result(label, r)

    print("\nDone.")


if __name__ == "__main__":
    main()
