"""
LOB Microstructure Feature Engineering
=======================================
Pure functions — no I/O, no state, no side-effects.
Callable from lob_collector.py (real-time) and the offline training pipeline.

Feature families (per arXiv 2602.00776, Bieganowski & Ślepaczuk):
  1. Top-of-book metrics  : mid price, relative spread, L1 bid/ask quantities
  2. Order flow imbalance : net signed taker USD volume over rolling windows
  3. VWAP-to-mid deviations: buy and sell VWAP vs mid price, per window

All features use relative/ratio measures — scale-invariant across assets.
Deep book levels deliberately excluded (paper finding: adds noise, hurts portability).

Windows: 5s, 30s, 120s (computed for all OFI and VWAP features).
"""

from __future__ import annotations

from typing import NamedTuple


# ── Data types ────────────────────────────────────────────────────────────────

class BookState(NamedTuple):
    """Current L1 order book snapshot."""
    bid_price: float
    bid_qty:   float
    ask_price: float
    ask_qty:   float
    ts:        float   # Unix timestamp (seconds UTC) of last update


class TradeRecord(NamedTuple):
    """Single aggregated trade event."""
    ts:     float   # Unix timestamp (seconds UTC)
    price:  float
    qty:    float   # base currency quantity
    usd:    float   # notional value (price × qty)
    is_buy: bool    # True = taker was the buyer (buy aggression)
                    # Binance aggTrade: m=False → buyer is taker → is_buy=True
                    #                  m=True  → seller is taker → is_buy=False


# ── Feature windows ───────────────────────────────────────────────────────────

WINDOWS = (5, 30, 120)   # seconds — must match FEATURE_COLUMNS order below


# ── Column name registry ──────────────────────────────────────────────────────
# Used to enforce schema consistency between sidecar (write) and training (read).

FEATURE_COLUMNS: list[str] = [
    # Top-of-book (instantaneous)
    "mid",
    "spread_rel",
    "bid_qty_l1",
    "ask_qty_l1",
    "vol_imbalance_l1",
    # Per-window features (order matches WINDOWS tuple)
    "ofi_5s",
    "buy_vwap_dev_5s",
    "sell_vwap_dev_5s",
    "ofi_30s",
    "buy_vwap_dev_30s",
    "sell_vwap_dev_30s",
    "ofi_120s",
    "buy_vwap_dev_120s",
    "sell_vwap_dev_120s",
]


# ── Core feature computation ──────────────────────────────────────────────────

def compute_features(
    book:    BookState,
    trades:  list[TradeRecord],
    now_ts:  float,
) -> dict[str, float] | None:
    """
    Compute all LOB microstructure features from current state.

    Args:
        book:    Latest L1 order book snapshot.
        trades:  Recent trade records (pre-pruned to max window age by caller).
        now_ts:  Current Unix timestamp (seconds UTC).

    Returns:
        Dict mapping FEATURE_COLUMNS names to float values, or None if the
        book state is invalid (crossed book, zero prices, or not yet populated).
    """
    if book is None:
        return None
    if book.bid_price <= 0.0 or book.ask_price <= 0.0:
        return None
    if book.ask_price <= book.bid_price:
        return None  # crossed book — data error, skip this snapshot

    # ── Top-of-book metrics ────────────────────────────────────────────────────
    mid        = (book.bid_price + book.ask_price) / 2.0
    spread_rel = (book.ask_price - book.bid_price) / mid
    denom      = book.bid_qty + book.ask_qty
    vol_imbalance_l1 = (
        (book.bid_qty - book.ask_qty) / denom if denom > 0.0 else 0.0
    )

    feats: dict[str, float] = {
        "mid":              mid,
        "spread_rel":       spread_rel,
        "bid_qty_l1":       book.bid_qty,
        "ask_qty_l1":       book.ask_qty,
        "vol_imbalance_l1": vol_imbalance_l1,
    }

    # ── Per-window OFI and VWAP deviations ────────────────────────────────────
    for w in WINDOWS:
        cutoff        = now_ts - w
        window_trades = [t for t in trades if t.ts >= cutoff]

        buy_trades  = [t for t in window_trades if t.is_buy]
        sell_trades = [t for t in window_trades if not t.is_buy]

        buy_usd  = sum(t.usd for t in buy_trades)
        sell_usd = sum(t.usd for t in sell_trades)

        # Order flow imbalance: positive = net buy pressure, negative = net sell
        ofi = buy_usd - sell_usd

        # VWAP deviation from mid (USD-weighted average trade price vs mid)
        # Buy trades execute at/above ask → expect buy_vwap_dev >= 0 typically
        # Sell trades execute at/below bid → expect sell_vwap_dev <= 0 typically
        # Large deviations from mid signal aggressive or urgency-driven flow
        if buy_usd > 0.0:
            buy_vwap     = sum(t.price * t.usd for t in buy_trades) / buy_usd
            buy_vwap_dev = (buy_vwap - mid) / mid
        else:
            buy_vwap_dev = 0.0   # no buy flow this window

        if sell_usd > 0.0:
            sell_vwap     = sum(t.price * t.usd for t in sell_trades) / sell_usd
            sell_vwap_dev = (sell_vwap - mid) / mid
        else:
            sell_vwap_dev = 0.0  # no sell flow this window

        feats[f"ofi_{w}s"]           = ofi
        feats[f"buy_vwap_dev_{w}s"]  = buy_vwap_dev
        feats[f"sell_vwap_dev_{w}s"] = sell_vwap_dev

    return feats
