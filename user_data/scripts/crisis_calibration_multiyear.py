"""
Multi-year CRISIS gate (ATR p90) calibration across 2022-2025.
Identifies when the gate would have fired and cross-references known crisis events.

Usage: python user_data/scripts/crisis_calibration_multiyear.py
"""

from pathlib import Path

import numpy as np
import pandas as pd


def load_daily_data(pair: str, data_dir: Path) -> pd.DataFrame:
    base = pair.split("/")[0]
    fname = f"{base}_USDT_USDT-1d-futures.feather"
    fpath = data_dir / fname
    df = pd.read_feather(fpath)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(span=period, min_periods=period).mean()


def compute_crisis_state(atr: pd.Series, lookback: int = 30) -> pd.Series:
    rolling_p90 = atr.rolling(window=lookback, min_periods=lookback).quantile(0.90)
    return atr > rolling_p90


# Known crypto crisis events for cross-reference
CRISIS_EVENTS = {
    "2020-03-12": "COVID crash",
    "2020-03-13": "COVID crash",
    "2021-05-19": "China mining ban",
    "2022-05-09": "LUNA/UST collapse",
    "2022-05-10": "LUNA/UST collapse",
    "2022-05-11": "LUNA/UST collapse",
    "2022-05-12": "LUNA/UST collapse",
    "2022-06-13": "3AC/Celsius insolvency",
    "2022-06-14": "3AC/Celsius insolvency",
    "2022-11-08": "FTX collapse",
    "2022-11-09": "FTX collapse",
    "2022-11-10": "FTX collapse",
    "2024-08-05": "Japan carry trade unwind",
    "2025-02-03": "Trump tariff shock",
    "2025-04-02": "Liberation Day tariffs",
}


def analyze_pair(pair: str, df: pd.DataFrame) -> dict:
    atr = compute_atr(df)
    crisis = compute_crisis_state(atr)

    n_total = len(crisis.dropna())
    n_crisis = crisis.sum()

    # Crisis days per year
    yearly = pd.DataFrame({"crisis": crisis, "atr": atr, "close": df["close"]}, index=df.index)
    yearly["year"] = yearly.index.year
    yearly_summary = yearly.groupby("year").agg(
        n_days=("crisis", "count"),
        crisis_days=("crisis", "sum"),
        crisis_pct=("crisis", "mean"),
    )

    # Cross-reference with known events
    events_hit = {}
    for date_str, label in CRISIS_EVENTS.items():
        event_date = pd.Timestamp(date_str)
        # Check if any pairing is in crisis on that date or within +/- 1 day
        if event_date in crisis.index:
            is_crisis = crisis.loc[event_date]
            if is_crisis:
                events_hit[date_str] = label

    # Days where crisis is True and price change is extreme
    crisis_days = yearly[crisis].copy()
    crisis_days["return"] = df["close"].pct_change()
    crisis_days["abs_return"] = crisis_days["return"].abs()

    return {
        "pair": pair,
        "n_total_days": n_total,
        "n_crisis_days": n_crisis,
        "crisis_rate": n_crisis / n_total * 100 if n_total > 0 else 0,
        "yearly": yearly_summary,
        "events_hit": events_hit,
        "avg_crisis_abs_return": crisis_days[crisis_days["crisis"]]["abs_return"].mean() if n_crisis > 0 else 0,
        "avg_normal_abs_return": crisis_days[~crisis_days["crisis"]]["abs_return"].mean() if n_total > n_crisis else 0,
        "crisis_dates_sample": crisis_days[crisis_days["crisis"]].head(20).index.strftime("%Y-%m-%d").tolist() if n_crisis > 0 else [],
    }


def main():
    base = Path(__file__).parent.parent  # user_data/
    data_dir = base / "data" / "binance" / "futures"

    PAIRS = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "XRP/USDT:USDT", "BNB/USDT:USDT"]

    print("=" * 70)
    print("CRISIS GATE (ATR p90) MULTI-YEAR CALIBRATION")
    print("=" * 70)

    all_results = {}
    for pair in PAIRS:
        try:
            df = load_daily_data(pair, data_dir)
            result = analyze_pair(pair, df)
            all_results[pair] = result

            print(f"\n{'---' * 16}")
            print(f"  {pair}: {result['n_total_days']} days with ATR data")
            print(f"  Crisis days: {result['n_crisis_days']} ({result['crisis_rate']:.1f}%)")
            print(f"  Avg abs return (crisis): {result['avg_crisis_abs_return']*100:.2f}%")
            print(f"  Avg abs return (normal): {result['avg_normal_abs_return']*100:.2f}%")

            print(f"\n  Crisis days per year:")
            for year, row in result["yearly"].iterrows():
                print(f"    {year}: {int(row['crisis_days']):3d} / {int(row['n_days']):4d} ({row['crisis_pct']*100:.1f}%)")

            if result["events_hit"]:
                print(f"\n  Known events detected ({len(result['events_hit'])}/{len(CRISIS_EVENTS)}):")
                for date_str, label in sorted(result["events_hit"].items()):
                    print(f"    {date_str}: {label} ✓")
            else:
                print(f"\n  Known events detected: 0/{len(CRISIS_EVENTS)}")

        except FileNotFoundError:
            print(f"  {pair}: SKIPPED (no data)")

    # Aggregate
    print(f"\n{'=' * 70}")
    print("AGGREGATE SUMMARY")
    print(f"{'=' * 70}")

    for pair, result in all_results.items():
        n_events = len(CRISIS_EVENTS)
        n_hit = len(result["events_hit"])
        print(f"\n  {pair}:")
        print(f"    Crisis rate: {result['crisis_rate']:.1f}% ({result['n_crisis_days']} days total)")
        print(f"    Events detected: {n_hit}/{n_events}")
        if n_hit > 0:
            for date_str, label in sorted(result["events_hit"].items()):
                print(f"      {date_str}: {label}")
        if n_hit < n_events:
            missed = set(CRISIS_EVENTS.keys()) - set(result["events_hit"].keys())
            if missed:
                print(f"    Missed events:")
                for m in sorted(missed):
                    print(f"      {m}: {CRISIS_EVENTS[m]}")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
