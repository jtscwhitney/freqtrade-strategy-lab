# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
"""
A1-ROFI V01 — Order Flow Imbalance at Candle Level (Phase 0 backtest)
========================================================================
Sweep #8 candidate. Resurrects Candidate A's validated OFI signal (IC=0.135,
dir_acc=54.2% at 3s) at Freqtrade-native 5m candle level where fee math is
improved: 10 bps RT vs 5-10 bps typical 5m move = 1-2x ratio (vs 6x at 3s).

Signal
------
Freqtrade orderflow provides per-candle `delta` (bid_vol - ask_vol) from
public trade data. We compute a rolling z-score of the trade imbalance ratio
and enter when |z| > threshold in the direction of the imbalance.

Exit: trailing stop + time stop at 6 candles (30 min at 5m).

Phase 0 scope: BTC/USDT:USDT only, 2022-2026 backtest.
"""

import logging
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_open

logger = logging.getLogger(__name__)


class A1_ROFI_V01(IStrategy):
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
    # SIGNAL PARAMETERS (Phase 0 defaults — calibrate from backtest)
    # -------------------------------------------------------------------------
    IMBALANCE_Z_THRESHOLD: float = 2.0       # |z| > threshold to enter
    IMBALANCE_Z_WINDOW: int = 20             # rolling window for z-score
    STOP_FROM_ENTRY: float = 0.03            # 3% hard stop from entry at 2x = 1.5% price
    MAX_HOLD_CANDLES: int = 6                # 30 min time stop

    # -------------------------------------------------------------------------
    # LEVERAGE
    # -------------------------------------------------------------------------
    LEVERAGE_FULL: float = 2.0

    # -------------------------------------------------------------------------
    # INDICATORS
    # -------------------------------------------------------------------------
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # --- Trade imbalance from Freqtrade orderflow ---
        # `delta` = bid_vol - ask_vol per candle (populated by Freqtrade when
        # use_public_trades = True). `bid` and `ask` are also available.
        bid_ask_total = dataframe["bid"] + dataframe["ask"]
        dataframe["imbalance_ratio"] = np.where(
            bid_ask_total > 0,
            dataframe["delta"] / bid_ask_total,
            0.0,
        )

        # Rolling z-score of imbalance ratio
        roll_mean = dataframe["imbalance_ratio"].rolling(self.IMBALANCE_Z_WINDOW).mean()
        roll_std = dataframe["imbalance_ratio"].rolling(self.IMBALANCE_Z_WINDOW).std()
        dataframe["imbalance_z"] = np.where(
            roll_std > 0,
            (dataframe["imbalance_ratio"] - roll_mean) / roll_std,
            0.0,
        )

        return dataframe

    # -------------------------------------------------------------------------
    # ENTRY
    # -------------------------------------------------------------------------
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if "imbalance_z" not in dataframe.columns:
            return dataframe

        z = dataframe["imbalance_z"]
        threshold = self.IMBALANCE_Z_THRESHOLD

        # Long: extreme positive imbalance (buy volume >> sell volume)
        dataframe.loc[
            (z > threshold) & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: extreme negative imbalance (sell volume >> buy volume)
        dataframe.loc[
            (z < -threshold) & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    # -------------------------------------------------------------------------
    # EXIT
    # -------------------------------------------------------------------------
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # No exit signals — exits handled by custom_stoploss + custom_exit
        return dataframe

    # -------------------------------------------------------------------------
    # CUSTOM STOPLOSS — fixed from entry
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
