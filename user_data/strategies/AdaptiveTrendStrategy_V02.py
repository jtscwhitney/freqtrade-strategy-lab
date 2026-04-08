# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
# isort: skip_file
"""
AdaptiveTrend (Candidate M) — Phase 0 V02: expanded 61-pair universe (top-15 + 46 mid-caps).

V01 finding: long signal weak on large-cap-only; short leg carried all profit.
Hypothesis: mid/small-cap pairs exhibit stronger momentum → improves long-side PF.

Changes vs V01:
- LONG_PAIRS: expanded from 15 → 61 (top-15 + 46 established mid-caps)
- SHORT_PAIRS: expanded from 6 → 21 (original 6 large-caps + 15 liquid mid-caps)
- ATR_MULT: 3.5 (empirically better than 2.5 from V01 testing)
- MAX_CONCURRENT_LONG: 25 (scaled for larger universe)
- MAX_CONCURRENT_SHORT: 12
- can_short: False initially (long-only baseline first per Phase 0 protocol)

Survivorship bias note: pairs selected from those active today with history to 2022.
Pairs without 6h data back to 2022-01-01 are excluded after download verification.

Backtest (repo root):
    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_adaptivetrend_v2.json --strategy AdaptiveTrendStrategy_V02 --timerange 20220101-20250101 --timeframe 6h --fee 0.001 --cache none
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


class AdaptiveTrendStrategy_V02(IStrategy):
    timeframe = "6h"

    MOM_LOOKBACK: int = 24
    THETA_ENTRY: float = 0.03
    ATR_PERIOD: int = 14
    ATR_MULT: float = 3.5  # V01 empirical optimum; 2.5 (paper default) was too tight

    # --- Top-15 large-caps (V01 universe) ---
    _TOP15: frozenset[str] = frozenset({
        "BTC/USDT:USDT", "ETH/USDT:USDT", "BNB/USDT:USDT", "SOL/USDT:USDT",
        "XRP/USDT:USDT", "DOGE/USDT:USDT", "ADA/USDT:USDT", "AVAX/USDT:USDT",
        "DOT/USDT:USDT", "LINK/USDT:USDT", "UNI/USDT:USDT", "ATOM/USDT:USDT",
        "NEAR/USDT:USDT", "APT/USDT:USDT", "OP/USDT:USDT",
    })

    # --- 46 established mid-caps (Binance futures, active, data from ≥2022) ---
    _MIDCAPS: frozenset[str] = frozenset({
        "AAVE/USDT:USDT", "ALGO/USDT:USDT", "AXS/USDT:USDT", "BAND/USDT:USDT",
        "BCH/USDT:USDT", "CELO/USDT:USDT", "CELR/USDT:USDT", "CHZ/USDT:USDT",
        "COMP/USDT:USDT", "CRV/USDT:USDT", "DYDX/USDT:USDT", "EGLD/USDT:USDT",
        "ENJ/USDT:USDT", "ETC/USDT:USDT", "FIL/USDT:USDT", "FLOW/USDT:USDT",
        "GALA/USDT:USDT", "GRT/USDT:USDT", "HBAR/USDT:USDT", "HOT/USDT:USDT",
        "ICX/USDT:USDT", "ICP/USDT:USDT", "IOTA/USDT:USDT", "IOTX/USDT:USDT",
        "KAVA/USDT:USDT", "KSM/USDT:USDT", "LTC/USDT:USDT", "MANA/USDT:USDT",
        "ONE/USDT:USDT", "ONT/USDT:USDT", "ROSE/USDT:USDT", "RUNE/USDT:USDT",
        "SAND/USDT:USDT", "SKL/USDT:USDT", "SNX/USDT:USDT", "STORJ/USDT:USDT",
        "SUSHI/USDT:USDT", "THETA/USDT:USDT", "TRX/USDT:USDT", "VET/USDT:USDT",
        "XLM/USDT:USDT", "XTZ/USDT:USDT", "YFI/USDT:USDT", "ZEC/USDT:USDT",
        "ZIL/USDT:USDT", "1INCH/USDT:USDT",
    })

    LONG_PAIRS: frozenset[str] = _TOP15 | _MIDCAPS  # 61 pairs total

    SHORT_PAIRS: frozenset[str] = frozenset({
        # Original 6 large-cap shorts
        "ETH/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT",
        "XRP/USDT:USDT", "ADA/USDT:USDT", "AVAX/USDT:USDT",
        # 15 liquid mid-cap shorts (high-volatility, known trend characteristics)
        "AAVE/USDT:USDT", "AXS/USDT:USDT", "CRV/USDT:USDT", "DYDX/USDT:USDT",
        "ETC/USDT:USDT", "FIL/USDT:USDT", "GALA/USDT:USDT", "GRT/USDT:USDT",
        "ICP/USDT:USDT", "LTC/USDT:USDT", "RUNE/USDT:USDT", "SAND/USDT:USDT",
        "SNX/USDT:USDT", "SUSHI/USDT:USDT", "ALGO/USDT:USDT",
    })

    MAX_CONCURRENT_LONG: int = 25
    MAX_CONCURRENT_SHORT: int = 12

    can_short = False  # Phase 0 Step 1: long-only baseline; set True for Step 3

    process_only_new_candles = True
    minimal_roi = {"0": 100}
    stoploss = -0.99
    use_custom_stoploss = True
    trailing_stop = False
    startup_candle_count = 50

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
        dataframe["mom"] = dataframe["close"].pct_change(periods=int(self.MOM_LOOKBACK))
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=int(self.ATR_PERIOD))
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        vol = dataframe["volume"] > 0
        valid = dataframe["mom"].notna() & dataframe["atr"].notna()

        if pair in self.LONG_PAIRS:
            dataframe.loc[vol & valid & (dataframe["mom"] > float(self.THETA_ENTRY)), "enter_long"] = 1

        if self.SHORT_PAIRS and pair in self.SHORT_PAIRS:
            dataframe.loc[vol & valid & (dataframe["mom"] < -float(self.THETA_ENTRY)), "enter_short"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time: datetime,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> bool:
        open_trades = Trade.get_open_trades()
        n_long = sum(1 for t in open_trades if not t.is_short)
        n_short = sum(1 for t in open_trades if t.is_short)
        if side == "long":
            return pair in self.LONG_PAIRS and n_long < int(self.MAX_CONCURRENT_LONG)
        if side == "short":
            return pair in self.SHORT_PAIRS and n_short < int(self.MAX_CONCURRENT_SHORT)
        return True

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
                self._trail_stop_abs[tid] = max(trade.open_rate - mult * atr, cand)
            else:
                self._trail_stop_abs[tid] = max(float(self._trail_stop_abs[tid]), cand)
            stop_price = float(self._trail_stop_abs[tid])
            return max((stop_price - current_rate) / max(current_rate, 1e-12), float(self.stoploss))
        else:
            cand = close + mult * atr
            if tid not in self._trail_stop_abs:
                self._trail_stop_abs[tid] = min(trade.open_rate + mult * atr, cand)
            else:
                self._trail_stop_abs[tid] = min(float(self._trail_stop_abs[tid]), cand)
            stop_price = float(self._trail_stop_abs[tid])
            base_sl = (stop_price - current_rate) / max(current_rate, 1e-12)
            return min(max(base_sl, 0.05), 0.99)

    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        return min(1.0, float(max_leverage))
