"""
Gate calibration: backtest CONFIRMED gates against realized LiqCascade PnL.
Computes what each gate would have blocked/allowed and the P&L differential.

Usage: python user_data/scripts/gate_calibration.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


# --- Load daily price data ---
def load_daily_data(pair: str, data_dir: Path) -> pd.DataFrame:
    """Load daily futures feather file for a pair."""
    # pair is like "BTC/USDT:USDT", map to "BTC_USDT_USDT-1d-futures.feather"
    base = pair.split("/")[0]
    fname = f"{base}_USDT_USDT-1d-futures.feather"
    fpath = data_dir / fname
    if not fpath.exists():
        raise FileNotFoundError(f"Missing data: {fpath}")
    df = pd.read_feather(fpath)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


def compute_ema200(df: pd.DataFrame) -> pd.Series:
    """Compute EMA200 of close prices."""
    return df["close"].ewm(span=200, min_periods=200).mean()


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Compute ATR(14) from daily data."""
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.ewm(span=period, min_periods=period).mean()
    return atr


def compute_crisis_state(atr: pd.Series, lookback: int = 30) -> pd.Series:
    """CRISIS gate: True when ATR > 90th percentile of rolling 30-day ATR."""
    rolling_p90 = atr.rolling(window=lookback, min_periods=lookback).quantile(0.90)
    return atr > rolling_p90


# --- Load trade data ---
COLUMNS = [
    "strategy", "pair", "is_short", "close_profit", "close_profit_abs",
    "stake_amount", "open_date", "close_date", "exit_reason",
]


def load_trades_from_csv(csv_path: Path) -> pd.DataFrame:
    """Load closed LiqCascade trades from SSH-extracted CSV (no header)."""
    df = pd.read_csv(csv_path, names=COLUMNS, header=None)
    df["open_date"] = pd.to_datetime(df["open_date"]).dt.tz_localize("UTC")
    df["close_date"] = pd.to_datetime(df["close_date"]).dt.tz_localize("UTC")
    df["is_short"] = df["is_short"].astype(int).astype(bool)
    df["close_profit"] = df["close_profit"].astype(float)
    df["close_profit_abs"] = df["close_profit_abs"].astype(float)
    df["stake_amount"] = df["stake_amount"].astype(float)
    df["id"] = range(len(df))
    return df




def tag_trades_with_gates(trades: pd.DataFrame, pair_data: dict) -> pd.DataFrame:
    """For each trade, tag whether each gate would have allowed or blocked it."""
    results = []

    for _, trade in trades.iterrows():
        pair = trade["pair"]
        open_dt = trade["open_date"]
        is_short = trade["is_short"]

        if pair not in pair_data:
            continue

        prices = pair_data[pair]

        # Find the most recent daily close before trade entry
        # The gate looks at daily data UP TO the trade's open date
        daily_before = prices[prices.index <= open_dt]
        if len(daily_before) == 0:
            continue

        last_daily = daily_before.iloc[-1]
        trade_date = daily_before.index[-1]

        # EMA200 gate
        ema200 = last_daily.get("ema200")
        close_price = last_daily["close"]
        if ema200 is not None and not np.isnan(ema200):
            if is_short:
                # Block shorts above EMA200
                ema200_block = close_price > ema200
                ema200_direction = "block_shorts_above"
            else:
                # Block longs below EMA200
                ema200_block = close_price < ema200
                ema200_direction = "block_longs_below"
        else:
            ema200_block = False
            ema200_direction = "insufficient_data"

        # CRISIS gate (ATR p90)
        crisis = last_daily.get("crisis")
        crisis_block = bool(crisis) if crisis is not None and not (isinstance(crisis, float) and np.isnan(crisis)) else False

        # Log the gate states
        results.append({
            "trade_id": trade["id"],
            "pair": pair,
            "is_short": is_short,
            "close_profit": trade["close_profit"],
            "close_profit_abs": trade["close_profit_abs"],
            "stake_amount": trade["stake_amount"],
            "open_date": open_dt,
            "close_date": trade["close_date"],
            "exit_reason": trade["exit_reason"],
            "strategy": trade["strategy"],
            "trade_date": trade_date,
            "close_price": close_price,
            "ema200": ema200,
            "ema200_block": ema200_block,
            "ema200_direction": ema200_direction,
            "crisis_block": crisis_block,
        })

    return pd.DataFrame(results)


