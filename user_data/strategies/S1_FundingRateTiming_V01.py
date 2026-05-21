# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
"""
S1 — Funding Rate Timing V01 (Phase 0 backtest)
=================================================
Entry window: 5-15 min before Binance 8h funding payments (00:00, 08:00, 16:00 UTC).
Extreme funding rate filter applied when data available.

Phase 0: BTC + ETH, Apr 20 – May 10 2026.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

import json

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_open

logger = logging.getLogger(__name__)


class S1_FundingRateTiming_V01(IStrategy):
    timeframe = "5m"
    startup_candle_count: int = 2000

    can_short = True
    process_only_new_candles = True

    minimal_roi: dict = {
        "0":  0.015,
        "10": 0.008,
        "15": 0.000,
    }

    stoploss: float = -0.99
    use_custom_stoploss: bool = True

    FUNDING_PCT_LONG: float = 0.10       # Bottom decile (rank returns 0-1)
    FUNDING_PCT_SHORT: float = 0.90      # Top decile
    FUNDING_PCT_WINDOW: int = 720
    ENTRY_WINDOW_MIN: int = 5
    ENTRY_WINDOW_MAX: int = 15
    STOP_FROM_ENTRY: float = 0.02

    LEVERAGE_FULL: float = 2.0
    FUNDING_HOURS: list = [0, 8, 16]

    # -------------------------------------------------------------------------
    # INDICATORS
    # -------------------------------------------------------------------------
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # --- Funding rate from feather file ---
        pair_slug = metadata["pair"].replace("/", "_").replace(":", "_")
        funding_path = Path(
            f"/freqtrade/user_data/data/binance/futures/{pair_slug}-1h-funding_rate.feather"
        )

        has_funding = False
        if funding_path.exists():
            try:
                funding_df = pd.read_feather(funding_path)
                # Freqtrade stores funding rate in OHLCV format — the "open"
                # column is the actual funding rate value.
                if not funding_df.empty and "open" in funding_df.columns:
                    funding_df = funding_df.sort_index()
                    fr_series = funding_df["open"]
                    merged = fr_series.reindex(dataframe.index)
                    merged = merged.ffill()
                    dataframe["funding_rate"] = merged
                    n_vals = int(merged.notna().sum())
                    if n_vals > 10:
                        has_funding = True
            except Exception:
                pass

        if has_funding:
            dataframe["funding_rate_pct"] = (
                dataframe["funding_rate"]
                .expanding(min_periods=200)
                .rank(pct=True)
            )
        else:
            dataframe["funding_rate_pct"] = 0.5

        # Minutes until next funding payment
        dataframe["minutes_to_funding"] = dataframe["date"].apply(self._minutes_to_funding)

        return dataframe

    # -------------------------------------------------------------------------
    # ENTRY
    # -------------------------------------------------------------------------
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if "minutes_to_funding" not in dataframe.columns:
            return dataframe

        mtf = dataframe["minutes_to_funding"]
        frp = dataframe["funding_rate_pct"]

        in_window = (
            (mtf >= self.ENTRY_WINDOW_MIN)
            & (mtf < self.ENTRY_WINDOW_MAX)
            & (dataframe["volume"] > 0)
        )

        # V02: momentum-continuation — trade WITH the funding direction
        # Extreme positive funding = strong upward momentum = go LONG
        # Extreme negative funding = strong downward momentum = go SHORT
        dataframe.loc[
            in_window & (frp > self.FUNDING_PCT_SHORT),
            "enter_long",
        ] = 1

        dataframe.loc[
            in_window & (frp < self.FUNDING_PCT_LONG),
            "enter_short",
        ] = 1

        return dataframe

    # -------------------------------------------------------------------------
    # EXIT
    # -------------------------------------------------------------------------
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        return stoploss_from_open(self.STOP_FROM_ENTRY, current_profit, is_short=trade.is_short)

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if trade.open_date_utc is None:
            return None
        if (current_time - trade.open_date_utc).total_seconds() / 60 >= 20:
            return "time_stop"
        return None

    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage,
                 entry_tag, side, **kwargs):
        return min(self.LEVERAGE_FULL, max_leverage)

    def _minutes_to_funding(self, dt: datetime) -> int:
        hour = dt.hour
        minute = dt.minute
        current_minutes = hour * 60 + minute
        for fh in self.FUNDING_HOURS:
            f_minutes = fh * 60
            if f_minutes > current_minutes:
                return f_minutes - current_minutes
        return (24 * 60 - current_minutes) + self.FUNDING_HOURS[0] * 60
