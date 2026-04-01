"""
Load Freqtrade backtest-export JSON trades and plot PnL by period + cumulative series.

Default input: unpacked BNB/SOL 4h analysis export.

Usage (host Python with pandas + matplotlib):
  python user_data/scripts/analyze_backtest_export_trades.py

Or:
  python user_data/scripts/analyze_backtest_export_trades.py --json path/to/backtest-result-*.json --out-dir path/to/charts
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def load_trades(json_path: Path) -> tuple[pd.DataFrame, str]:
    with open(json_path, encoding="utf-8") as f:
        root = json.load(f)
    strat_key = next(iter(root["strategy"].keys()))
    trades = root["strategy"][strat_key]["trades"]
    df = pd.DataFrame(trades)
    if df.empty:
        return df, strat_key
    df["close_dt"] = pd.to_datetime(df["close_date"], utc=True)
    df["year"] = df["close_dt"].dt.year
    df["month"] = df["close_dt"].dt.strftime("%Y-%m")
    return df.sort_values("close_dt"), strat_key


def main() -> None:
    repo = Path(__file__).resolve().parents[2]  # user_data/scripts -> parents[2] = repo root
    default_json = (
        repo
        / "user_data/results/cointpairs_bnb_sol_4h_analysis/backtest-result-2026-04-01_11-49-21_unpacked"
        / "backtest-result-2026-04-01_11-49-21.json"
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=default_json, help="Backtest export JSON")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for PNGs (default: <json-dir>/charts)",
    )
    args = ap.parse_args()
    json_path: Path = args.json
    out_dir: Path = args.out_dir or (json_path.parent / "charts")
    out_dir.mkdir(parents=True, exist_ok=True)

    df, strat = load_trades(json_path)
    if df.empty:
        print("No trades in export.")
        return

    starting = 10_000.0  # from this backtest; override if needed
    df["cum_pnl"] = df["profit_abs"].cumsum()
    df["equity"] = starting + df["cum_pnl"]

    # --- Yearly PnL (USDT) ---
    yearly = df.groupby("year", as_index=False)["profit_abs"].sum()
    yearly_by_pair = (
        df.groupby(["year", "pair"], as_index=False)["profit_abs"]
        .sum()
        .pivot(index="year", columns="pair", values="profit_abs")
        .fillna(0)
    )

    fig_y, ax_y = plt.subplots(figsize=(10, 5))
    years = yearly["year"].astype(str)
    ax_y.bar(years, yearly["profit_abs"], color="#2d6a4f", edgecolor="#1b4332", linewidth=0.8)
    ax_y.axhline(0, color="#333", linewidth=0.8)
    ax_y.set_ylabel("Realized PnL (USDT)")
    ax_y.set_xlabel("Year (by close_date)")
    ax_y.set_title(f"Backtest leg-trades: PnL by year — {strat}")
    for i, row in yearly.iterrows():
        ax_y.text(
            i,
            row["profit_abs"] + (200 if row["profit_abs"] >= 0 else -400),
            f"{row['profit_abs']:,.0f}",
            ha="center",
            va="bottom" if row["profit_abs"] >= 0 else "top",
            fontsize=9,
        )
    fig_y.tight_layout()
    p_yearly = out_dir / "pnl_by_year.png"
    fig_y.savefig(p_yearly, dpi=150)
    plt.close(fig_y)

    # --- Stacked / grouped by pair per year ---
    fig_p, ax_p = plt.subplots(figsize=(10, 5))
    pair_cols = [c for c in yearly_by_pair.columns]
    x = range(len(yearly_by_pair.index))
    width = 0.42
    if len(pair_cols) >= 2:
        b0 = ax_p.bar(
            [i - width / 2 for i in x],
            yearly_by_pair[pair_cols[0]],
            width,
            label=pair_cols[0],
            color="#1d3557",
        )
        b1 = ax_p.bar(
            [i + width / 2 for i in x],
            yearly_by_pair[pair_cols[1]],
            width,
            label=pair_cols[1],
            color="#e63946",
        )
        ax_p.legend()
    else:
        ax_p.bar(list(x), yearly_by_pair.iloc[:, 0], color="#457b9d", label=pair_cols[0])
        ax_p.legend()
    ax_p.set_xticks(list(x))
    ax_p.set_xticklabels([str(y) for y in yearly_by_pair.index])
    ax_p.axhline(0, color="#333", linewidth=0.8)
    ax_p.set_ylabel("USDT")
    ax_p.set_xlabel("Year")
    ax_p.set_title(f"PnL by year and leg (pair) — {strat}")
    fig_p.tight_layout()
    p_pair = out_dir / "pnl_by_year_by_pair.png"
    fig_p.savefig(p_pair, dpi=150)
    plt.close(fig_p)

    # --- Cumulative PnL time series ---
    fig_c, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax1.plot(df["close_dt"], df["cum_pnl"], color="#1d3557", linewidth=1.2, label="Cumulative realized PnL (USDT)")
    ax1.fill_between(df["close_dt"], 0, df["cum_pnl"], alpha=0.12, color="#1d3557")
    ax1.axhline(0, color="#999", linewidth=0.7)
    ax1.set_ylabel("Cumulative PnL (USDT)")
    ax1.set_title(f"Cumulative realized PnL (sorted by close) — {strat}")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.25)

    for pair, sub in df.groupby("pair"):
        ax2.plot(sub["close_dt"], sub["profit_abs"].cumsum(), linewidth=1.0, label=pair)
    ax2.axhline(0, color="#999", linewidth=0.7)
    ax2.set_ylabel("Cum. PnL by pair")
    ax2.set_xlabel("Trade close time (UTC)")
    ax2.legend(loc="upper left", fontsize=8)
    ax2.grid(True, alpha=0.25)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig_c.autofmt_xdate()

    fig_c.tight_layout()
    p_cum = out_dir / "cumulative_pnl_timeseries.png"
    fig_c.savefig(p_cum, dpi=150)
    plt.close(fig_c)

    # --- Monthly PnL (extra time resolution) ---
    monthly = df.groupby("month", as_index=False)["profit_abs"].sum()
    fig_m, ax_m = plt.subplots(figsize=(12, 4))
    ax_m.bar(range(len(monthly)), monthly["profit_abs"], color="#457b9d", edgecolor="#1d3557", linewidth=0.5)
    ax_m.axhline(0, color="#333", linewidth=0.8)
    ax_m.set_xticks(range(len(monthly)))
    ax_m.set_xticklabels(monthly["month"], rotation=45, ha="right", fontsize=7)
    ax_m.set_ylabel("USDT")
    ax_m.set_title(f"Monthly realized PnL (leg-trades) — {strat}")
    fig_m.tight_layout()
    p_m = out_dir / "pnl_by_month.png"
    fig_m.savefig(p_m, dpi=150)
    plt.close(fig_m)

    # Console tables
    print(f"Strategy: {strat}")
    print(f"Trades: {len(df)}")
    print("\n--- PnL by year (USDT) ---")
    print(yearly.to_string(index=False))
    print("\n--- PnL by year × pair ---")
    print(yearly_by_pair.to_string())
    print(f"\nCharts written to: {out_dir.resolve()}")
    print(f"  {p_yearly.name}")
    print(f"  {p_pair.name}")
    print(f"  {p_cum.name}")
    print(f"  {p_m.name}")


if __name__ == "__main__":
    main()