def analyze_gate(tagged: pd.DataFrame, gate_col: str, label: str) -> dict:
    """Analyze what a gate blocked vs allowed."""
    blocked = tagged[tagged[gate_col]]
    allowed = tagged[~tagged[gate_col]]

    n_blocked = len(blocked)
    n_allowed = len(allowed)
    n_total = len(tagged)

    avg_profit_blocked = blocked["close_profit"].mean() if n_blocked > 0 else 0
    avg_profit_allowed = allowed["close_profit"].mean() if n_allowed > 0 else 0
    sum_profit_blocked = blocked["close_profit_abs"].sum() if n_blocked > 0 else 0
    sum_profit_allowed = allowed["close_profit_abs"].sum() if n_allowed > 0 else 0

    pct_blocked = n_blocked / n_total * 100 if n_total > 0 else 0

    # What fraction of blocked trades were actually losses?
    if n_blocked > 0:
        pct_blocked_losses = (blocked["close_profit"] < 0).mean() * 100
    else:
        pct_blocked_losses = 0

    return {
        "gate": label,
        "n_total": n_total,
        "n_blocked": n_blocked,
        "n_allowed": n_allowed,
        "pct_blocked": pct_blocked,
        "avg_profit_blocked": avg_profit_blocked,
        "avg_profit_allowed": avg_profit_allowed,
        "sum_profit_abs_blocked": sum_profit_blocked,
        "sum_profit_abs_allowed": sum_profit_allowed,
        "pct_blocked_losses": pct_blocked_losses,
        "avg_profit_delta": avg_profit_blocked - avg_profit_allowed,
    }


