# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
"""
A1-ROFI V02 — Cumulative Delta Divergence (Phase 0 backtest)
================================================================
Variant of A1-ROFI that uses cumulative delta divergence instead of
per-candle imbalance z-score.

Signal
------
Compute cum_delta (sum of bid_vol - ask_vol) and price return over a rolling
window. When cum_delta and price diverge — cum_delta is strongly positive while
price is flat/falling (bullish), or cum_delta is strongly negative while price
is flat/rising (bearish) — it suggests informed absorption: one side is
accumulating while the price hasn't moved yet.

This is a lead indicator: the price should eventually follow the cumulative
delta direction when the absorbing side is done.

Exit: trailing stop + time stop at 6 candles (30 min at 5m).

Phase 0 scope: BTC + ETH, Jan 2026.
"""

import logging
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_open

logger = logging.getLogger(__name__)


class A1_ROFI_V02(IStrategy):
    # -------------------------------------------------------------------------
    # STRATEGY CONFIG
    # -------------------------------------------------------------------------
    timeframe = "5m"
    startup_candle_count: int = 300

    can_short = True
    use_public_trades = True
    process_only_new_candles = True

    # -------------------------------------------------------------------------
    # EXIT CONFIG
    # -------------------------------------------------------------------------
    minimal_roi: dict = {
        "0":  0.04,
        "15": 0.02,
        "30": 0.00,
    }

    stoploss: float = -0.99
    use_custom_stoploss: bool = True

    # -------------------------------------------------------------------------
    # SIGNAL PARAMETERS
    # -------------------------------------------------------------------------
    DIVERGENCE_WINDOW: int = 20               # candles for cum_delta / price return
    CUM_DELTA_THRESHOLD: float = 0.02         # |norm_cum_delta| > threshold (2% of volume)
    PRICE_FLAT_MAX: float = 0.003             # |price_return| < threshold (0.3%)
    STOP_FROM_ENTRY: float = 0.03             # 3% hard stop from entry
    MAX_HOLD_CANDLES: int = 6                 # 30 min time stop

    # -------------------------------------------------------------------------
    # LEVERAGE
    # -------------------------------------------------------------------------
    LEVERAGE_FULL: float = 2.0

    # -------------------------------------------------------------------------
    # INDICATORS
    # -------------------------------------------------------------------------
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Cumulative delta over rolling window
        dataframe["cum_delta"] = dataframe["delta"].rolling(self.DIVERGENCE_WINDOW).sum()

        # Total volume over same window (bid + ask)
        total_vol = (dataframe["bid"] + dataframe["ask"]).rolling(self.DIVERGENCE_WINDOW).sum()
        dataframe["norm_cum_delta"] = np.where(
            total_vol > 0,
            dataframe["cum_delta"] / total_vol,
            0.0,
        )

        # Price return over window
        dataframe["price_return"] = (
            dataframe["close"] / dataframe["close"].shift(self.DIVERGENCE_WINDOW) - 1.0
        )

        return dataframe

    # -------------------------------------------------------------------------
    # ENTRY
    # -------------------------------------------------------------------------
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if "norm_cum_delta" not in dataframe.columns:
            return dataframe

        ncd = dataframe["norm_cum_delta"]
        pr = dataframe["price_return"]
        cdt = self.CUM_DELTA_THRESHOLD
        pfm = self.PRICE_FLAT_MAX

        # Bullish divergence: strong positive cum_delta but price hasn't moved up yet
        # Buyers are absorbing — price should follow up
        dataframe.loc[
            (ncd > cdt) & (pr < pfm) & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Bearish divergence: strong negative cum_delta but price hasn't moved down yet
        # Sellers are absorbing — price should follow down
        dataframe.loc[
            (ncd < -cdt) & (pr > -pfm) & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    # -------------------------------------------------------------------------
    # EXIT
    # -------------------------------------------------------------------------
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    # -------------------------------------------------------------------------
    # CUSTOM STOPLOSS
    # -------------------------------------------------------------------------
    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        return stoploss_from_open(self.STOP_FROM_ENTRY, current_profit, is_short=trade.is_short)

    # -------------------------------------------------------------------------
    # CUSTOM EXIT — time stop
    # -------------------------------------------------------------------------
    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> str | None:
        if trade.open_date_utc is None:
            return None
        hold_minutes = (current_time - trade.open_date_utc).total_seconds() / 60
        if hold_minutes >= self.MAX_HOLD_CANDLES * 5:
            return "time_stop"
        return None

    # -------------------------------------------------------------------------
    # LEVERAGE
    # -------------------------------------------------------------------------
    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: str,
        side: str,
        **kwargs,
    ) -> float:
        return min(self.LEVERAGE_FULL, max_leverage)
