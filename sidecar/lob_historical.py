#!/usr/bin/env python3
"""
LOB Historical Data Downloader + Feature Preprocessor
======================================================
Downloads historical bookTicker + aggTrades data from Binance's public data
portal (data.binance.vision), resamples to 1-second LOB snapshots, computes
microstructure features using lob_features.py, and writes Parquet files in
the same schema as lob_collector.py.

This replaces the 14-day live collection wait — months of training data
available immediately.

Usage:
    python sidecar/lob_historical.py
    python sidecar/lob_historical.py --start 2024-06-01 --end 2025-03-01
    python sidecar/lob_historical.py --symbols BTCUSDT --start 2025-01-01

Output:
    sidecar/data/lob_raw/{SYMBOL}/{YYYY-MM-DD}/lob_{SYMBOL}_{date}_{time}.parquet
    (identical schema to lob_collector.py — fully interchangeable for training)

Download cache:
    sidecar/data/download_cache/  (raw ZIP files — safe to delete after processing)

Requirements:
    pip install requests pandas pyarrow numpy
"""

from __future__ import annotations

import argparse
import io
import logging
import sys
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

# ── Path setup ────────────────────────────────────────────────────────────────
# Allow running from project root or from sidecar/ directory
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

from lob_features import FEATURE_COLUMNS  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = _HERE.parent
DATA_DIR   = BASE_DIR / "sidecar" / "data" / "lob_raw"
CACHE_DIR  = BASE_DIR / "sidecar" / "data" / "download_cache"
LOG_PATH   = BASE_DIR / "sidecar" / "logs" / "lob_historical.log"

# ── Binance data portal ───────────────────────────────────────────────────────
_PORTAL = "https://data.binance.vision/data/futures/um/daily"

# ── CSV column definitions (no header row in Binance files) ──────────────────
_BOOK_TICKER_COLS = [
    "update_id", "best_bid_price", "best_bid_qty",
    "best_ask_price", "best_ask_qty", "transaction_time", "event_time",
]
_AGG_TRADES_COLS = [
    "agg_trade_id", "price", "qty", "first_trade_id",
    "last_trade_id", "transact_time", "is_buyer_maker",
]

# ── Parquet schema (must match lob_collector.py) ──────────────────────────────
_SCHEMA = pa.schema(
    [("timestamp_utc", pa.float64()), ("symbol", pa.string())]
    + [(col, pa.float64()) for col in FEATURE_COLUMNS]
)

# ── Trade window for rolling features ─────────────────────────────────────────
_MAX_WINDOW_S = 120   # seconds — longest OFI/VWAP window


# ── Logging ───────────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("lob_historical")


logger = _setup_logging()


# ── Download helpers ──────────────────────────────────────────────────────────

def _download_zip(url: str, cache_path: Path) -> Path | None:
    """
    Download a ZIP file to cache_path, skipping if already cached.
    Returns the cache path on success, None if the file doesn't exist (404)
    or on download error.
    """
    if cache_path.exists():
        logger.debug("Cache hit: %s", cache_path.name)
        return cache_path

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, timeout=120, stream=True)
        if resp.status_code == 404:
            logger.debug("Not found (404): %s", url)
            return None
        resp.raise_for_status()

        size_mb = int(resp.headers.get("content-length", 0)) / 1_048_576
        logger.info("Downloading %.1f MB: %s", size_mb, Path(url).name)

        with cache_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)

        return cache_path

    except requests.RequestException as exc:
        logger.warning("Download failed for %s: %s", Path(url).name, exc)
        cache_path.unlink(missing_ok=True)
        return None


