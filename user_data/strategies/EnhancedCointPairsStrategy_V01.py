# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
EnhancedCointPairsStrategy_V01 — Candidate L Phase 1: dual-leg BTC/ETH @ 4h

Phase 0: BTC/ETH@4h scored GO (6/8). Dual-leg spread: log(BTC) - β * log(ETH).

Entries:
- z > +ENTRY: short BTC, long ETH
- z < -ENTRY: long BTC, short ETH
- Optional vol filter (Palazzi-style): spread vol vs rolling p90 — **off by default**; lab backtests showed
  it + spread trail cut net P&L vs z-reversion + time stop on this pair/TF.

Exits:
- z reversion (populate_exit_trend)
- Optional adaptive spread trail (custom_exit) — **off by default** (same A/B result as vol filter)
- Time stop
- Orphan / partner_closed: dual-leg safety

`custom_stake_amount`: β-weights 1/(1+β) BTC, β/(1+β) ETH per slot.

Set ENABLE_VOL_FILTER / ENABLE_SPREAD_TRAIL True to experiment toward Palazzi-style live risk control.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime

from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.strategy.parameters import DecimalParameter, IntParameter
from freqtrade.persistence import Trade


class EnhancedCointPairsStrategy_V01(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "4h"
    inf_tf = "4h"

    minimal_roi = {"0": 100}
    stoploss = -0.99
    use_custom_stoploss = False

    can_short = True

    # Backtest A/B (2026-03): z + time + β stakes ≈ +24% full-sample; vol+trail ≈ flat — defaults follow the former.
    ENABLE_VOL_FILTER: bool = False
    ENABLE_SPREAD_TRAIL: bool = False

    # ≥ max(ols_window, zscore_window) + vol warm-up; 500 covers hyperopt upper ranges.
    startup_candle_count: int = 500

    # Hyperopt spaces (defaults match Phase 0–aligned manual backtest)
    entry_zscore = DecimalParameter(1.5, 3.0, default=2.0, decimals=2, space="buy")
    exit_zscore = DecimalParameter(0.0, 1.0, default=0.5, decimals=2, space="sell")
    zscore_window = IntParameter(12, 180, default=84, space="buy")
    ols_window = IntParameter(120, 270, default=180, space="buy")
    max_hold_candles = IntParameter(240, 480, default=360, space="sell")

    # Volatility filter: 24h = 6 × 4h candles; percentile lookback ~30d
    SPREAD_VOL_WINDOW: int = 6
    SPREAD_VOL_PCT_LOOKBACK: int = 180
    VOL_PERCENTILE: float = 0.90

    # Adaptive trailing: close if spread moves against position by TRAIL_K × local spread vol
    TRAIL_K: float = 2.0

    # Only for missing partner at entry; not when partner already exited (trail/z).
    ORPHAN_MAX_CANDLES: int = 6

    _ANCHOR = "ETH/USDT:USDT"
    _TRADED = "BTC/USDT:USDT"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        # session_floor_str -> {"max": float, "min": float} for trailing (both legs share key)
        self._spread_extreme: dict[str, dict[str, float]] = {}
        self._had_partner: set[int] = set()  # trade ids that saw both legs open

    def informative_pairs(self) -> list[tuple[str, str]]:
        return [
            (self._TRADED, self.inf_tf),
            (self._ANCHOR, self.inf_tf),
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        if pair == self._TRADED:
            other = self.dp.get_pair_dataframe(self._ANCHOR, self.inf_tf)
            if other.empty:
                return self._nan_frame(dataframe)
            other = other[["date", "close"]].rename(columns={"close": "anchor_close"})
            dataframe = merge_informative_pair(
                dataframe, other, self.timeframe, self.inf_tf,
                ffill=True, date_column="date",
            )
            acol = f"anchor_close_{self.inf_tf}"
            log_y = np.log(dataframe["close"])
            log_x = np.log(dataframe[acol])
        else:
            other = self.dp.get_pair_dataframe(self._TRADED, self.inf_tf)
            if other.empty:
                return self._nan_frame(dataframe)
            other = other[["date", "close"]].rename(columns={"close": "traded_close"})
            dataframe = merge_informative_pair(
                dataframe, other, self.timeframe, self.inf_tf,
                ffill=True, date_column="date",
            )
            tcol = f"traded_close_{self.inf_tf}"
            log_y = np.log(dataframe[tcol])
            log_x = np.log(dataframe["close"])

        dataframe["hedge_ratio"] = self._rolling_hedge_ratio(log_y, log_x, int(self.ols_window.value))
        dataframe["spread"] = log_y - dataframe["hedge_ratio"] * log_x
        zw = int(self.zscore_window.value)
        sm = dataframe["spread"].rolling(zw).mean()
        sd = dataframe["spread"].rolling(zw).std().replace(0, np.nan)
        dataframe["z_score"] = (dataframe["spread"] - sm) / sd

        spread_vol = dataframe["spread"].rolling(self.SPREAD_VOL_WINDOW).std()
        dataframe["spread_vol"] = spread_vol
        vol_thr = spread_vol.rolling(self.SPREAD_VOL_PCT_LOOKBACK).quantile(self.VOL_PERCENTILE)
        if self.ENABLE_VOL_FILTER:
            dataframe["spread_vol_ok"] = (spread_vol <= vol_thr) | vol_thr.isna()
        else:
            dataframe["spread_vol_ok"] = 1

        return dataframe

    def _nan_frame(self, dataframe: DataFrame) -> DataFrame:
        dataframe["z_score"] = np.nan
        dataframe["spread_vol_ok"] = 1
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        ok = dataframe["z_score"].notna() & (dataframe["volume"] > 0)
        if self.ENABLE_VOL_FILTER:
            ok = ok & (dataframe["spread_vol_ok"] == 1)

        ez = float(self.entry_zscore.value)
        if pair == self._TRADED:
            dataframe.loc[ok & (dataframe["z_score"] < -ez), "enter_long"] = 1
            dataframe.loc[ok & (dataframe["z_score"] > ez), "enter_short"] = 1
        else:
            dataframe.loc[ok & (dataframe["z_score"] > ez), "enter_long"] = 1
            dataframe.loc[ok & (dataframe["z_score"] < -ez), "enter_short"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        has_signal = dataframe["z_score"].notna()

        xz = float(self.exit_zscore.value)
        if pair == self._TRADED:
            dataframe.loc[has_signal & (dataframe["z_score"] > -xz), "exit_long"] = 1
            dataframe.loc[has_signal & (dataframe["z_score"] < xz), "exit_short"] = 1
        else:
            dataframe.loc[has_signal & (dataframe["z_score"] < xz), "exit_long"] = 1
            dataframe.loc[has_signal & (dataframe["z_score"] > -xz), "exit_short"] = 1

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
        """Do not stack beyond two pair legs; block duplicate same-pair entries."""
        open_bt = [t for t in Trade.get_open_trades() if t.pair == self._TRADED]
        open_eth = [t for t in Trade.get_open_trades() if t.pair == self._ANCHOR]
        if pair == self._TRADED and open_bt:
            return False
        if pair == self._ANCHOR and open_eth:
            return False
        if len(open_bt) + len(open_eth) >= 2:
            return False
        return True

    def _session_key(self, trade: Trade) -> str:
        ts = pd.Timestamp(trade.open_date_utc).floor("4h")
        return str(ts.value)

    def _is_short_spread_leg(self, trade: Trade) -> bool:
        """Short-spread regime: BTC short + ETH long (z > ENTRY)."""
        if trade.pair == self._TRADED:
            return bool(trade.is_short)
        return not bool(trade.is_short)

    def _tf_seconds(self) -> int:
        return int(pd.Timedelta(self.timeframe).total_seconds())

    def _both_pair_legs_open(self) -> bool:
        """True when BTC and ETH each have an open trade (paired session)."""
        pairs = {t.pair for t in Trade.get_open_trades() if t.pair in (self._TRADED, self._ANCHOR)}
        return self._TRADED in pairs and self._ANCHOR in pairs

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> str | None:
        tf_sec = self._tf_seconds()
        trade_duration_candles = int((current_time - trade.open_date_utc).total_seconds() / tf_sec)

        if self._both_pair_legs_open():
            self._had_partner.add(int(trade.id))

        if not self._both_pair_legs_open():
            if int(trade.id) not in self._had_partner:
                if trade_duration_candles >= self.ORPHAN_MAX_CANDLES:
                    return "orphan_close"
                return None
            return "partner_closed"

        if self.ENABLE_SPREAD_TRAIL:
            df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if df.empty:
                return None
            sub = df.loc[df["date"] <= current_time]
            if sub.empty:
                return None
            row = sub.iloc[-1]
            spread = float(row["spread"])
            sv = row["spread_vol"]
            vol = float(sv) if not pd.isna(sv) else float(sub["spread"].tail(self.SPREAD_VOL_WINDOW).std())
            if np.isnan(vol) or vol <= 0:
                vol = 1e-12

            sk = self._session_key(trade)
            if sk not in self._spread_extreme:
                self._spread_extreme[sk] = {"max": spread, "min": spread}
            else:
                self._spread_extreme[sk]["max"] = max(self._spread_extreme[sk]["max"], spread)
                self._spread_extreme[sk]["min"] = min(self._spread_extreme[sk]["min"], spread)
            ex = self._spread_extreme[sk]
            short_spread = self._is_short_spread_leg(trade)
            if short_spread:
                if spread < ex["max"] - self.TRAIL_K * vol:
                    return "trail_spread"
            else:
                if spread > ex["min"] + self.TRAIL_K * vol:
                    return "trail_spread"

        if trade_duration_candles >= int(self.max_hold_candles.value):
            return "time_stop"
        return None

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
        return min(2.0, max_leverage)

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        """Split one slot's budget across legs with β-weights (log-spread hedge)."""
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return proposed_stake
        row = df.loc[df["date"] <= current_time]
        if row.empty:
            return proposed_stake
        beta = float(row["hedge_ratio"].iloc[-1])
        if np.isnan(beta) or beta <= 0:
            return proposed_stake
        den = 1.0 + beta
        w_btc = 1.0 / den
        w_eth = beta / den
        w = w_btc if pair == self._TRADED else w_eth
        stake = proposed_stake * w
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def _rolling_hedge_ratio(self, y: pd.Series, x: pd.Series, window: int) -> pd.Series:
        y_vals = y.values.astype(float)
        x_vals = x.values.astype(float)
        n = len(y_vals)
        betas = np.full(n, np.nan)
        for i in range(window - 1, n):
            y_w = y_vals[i - window + 1 : i + 1]
            x_w = x_vals[i - window + 1 : i + 1]
            if np.any(np.isnan(y_w)) or np.any(np.isnan(x_w)):
                continue
            x_mean = x_w.mean()
            y_mean = y_w.mean()
            x_demeaned = x_w - x_mean
            var_x = np.dot(x_demeaned, x_demeaned)
            if var_x < 1e-12:
                continue
            betas[i] = np.dot(x_demeaned, y_w - y_mean) / var_x
        return pd.Series(betas, index=y.index)
