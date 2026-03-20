#!/usr/bin/env python3
"""
LOB Data Collector — Phase 0 Sidecar
======================================
Streams Binance Futures WebSocket (bookTicker + aggTrade), computes LOB
microstructure features every second, and writes compressed Parquet files
for offline model training (Phase 1).

Streams used (combined WebSocket connection):
    <symbol>@bookTicker  — L1 bid/ask price and qty, event-driven
    <symbol>@aggTrade    — aggregated trades (price, qty, direction)

Output:
    sidecar/data/lob_raw/{SYMBOL}/{YYYY-MM-DD}/lob_{SYMBOL}_{YYYYMMDD}_{HHMM}.parquet
    (~15–20 MB/day/symbol compressed; 2 weeks ≈ 200–300 MB total)

Log:
    sidecar/logs/lob_collector.log

Requirements:
    pip install websockets pyarrow numpy
"""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import websockets

from lob_features import (
    FEATURE_COLUMNS,
    BookState,
    TradeRecord,
    compute_features,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "sidecar" / "data" / "lob_raw"
LOG_PATH = BASE_DIR / "sidecar" / "logs" / "lob_collector.log"

# ── Parameters ────────────────────────────────────────────────────────────────
SNAPSHOT_INTERVAL  = 1.0     # seconds between feature snapshots
ROWS_PER_FILE      = 3_600   # rows per Parquet file (~1 hour at 1s cadence)
TRADE_BUFFER_SECS  = 125     # keep trades this recent (> 120s max window + margin)
HEALTH_LOG_SECS    = 300     # log message-rate health every N seconds

# ── Symbols ───────────────────────────────────────────────────────────────────
# Key: Binance symbol, Value: Freqtrade pair string (for signal file in Phase 2)
SYMBOLS: dict[str, str] = {
    "BTCUSDT": "BTC/USDT:USDT",
    "ETHUSDT": "ETH/USDT:USDT",
}

# ── WebSocket ─────────────────────────────────────────────────────────────────
_streams = "/".join(
    f"{sym.lower()}@bookTicker/{sym.lower()}@aggTrade"
    for sym in SYMBOLS
)
WS_URI              = f"wss://fstream.binance.com/stream?streams={_streams}"
RECONNECT_DELAY_MIN = 1
RECONNECT_DELAY_MAX = 60

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("lob_collector")

# ── Parquet schema ────────────────────────────────────────────────────────────
_SCHEMA = pa.schema(
    [("timestamp_utc", pa.float64()), ("symbol", pa.string())]
    + [(col, pa.float64()) for col in FEATURE_COLUMNS]
)

# ── Per-symbol state ──────────────────────────────────────────────────────────
_book:        dict[str, BookState | None]   = {s: None      for s in SYMBOLS}
_trades:      dict[str, deque[TradeRecord]] = {s: deque()   for s in SYMBOLS}
_rows:        dict[str, list[dict]]         = {s: []        for s in SYMBOLS}
_last_msg_ts: dict[str, float]              = {s: 0.0       for s in SYMBOLS}
_shutdown = False


# ── Parquet I/O ───────────────────────────────────────────────────────────────

def _flush_to_parquet(symbol: str, rows: list[dict]) -> None:
    """Write buffered rows to a Snappy-compressed Parquet file."""
    if not rows:
        return
    first_ts  = datetime.fromtimestamp(rows[0]["timestamp_utc"], tz=timezone.utc)
    date_str  = first_ts.strftime("%Y-%m-%d")
    time_str  = first_ts.strftime("%H%M")
    out_dir   = DATA_DIR / symbol / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path  = out_dir / f"lob_{symbol}_{date_str.replace('-', '')}_{time_str}.parquet"

    arrays = {
        col: [r.get(col) for r in rows]
        for col in ["timestamp_utc", "symbol"] + FEATURE_COLUMNS
    }
    table = pa.table(arrays, schema=_SCHEMA)
    pq.write_table(table, out_path, compression="snappy")
    logger.info("Flushed %d rows → %s", len(rows), out_path)


# ── Trade buffer maintenance ──────────────────────────────────────────────────

def _prune_trades(symbol: str, now_ts: float) -> None:
    """Drop trades older than TRADE_BUFFER_SECS from the deque."""
    dq     = _trades[symbol]
    cutoff = now_ts - TRADE_BUFFER_SECS
    while dq and dq[0].ts < cutoff:
        dq.popleft()


# ── Message handlers ──────────────────────────────────────────────────────────

def _handle_book_ticker(symbol: str, data: dict) -> None:
    """Update L1 book state from a bookTicker message."""
    _book[symbol] = BookState(
        bid_price = float(data["b"]),
        bid_qty   = float(data["B"]),
        ask_price = float(data["a"]),
        ask_qty   = float(data["A"]),
        ts        = data.get("T", data.get("E", 0)) / 1_000.0,
    )
    _last_msg_ts[symbol] = _book[symbol].ts


def _handle_agg_trade(symbol: str, data: dict) -> None:
    """Append a trade record to the per-symbol buffer."""
    price  = float(data["p"])
    qty    = float(data["q"])
    ts_s   = data["T"] / 1_000.0   # Binance timestamps are in milliseconds
    # Binance aggTrade: m=True  → buyer is the market maker → taker is SELLER → is_buy=False
    #                  m=False → buyer is the market taker → is_buy=True
    is_buy = not data["m"]
    _trades[symbol].append(
        TradeRecord(ts=ts_s, price=price, qty=qty, usd=price * qty, is_buy=is_buy)
    )
    _last_msg_ts[symbol] = ts_s


# ── WebSocket receive loop ────────────────────────────────────────────────────

async def stream_market_data() -> None:
    """Connect to Binance combined stream; dispatch to handlers. Reconnects on error."""
    delay = RECONNECT_DELAY_MIN

    while not _shutdown:
        try:
            logger.info("Connecting to %s", WS_URI)
            async with websockets.connect(WS_URI, ping_interval=None) as ws:
                delay = RECONNECT_DELAY_MIN
                logger.info("Connected. Receiving %s streams.", len(SYMBOLS) * 2)

                async for raw in ws:
                    if _shutdown:
                        break

                    msg    = json.loads(raw)
                    stream = msg.get("stream", "")
                    data   = msg.get("data", {})
                    symbol = stream.split("@")[0].upper()

                    if symbol not in SYMBOLS:
                        continue

                    if "@bookTicker" in stream:
                        _handle_book_ticker(symbol, data)
                    elif "@aggTrade" in stream:
                        _handle_agg_trade(symbol, data)

        except (
            websockets.exceptions.ConnectionClosed,
            websockets.exceptions.WebSocketException,
            OSError,
        ) as exc:
            logger.warning("WebSocket disconnected: %s. Reconnecting in %ds.", exc, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_DELAY_MAX)

        except Exception as exc:
            logger.error("Unexpected error: %s. Reconnecting in %ds.", exc, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_DELAY_MAX)


# ── Snapshot timer ────────────────────────────────────────────────────────────

async def snapshot_timer() -> None:
    """
    Every SNAPSHOT_INTERVAL seconds: compute features for each symbol, append
    to row buffer, and flush to Parquet when ROWS_PER_FILE is reached.
    """
    last_health_log = 0.0

    while not _shutdown:
        await asyncio.sleep(SNAPSHOT_INTERVAL)
        now    = datetime.now(timezone.utc)
        now_ts = now.timestamp()

        for symbol in SYMBOLS:
            _prune_trades(symbol, now_ts)

            book = _book[symbol]
            if book is None:
                continue   # no book state yet — still warming up

            feats = compute_features(book, list(_trades[symbol]), now_ts)
            if feats is None:
                continue   # invalid book state (e.g., crossed book)

            _rows[symbol].append({"timestamp_utc": now_ts, "symbol": symbol, **feats})

            if len(_rows[symbol]) >= ROWS_PER_FILE:
                _flush_to_parquet(symbol, _rows[symbol])
                _rows[symbol] = []

        # Periodic health log: warn if a symbol has gone silent
        if now_ts - last_health_log >= HEALTH_LOG_SECS:
            last_health_log = now_ts
            for symbol in SYMBOLS:
                age = now_ts - _last_msg_ts[symbol]
                if age > 10.0:
                    logger.warning(
                        "%s: no messages received for %.0fs — possible data gap.",
                        symbol, age,
                    )
                else:
                    row_count = len(_rows[symbol])
                    logger.info(
                        "%s: healthy — %d rows buffered, last msg %.1fs ago.",
                        symbol, row_count, age,
                    )


# ── Graceful shutdown ─────────────────────────────────────────────────────────

def _on_shutdown(signum, frame) -> None:
    """Flush remaining buffered rows before exit."""
    global _shutdown
    logger.info("Shutdown signal received. Flushing remaining data...")
    _shutdown = True
    for symbol in SYMBOLS:
        if _rows[symbol]:
            _flush_to_parquet(symbol, _rows[symbol])
            _rows[symbol] = []
    logger.info("Flush complete. Exiting.")
    sys.exit(0)


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    logger.info("Starting LOB collector.")
    logger.info("Symbols  : %s", list(SYMBOLS.keys()))
    logger.info("Output   : %s", DATA_DIR)
    logger.info("Snapshot : every %ss | %s rows per file (~1h)", SNAPSHOT_INTERVAL, ROWS_PER_FILE)
    await asyncio.gather(
        stream_market_data(),
        snapshot_timer(),
    )


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _on_shutdown)
    signal.signal(signal.SIGINT,  _on_shutdown)
    asyncio.run(main())