def _open_zip_csv(zip_path: Path, col_names: list[str],
                  dtypes: dict | None = None) -> pd.DataFrame | None:
    """Extract the single CSV from a ZIP file and return as DataFrame."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as f:
                df = pd.read_csv(
                    io.TextIOWrapper(f, encoding="utf-8"),
                    names=col_names,
                    header=None,
                    dtype=dtypes,
                )
        return df
    except Exception as exc:
        logger.error("Failed to read %s: %s", zip_path.name, exc)
        return None


# ── Data loaders ──────────────────────────────────────────────────────────────

def load_book_ticker(symbol: str, day: date) -> pd.DataFrame | None:
    """
    Download (or load from cache) and parse the daily bookTicker CSV.
    Returns a DataFrame with columns: ts_s, mid, spread_rel,
    bid_qty_l1, ask_qty_l1, vol_imbalance_l1 — resampled to 1-second.
    """
    date_str = day.strftime("%Y-%m-%d")
    filename = f"{symbol}-bookTicker-{date_str}.zip"
    url      = f"{_PORTAL}/bookTicker/{symbol}/{filename}"
    cache    = CACHE_DIR / "bookTicker" / symbol / filename
    zip_path = _download_zip(url, cache)
    if zip_path is None:
        return None

    df = _open_zip_csv(zip_path, _BOOK_TICKER_COLS, dtypes={
        "update_id":        "int64",
        "best_bid_price":   "float64",
        "best_bid_qty":     "float64",
        "best_ask_price":   "float64",
        "best_ask_qty":     "float64",
        "transaction_time": "int64",
        "event_time":       "int64",
    })
    if df is None or df.empty:
        return None

    # Sort to handle the known out-of-order issue in 2024+ files
    df = df.sort_values(["event_time", "update_id"], ignore_index=True)

    # Drop crossed-book rows (data errors)
    valid = (df["best_bid_price"] > 0) & (df["best_ask_price"] > df["best_bid_price"])
    df = df[valid]
    if df.empty:
        return None

    # Derive features from top-of-book
    df["mid"]            = (df["best_bid_price"] + df["best_ask_price"]) / 2.0
    df["spread_rel"]     = (df["best_ask_price"] - df["best_bid_price"]) / df["mid"]
    denom                = df["best_bid_qty"] + df["best_ask_qty"]
    df["vol_imbalance_l1"] = np.where(
        denom > 0,
        (df["best_bid_qty"] - df["best_ask_qty"]) / denom,
        0.0,
    )

    # Convert ms → integer seconds, then keep LAST update per second
    df["ts_s"] = df["transaction_time"] // 1000
    df = (
        df.groupby("ts_s", sort=True)
          .last()
          .reset_index()
    )

    return df[["ts_s", "mid", "spread_rel",
               "best_bid_qty", "best_ask_qty", "vol_imbalance_l1"]].rename(
        columns={"best_bid_qty": "bid_qty_l1", "best_ask_qty": "ask_qty_l1"}
    )


def load_agg_trades(symbol: str, day: date) -> pd.DataFrame | None:
    """
    Download (or load from cache) and parse the daily aggTrades CSV.
    Returns a DataFrame with columns: ts_s, buy_usd, sell_usd,
    buy_price_x_usd, sell_price_x_usd — aggregated to 1-second.
    """
    date_str = day.strftime("%Y-%m-%d")
    filename = f"{symbol}-aggTrades-{date_str}.zip"
    url      = f"{_PORTAL}/aggTrades/{symbol}/{filename}"
    cache    = CACHE_DIR / "aggTrades" / symbol / filename
    zip_path = _download_zip(url, cache)
    if zip_path is None:
        return None

    df = _open_zip_csv(zip_path, _AGG_TRADES_COLS, dtypes={
        "agg_trade_id":    "int64",
        "price":           "float64",
        "qty":             "float64",
        "first_trade_id":  "int64",
        "last_trade_id":   "int64",
        "transact_time":   "int64",
        "is_buyer_maker":  "bool",
    })
    if df is None or df.empty:
        return None

    # Binance: is_buyer_maker=True → buyer is maker → taker is SELLER
    #          is_buyer_maker=False → buyer is taker → BUY aggression
    df["usd"]              = df["price"] * df["qty"]
    is_buy                 = ~df["is_buyer_maker"]
    df["buy_usd"]          = np.where(is_buy, df["usd"], 0.0)
    df["sell_usd"]         = np.where(~is_buy, df["usd"], 0.0)
    df["buy_price_x_usd"]  = np.where(is_buy,  df["price"] * df["usd"], 0.0)
    df["sell_price_x_usd"] = np.where(~is_buy, df["price"] * df["usd"], 0.0)
    df["ts_s"]             = df["transact_time"] // 1000

    trades_1s = (
        df.groupby("ts_s", sort=True)
          .agg(
              buy_usd=("buy_usd", "sum"),
              sell_usd=("sell_usd", "sum"),
              buy_price_x_usd=("buy_price_x_usd", "sum"),
              sell_price_x_usd=("sell_price_x_usd", "sum"),
          )
          .reset_index()
    )
    return trades_1s


# ── Feature computation (vectorized) ─────────────────────────────────────────

def compute_features_vectorized(
    book_1s:    pd.DataFrame,
    trades_1s:  pd.DataFrame,
    symbol:     str,
    prev_buf:   pd.DataFrame,   # last _MAX_WINDOW_S rows of previous day's trades_1s
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute all LOB features using vectorized pandas rolling operations.

    Prepends prev_buf (previous day's tail) to handle window boundary
    accuracy, then drops those rows from the output.

    Returns:
        (features_df, next_prev_buf) where next_prev_buf is the last
        _MAX_WINDOW_S rows of today's trades (carry-over for next day).
    """
    # Full 1-second time index for the day (00:00:00 – 23:59:59 UTC)
    day_start = int(book_1s["ts_s"].min())
    day_end   = int(book_1s["ts_s"].max())
    full_idx  = pd.RangeIndex(day_start, day_end + 1, name="ts_s")

    # Book: reindex to fill every second, forward-fill gaps (book state persists)
    book = (
        book_1s.set_index("ts_s")
               .reindex(full_idx)
               .ffill()
               .bfill()          # handle leading gap if first second has no update
    )

    # Trades: reindex to fill every second with zero (no trades = no flow)
    trade_cols = ["buy_usd", "sell_usd", "buy_price_x_usd", "sell_price_x_usd"]
    trades = (
        trades_1s.set_index("ts_s")[trade_cols]
                 .reindex(full_idx)
                 .fillna(0.0)
    )

    # Prepend previous day's tail for window warm-up
    if not prev_buf.empty:
        trades_combined = pd.concat([prev_buf, trades])
    else:
        trades_combined = trades

    n_prefix = len(prev_buf)

    # Compute rolling features for each window
    rows: dict[str, pd.Series] = {}
    for w in (5, 30, 120):
        buy_usd_w  = trades_combined["buy_usd"].rolling(w, min_periods=0).sum()
        sell_usd_w = trades_combined["sell_usd"].rolling(w, min_periods=0).sum()
        buy_px_usd = trades_combined["buy_price_x_usd"].rolling(w, min_periods=0).sum()
        sel_px_usd = trades_combined["sell_price_x_usd"].rolling(w, min_periods=0).sum()

        ofi = buy_usd_w - sell_usd_w

        # VWAP deviations — require current mid aligned with trades_combined index
        # The prefix rows have their own timestamps; current-day rows align with book
        mid_aligned = trades_combined.index.to_series().map(
            lambda ts: book.at[ts, "mid"] if ts in book.index else np.nan
        )
        mid_aligned = mid_aligned.ffill().bfill()

        buy_vwap     = buy_px_usd / buy_usd_w.replace(0, np.nan)
        buy_vwap_dev = ((buy_vwap - mid_aligned) / mid_aligned).fillna(0.0)

        sell_vwap     = sel_px_usd / sell_usd_w.replace(0, np.nan)
        sell_vwap_dev = ((sell_vwap - mid_aligned) / mid_aligned).fillna(0.0)

        # Slice off the prefix rows
        rows[f"ofi_{w}s"]           = ofi.iloc[n_prefix:]
        rows[f"buy_vwap_dev_{w}s"]  = buy_vwap_dev.iloc[n_prefix:]
        rows[f"sell_vwap_dev_{w}s"] = sell_vwap_dev.iloc[n_prefix:]

    # Build output DataFrame aligned to the book index
    out = book.copy()
    out["timestamp_utc"] = out.index.to_series().astype("float64")
    out["symbol"]        = symbol
    for col, series in rows.items():
        out[col] = series.values   # both aligned to full_idx after slicing

    out = out[["timestamp_utc", "symbol"] + FEATURE_COLUMNS].dropna(
        subset=["mid"]   # drop rows where book never populated
    )

    # Carry-over buffer for next day: last _MAX_WINDOW_S rows of today's trades
    next_prev = trades.tail(_MAX_WINDOW_S)

    return out, next_prev


