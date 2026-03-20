# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
# isort: skip_file
"""
Starter FreqAI strategy for freqtrade-strategy-lab.
Simplified regression setup: targets &s_close / &s_volatility, XGBoostRegressor in config.
Replace thresholds and logic as you iterate — see CLAUDE.md and user_data/info/PROJECT_NOTES.md.
"""
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime

import talib.abstract as ta

from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade


class StarterStrategy_V01(IStrategy):
    minimal_roi = {"0": 0.10, "240": 0.05, "480": 0}
    stoploss = -0.12
    use_custom_stoploss = True

    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    timeframe = "15m"
    inf_1h = "1h"

    can_short = True
    startup_candle_count = 1000

    # Fixed lab thresholds — move to Hyperopt DecimalParameter when ready
    ai_direction_threshold = 0.012
    ai_volatility_threshold = 0.012
    di_max_threshold = 0.45
    stoploss_multiplier = 1.4
    stoploss_hard_cap = 0.04

    def feature_engineering_expand_all(
        self, dataframe: DataFrame, period: int, metadata: dict, **kwargs
    ) -> DataFrame:
        dataframe[f"%-rsi-{period}"] = ta.RSI(dataframe, timeperiod=period)
        dataframe[f"%-roc-{period}"] = ta.ROC(dataframe, timeperiod=period)
        dataframe[f"%-atr-{period}"] = ta.ATR(dataframe, timeperiod=period)
        safe_atr = dataframe[f"%-atr-{period}"].replace(0, np.nan)
        dataframe[f"%-rsi_atr_ratio-{period}"] = dataframe[f"%-rsi-{period}"] / safe_atr
        ema = ta.EMA(dataframe, timeperiod=period)
        dataframe[f"%-ema_dist-{period}"] = (dataframe["close"] - ema) / ema
        bollinger = ta.BBANDS(dataframe, timeperiod=period, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe[f"%-bb_width-{period}"] = (
            bollinger["upperband"] - bollinger["lowerband"]
        ) / bollinger["middleband"]
        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek
        dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        label_period = self.freqai_info["feature_parameters"]["label_period_candles"]
        dataframe["&s_close"] = np.log(dataframe["close"].shift(-label_period) / dataframe["close"])
        future_high = dataframe["high"].rolling(label_period).max().shift(-label_period)
        future_low = dataframe["low"].rolling(label_period).min().shift(-label_period)
        dataframe["&s_volatility"] = (future_high - future_low) / dataframe["close"]
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = self.freqai.start(dataframe, metadata, self)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=9)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=21)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if not self.config.get("freqai", {}).get("enabled", False):
            return dataframe
        if "do_predict" not in dataframe.columns:
            return dataframe
        valid_prediction = dataframe["do_predict"] == 1
        if "DI_values" in dataframe.columns:
            safe_situation = dataframe["DI_values"] < self.di_max_threshold
        else:
            safe_situation = pd.Series(True, index=dataframe.index)
        if "&s_close" not in dataframe.columns or "&s_volatility" not in dataframe.columns:
            return dataframe

        ai_long = (
            (dataframe["&s_close"] > self.ai_direction_threshold)
            & (dataframe["&s_volatility"] > self.ai_volatility_threshold)
        )
        tech_long = (dataframe["rsi"] < 70) & (dataframe["ema_fast"] > dataframe["ema_slow"])
        dataframe.loc[
            valid_prediction & safe_situation & ai_long & tech_long & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        ai_short = (
            (dataframe["&s_close"] < -self.ai_direction_threshold)
            & (dataframe["&s_volatility"] > self.ai_volatility_threshold)
        )
        tech_short = (dataframe["rsi"] > 30) & (dataframe["ema_fast"] < dataframe["ema_slow"])
        dataframe.loc[
            valid_prediction & safe_situation & ai_short & tech_short & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if not self.config.get("freqai", {}).get("enabled", False):
            return dataframe
        if "&s_close" not in dataframe.columns or "DI_values" not in dataframe.columns:
            return dataframe
        di_breach = dataframe["DI_values"] >= self.di_max_threshold
        dataframe.loc[(dataframe["&s_close"] < 0) | di_breach, "exit_long"] = 1
        dataframe.loc[(dataframe["&s_close"] > 0) | di_breach, "exit_short"] = 1
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        if "atr" in last_candle and pd.notna(last_candle["atr"]):
            atr_pct = last_candle["atr"] / trade.open_rate
            dynamic_stop_pct = atr_pct * self.stoploss_multiplier
            dynamic_stop_pct = max(0.010, min(self.stoploss_hard_cap, dynamic_stop_pct))
            if trade.is_short:
                stop_price = trade.open_rate * (1 + dynamic_stop_pct)
                rel_stop = (current_rate - stop_price) / current_rate
            else:
                stop_price = trade.open_rate * (1 - dynamic_stop_pct)
                rel_stop = (stop_price - current_rate) / current_rate
            return rel_stop
        return -0.025

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
        return min(3.0, max_leverage)
