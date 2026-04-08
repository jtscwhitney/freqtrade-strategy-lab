# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
# isort: skip_file
"""
AdaptiveTrend (Candidate M) — Phase 0 MVP: ROC momentum + ATR trailing (Bui & Nguyen 2026).

- Signal: MOM_t = (P_t - P_{t-L}) / P_{t-L}; long if MOM > θ, short if MOM < -θ
- Exit: ATR trailing per paper — long: S_t = max(S_{t-1}, P_t - α×ATR); short: S_t = min(S_{t-1}, P_t + α×ATR)
- 70/30 slot caps: max 10 concurrent longs, 5 shorts (15 pairs total in config).

Parameter grid for Phase 0: edit MOM_LOOKBACK and THETA_ENTRY (3×3 runs).

Backtest (repo root, one line):

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_adaptivetrend.json --strategy AdaptiveTrendStrategy_V01 --timerange 20220101-20250101 --timeframe 6h --fee 0.0005 --cache none
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy


class AdaptiveTrendStrategy_V01(IStrategy):
    timeframe = "6h"

    # --- Phase 0 defaults (Bui paper center; sweep L ∈ {12,24,42}, θ ∈ {0.02,0.03,0.05}) ---
    MOM_LOOKBACK: int = 24
    THETA_ENTRY: float = 0.03
    ATR_PERIOD: int = 14
    ATR_MULT: float = 3.5

    # Liquid long universe (top-cap); whitelist in config must match or be a subset.
    LONG_PAIRS: frozenset[str] = frozenset(
        {
            "BTC/USDT:USDT",
            "ETH/USDT:USDT",
            "BNB/USDT:USDT",
            "SOL/USDT:USDT",
            "XRP/USDT:USDT",
            "DOGE/USDT:USDT",
            "ADA/USDT:USDT",
            "AVAX/USDT:USDT",
            "DOT/USDT:USDT",
            "LINK/USDT:USDT",
            "UNI/USDT:USDT",
            "ATOM/USDT:USDT",
            "NEAR/USDT:USDT",
            "APT/USDT:USDT",
            "OP/USDT:USDT",
        }
    )
    SHORT_PAIRS: frozenset[str] = frozenset(
        {
            "ETH/USDT:USDT",
            "SOL/USDT:USDT",
            "BNB/USDT:USDT",
            "XRP/USDT:USDT",
            "ADA/USDT:USDT",
            "AVAX/USDT:USDT",
        }
    )

    MAX_CONCURRENT_LONG: int = 10
    MAX_CONCURRENT_SHORT: int = 5

    can_short = True
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
        L = int(self.MOM_LOOKBACK)
        dataframe["mom"] = dataframe["close"].pct_change(periods=L)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=int(self.ATR_PERIOD))
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        vol = dataframe["volume"] > 0
        mom = dataframe["mom"]
        valid = mom.notna() & dataframe["atr"].notna()

        long_ok = vol & valid & (mom > float(self.THETA_ENTRY)) & (pair in self.LONG_PAIRS)
        dataframe.loc[long_ok, "enter_long"] = 1

        if self.SHORT_PAIRS and pair in self.SHORT_PAIRS:
            short_ok = vol & valid & (mom < -float(self.THETA_ENTRY))
            dataframe.loc[short_ok, "enter_short"] = 1

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

        base_sl = (stop_price - current_rate) / max(current_rate, 1e-12)
        if not trade.is_short:
            return max(float(base_sl), float(self.stoploss))
        # Short: stop above price → positive return (see BollingerBandsStrategyV9 pattern).
        if base_sl <= 0:
            return 0.05
        return min(float(base_sl), 0.99)

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