# ── Parquet writer ────────────────────────────────────────────────────────────

def write_output(df: pd.DataFrame, symbol: str, day: date) -> None:
    """Write feature DataFrame to a Snappy-compressed Parquet file."""
    if df.empty:
        logger.warning("%s %s: empty feature DataFrame — skipping write.", symbol, day)
        return

    date_str = day.strftime("%Y-%m-%d")
    time_str = "0000"
    out_dir  = DATA_DIR / symbol / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"lob_{symbol}_{date_str.replace('-', '')}_{time_str}.parquet"

    arrays = {
        col: df[col].to_numpy()
        for col in ["timestamp_utc", "symbol"] + FEATURE_COLUMNS
    }
    table = pa.table(arrays, schema=_SCHEMA)
    pq.write_table(table, out_path, compression="snappy")
    logger.info("%s %s: wrote %d rows → %s", symbol, date_str, len(df), out_path.name)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def process_symbol(symbol: str, start: date, end: date) -> None:
    """Download, process, and write features for all days in [start, end]."""
    logger.info("Processing %s: %s → %s", symbol, start, end)

    day_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    prev_buf  = pd.DataFrame()   # carry-over from previous day

    days_written = 0
    days_skipped = 0

    for day in day_range:
        date_str = day.strftime("%Y-%m-%d")

        # Check if output already exists — skip to avoid re-processing
        out_path = DATA_DIR / symbol / date_str / f"lob_{symbol}_{date_str.replace('-', '')}_0000.parquet"
        if out_path.exists():
            logger.info("%s %s: output exists — skipping (delete to reprocess).", symbol, date_str)
            # Still need to load trades for the carry-over buffer
            trades = load_agg_trades(symbol, day)
            if trades is not None and not trades.empty:
                prev_buf = trades.set_index("ts_s")[
                    ["buy_usd", "sell_usd", "buy_price_x_usd", "sell_price_x_usd"]
                ].tail(_MAX_WINDOW_S)
            days_skipped += 1
            continue

        book   = load_book_ticker(symbol, day)
        trades = load_agg_trades(symbol, day)

        if book is None or book.empty:
            logger.warning("%s %s: bookTicker unavailable — skipping.", symbol, date_str)
            days_skipped += 1
            prev_buf = pd.DataFrame()   # reset buffer — gap in data
            continue

        if trades is None or trades.empty:
            logger.warning("%s %s: aggTrades unavailable — skipping.", symbol, date_str)
            days_skipped += 1
            prev_buf = pd.DataFrame()
            continue

        try:
            features, prev_buf = compute_features_vectorized(
                book, trades, symbol, prev_buf
            )
            write_output(features, symbol, day)
            days_written += 1
        except Exception as exc:
            logger.error("%s %s: feature computation failed: %s", symbol, date_str, exc)
            days_skipped += 1
            prev_buf = pd.DataFrame()

    logger.info(
        "%s complete: %d days written, %d skipped.",
        symbol, days_written, days_skipped,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and preprocess Binance historical LOB data."
    )
    parser.add_argument(
        "--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT"],
        help="Binance symbols to process (default: BTCUSDT ETHUSDT)",
    )
    parser.add_argument(
        "--start",
        default=(date.today() - timedelta(days=30)).isoformat(),
        help="Start date YYYY-MM-DD (default: 30 days ago)",
    )
    parser.add_argument(
        "--end",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="End date YYYY-MM-DD inclusive (default: yesterday)",
    )
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end   = date.fromisoformat(args.end)

    if end >= date.today():
        parser.error("--end must be before today (historical data only)")
    if start > end:
        parser.error("--start must be before --end")

    days = (end - start).days + 1
    logger.info("LOB historical preprocessor starting.")
    logger.info("Symbols : %s", args.symbols)
    logger.info("Range   : %s → %s (%d days)", start, end, days)
    logger.info("Output  : %s", DATA_DIR)
    logger.info("Cache   : %s", CACHE_DIR)

    # Estimate download size (rough: bookTicker ~200MB/day, aggTrades ~60MB/day compressed)
    est_gb = days * len(args.symbols) * 0.26
    logger.info("Estimated download: ~%.1f GB compressed (varies significantly)", est_gb)

    for symbol in args.symbols:
        process_symbol(symbol, start, end)

    logger.info("All symbols complete.")


if __name__ == "__main__":
    main()