def main():
    base = Path(__file__).parent.parent  # user_data/
    data_dir = base / "data" / "binance" / "futures"

    # Re-extract from droplet if needed
    csv_path = base / "temp_liqcascade_trades.csv"
    if not csv_path.exists():
        print("Re-extracting trade data from LiqCascade droplet...")
        import subprocess
        result = subprocess.run([
            "ssh", "root@138.197.188.16",
            "cd /opt/freqtrade/freqtrade-scalper && sqlite3 -csv user_data/tradesv3.dryrun.sqlite 'SELECT strategy, pair, is_short, close_profit, close_profit_abs, stake_amount, open_date, close_date, exit_reason FROM trades WHERE is_open=0 ORDER BY close_date'"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            csv_path.write_text(result.stdout)
            print(f"  Extracted {result.stdout.count(chr(10))} lines")
        else:
            print(f"  SSH failed: {result.stderr}")
            return

    PAIRS = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "XRP/USDT:USDT", "BNB/USDT:USDT"]

    # Load and compute daily indicators
    print("Loading daily data and computing indicators...")
    pair_data = {}
    for pair in PAIRS:
        try:
            df = load_daily_data(pair, data_dir)
            df["ema200"] = compute_ema200(df)
            df["atr14"] = compute_atr(df)
            df["crisis"] = compute_crisis_state(df["atr14"])
            pair_data[pair] = df
            date_range = f"{df.index[0].date()} to {df.index[-1].date()}"
            n = len(df)
            print(f"  {pair}: {n} daily candles, {date_range}")
        except FileNotFoundError as e:
            print(f"  {pair}: SKIPPED ({e})")

    # Load trades
    print(f"\nLoading trades...")
    trades = load_trades_from_csv(csv_path)
    print(f"  {len(trades)} closed trades")
    print(f"  Strategies: {trades['strategy'].unique()}")
    print(f"  Pairs: {trades['pair'].unique()}")

    # Tag trades with gate conditions
    print("\nTagging trades with gate conditions...")
    tagged = tag_trades_with_gates(trades, pair_data)
    print(f"  {len(tagged)} trades tagged")

    # Analyze gates
    print("\n" + "=" * 70)
    print("GATE CALIBRATION RESULTS")
    print("=" * 70)

    # Overall
    print(f"\n{'Dataset':<30} {len(tagged)} trades")
    print(f"  Mean trade return: {tagged['close_profit'].mean():.6f}")
    print(f"  Total P&L (USDT):  {tagged['close_profit_abs'].sum():.2f}")
    print(f"  Win rate:          {(tagged['close_profit'] > 0).mean()*100:.1f}%")

    # --- EMA200 Gate ---
    ema200_tagged = tagged[tagged["ema200_block"] != "insufficient_data"]
    print(f"\n--- EMA200 Gate ({len(ema200_tagged)} trades with sufficient data) ---")
    ema200_result = analyze_gate(ema200_tagged, "ema200_block", "EMA200")
    _print_gate_result(ema200_result)

    # Split by direction
    for direction in ["block_longs_below", "block_shorts_above"]:
        subset = ema200_tagged[ema200_tagged["ema200_direction"] == direction]
        if len(subset) > 0:
            blocked = subset[subset["ema200_block"]]
            allowed = subset[~subset["ema200_block"]]
            print(f"\n  {direction}:")
            print(f"    Blocked: {len(blocked)} trades, avg P&L={blocked['close_profit'].mean():.6f}, { (blocked['close_profit']<0).mean()*100:.1f}% losing")
            print(f"    Allowed: {len(allowed)} trades, avg P&L={allowed['close_profit'].mean():.6f}, {(allowed['close_profit']<0).mean()*100:.1f}% losing")

    # --- CRISIS Gate ---
    print(f"\n--- CRISIS Gate (ATR p90, {len(tagged)} trades) ---")
    crisis_result = analyze_gate(tagged, "crisis_block", "CRISIS")
    _print_gate_result(crisis_result)

    # CRISIS by direction
    for label, mask in [("LONGS", ~tagged["is_short"]), ("SHORTS", tagged["is_short"])]:
        subset = tagged[mask]
        blocked = subset[subset["crisis_block"]]
        allowed = subset[~subset["crisis_block"]]
        print(f"\n  CRISIS {label}:")
        print(f"    Blocked: {len(blocked)} trades, avg P&L={blocked['close_profit'].mean():.6f}, {(blocked['close_profit']<0).mean()*100:.1f}% losing")
        print(f"    Allowed: {len(allowed)} trades, avg P&L={allowed['close_profit'].mean():.6f}, {(allowed['close_profit']<0).mean()*100:.1f}% losing")

    # --- Per-pair breakdown ---
    print(f"\n--- Per-Pair Gate Hit Rates ---")
    for pair in PAIRS:
        pt = tagged[tagged["pair"] == pair]
        if len(pt) == 0:
            continue
        ema20_pct = pt[pt["ema200_block"]].shape[0] / max(len(pt[pt["ema200_direction"] != "insufficient_data"]), 1) * 100
        crisis_pct = pt["crisis_block"].mean() * 100
        print(f"  {pair}: {len(pt):3d} trades, EMA200 hit={ema20_pct:.1f}%, CRISIS hit={crisis_pct:.1f}%")

    # --- Combined: both gates blocking ---
    print(f"\n--- Combined Blocking ---")
    tagged_valid = tagged[tagged["ema200_direction"] != "insufficient_data"]
    both_block = tagged_valid[tagged_valid["ema200_block"] & tagged_valid["crisis_block"]]
    either_block = tagged_valid[tagged_valid["ema200_block"] | tagged_valid["crisis_block"]]
    neither_block = tagged_valid[~(tagged_valid["ema200_block"] | tagged_valid["crisis_block"])]
    print(f"  Both gates block:  {len(both_block):3d} trades, avg P&L={both_block['close_profit'].mean():.6f}, sum P&L={both_block['close_profit_abs'].sum():.2f}")
    print(f"  Either gate blocks: {len(either_block):3d} trades, avg P&L={either_block['close_profit'].mean():.6f}, sum P&L={either_block['close_profit_abs'].sum():.2f}")
    print(f"  Neither blocks:     {len(neither_block):3d} trades, avg P&L={neither_block['close_profit'].mean():.6f}, sum P&L={neither_block['close_profit_abs'].sum():.2f}")

    # --- Save tagged dataset ---
    out_path = base / "results" / "gate_calibration_tagged_trades.csv"
    tagged.to_csv(out_path, index=False)
    print(f"\nTagged trades saved to {out_path}")

    print("\nDone.")


def _print_gate_result(r: dict):
    """Print formatted gate analysis result."""
    print(f"  Trades blocked:  {r['n_blocked']:4d} / {r['n_total']} ({r['pct_blocked']:.1f}%)")
    print(f"  Avg P&L blocked: {r['avg_profit_blocked']:.6f}  ({(1+r['avg_profit_blocked'])*100-100:.2f}% per trade)")
    print(f"  Avg P&L allowed: {r['avg_profit_allowed']:.6f}  ({(1+r['avg_profit_allowed'])*100-100:.2f}% per trade)")
    print(f"  P&L delta:       {r['avg_profit_delta']:+.6f}  (blocked vs allowed)")
    print(f"  Sum P&L blocked: {r['sum_profit_abs_blocked']:.2f} USDT")
    print(f"  Sum P&L allowed: {r['sum_profit_abs_allowed']:.2f} USDT")
    print(f"  % losing blocked:{r['pct_blocked_losses']:.1f}%")


if __name__ == "__main__":
    main()
