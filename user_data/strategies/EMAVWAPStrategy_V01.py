# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file
"""
EMAVWAP (Candidate O) — Phase 0 quick empirical test.

Signal: EMA(50) × YTD Anchored VWAP crossover.
- Long when EMA50 crosses ABOVE YTD VWAP (bullish institutional regime)
- Short when EMA50 crosses BELOW YTD VWAP (bearish institutional regime)

Exit: reverse crossover + ATR trailing stop (proxy for swing high/low stops) + ROI ladder.

Backtest (repo root, one line):

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_emavwap.json --strategy EMAVWAPStrategy_V01 --timerange 20220101- --timeframe 4h --fee 0.0005 --cache none
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


class EMAVWAPStrategy_V01(IStrategy):
    timeframe = "4h"

    # --- Parameters ---
    EMA_PERIOD: int = 50
    ATR_PERIOD: int = 14
    ATR_MULT: float = 3.0
    SWING_LOOKBACK: int = 20

    can_short = True
    process_only_new_candles = True

    minimal_roi = {"0": 0.10, "120": 0.05, "240": 0.03, "480": 0}
    stoploss = -0.99
    use_custom_stoploss = True
    trailing_stop = False

    startup_candle_count = 200

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._trail_stop_abs: dict[int, float] = {}

    def _row_at(self, pair: str, current_time: datetime) -> pd.Series | None:
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return None
        ct = current_time.replace(tzinfo=timezone.utc) if current_time.tzinfo is None else current_time.astimezone(timezone.utc)
        tcol = pd.to_datetime(df["date"], utc=True)
        mask = tcol <= ct
        if not mask.any():
            return None
        return df.loc[mask].iloc[-1]

    def _cleanup_trail_state(self) -> None:
        open_ids = {t.id for t in Trade.get_open_trades()}
        for tid in list(self._trail_stop_abs.keys()):
            if tid not in open_ids:
                self._trail_stop_abs.pop(tid, None)

    def bot_loop_start(self, current_time: datetime, **kwargs) -> None:
        self._cleanup_trail_state()

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # YTD Anchored VWAP — resets each calendar year
        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
        tp_vol = typical_price * dataframe["volume"]
        year = pd.to_datetime(dataframe["date"]).dt.year
        dataframe["cum_tp_vol"] = tp_vol.groupby(year, sort=False).cumsum()
        dataframe["cum_vol"] = dataframe["volume"].groupby(year, sort=False).cumsum()
        dataframe["ytd_vwap"] = dataframe["cum_tp_vol"] / dataframe["cum_vol"].replace(0, np.nan)

        dataframe["ema50"] = ta.EMA(dataframe, timeperiod=int(self.EMA_PERIOD))
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=int(self.ATR_PERIOD))

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        vol_ok = dataframe["volume"] > 0
        valid = dataframe["ema50"].notna() & dataframe["ytd_vwap"].notna()

        ema = dataframe["ema50"]
        ema_prev = dataframe["ema50"].shift(1)
        vwap = dataframe["ytd_vwap"]
        vwap_prev = dataframe["ytd_vwap"].shift(1)

        long_cross = valid & vol_ok & (ema > vwap) & (ema_prev <= vwap_prev)
        short_cross = valid & vol_ok & (ema < vwap) & (ema_prev >= vwap_prev)

        dataframe.loc[long_cross, "enter_long"] = 1
        dataframe.loc[short_cross, "enter_short"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        valid = dataframe["ema50"].notna() & dataframe["ytd_vwap"].notna()

        ema = dataframe["ema50"]
        ema_prev = dataframe["ema50"].shift(1)
        vwap = dataframe["ytd_vwap"]
        vwap_prev = dataframe["ytd_vwap"].shift(1)

        long_exit = valid & (ema < vwap) & (ema_prev >= vwap_prev)
        short_exit = valid & (ema > vwap) & (ema_prev <= vwap_prev)

        dataframe.loc[long_exit, "exit_long"] = 1
        dataframe.loc[short_exit, "exit_short"] = 1

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
        row = self._row_at(pair, current_time)
        if row is None:
            return self.stoploss

        atr = float(row.get("atr", 0.0) or 0.0)
        close = float(row.get("close", 0.0) or 0.0)
        if atr <= 0 or close <= 0 or current_rate <= 0:
            return self.stoploss

        mult = float(self.ATR_MULT)
        tid = trade.id

        if not trade.is_short:
            cand = close - mult * atr
            if tid not in self._trail_stop_abs:
                init = trade.open_rate - mult * atr
                self._trail_stop_abs[tid] = max(init, cand)
            else:
                self._trail_stop_abs[tid] = max(float(self._trail_stop_abs[tid]), cand)
            stop_price = float(self._trail_stop_abs[tid])
        else:
            cand = close + mult * atr
            if tid not in self._trail_stop_abs:
                init = trade.open_rate + mult * atr
                self._trail_stop_abs[tid] = min(init, cand)
            else:
                self._trail_stop_abs[tid] = min(float(self._trail_stop_abs[tid]), cand)
            stop_price = float(self._trail_stop_abs[tid])

        if stop_price <= 0 or current_rate <= 0:
            return self.stoploss

        if not trade.is_short:
            sl = (stop_price / current_rate) - 1.0
        else:
            sl = (current_rate / stop_price) - 1.0

        return max(sl, -0.99)
