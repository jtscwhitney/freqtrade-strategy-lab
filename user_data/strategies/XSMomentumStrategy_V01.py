# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
Cross-sectional momentum (Candidate G) — Phase 1 baseline.

**Registry (2026-03-29):** Candidate G is **PARKED** (empirically weak after Phase 1). Code retained; reopen only per `user_data/info/AlgoTrading_Research_Log.md` (Candidate G).

Ranks the futures whitelist by formation-period return on the base timeframe (1h),
goes long top-N winners and short bottom-N losers, rebalancing on a fixed calendar
grid aligned to holding length. Exits on holding-period time stop plus trailing stop.

Concrete variants (separate classes for backtest CLI):
    XSMomentumStrategy_V01_4h / _V01_1d — long/short (baseline, regime tilt **off**)
    XSMomentumStrategy_V02_4h / _V02_1d — long winners only (tilt **off**)
    XSMomentumStrategy_V03_4h / _V03_1d — V01 + **regime tilt on** (stake + leverage from BTC vol/trend; **fixed -12% stop**, startup 300)
    XSMomentumStrategy_V04_4h / _V04_1d — V02 + same tilt as V03
    XSMomentumStrategy_V03_1d_fair / _V04_1d_fair — **CLI aliases** for V03_1d / V04_1d (identical behavior)

Middle path: V01/V02 keep REGIME_TILT_ENABLED=False (control). V03/V04 set True — compare A/B after Phase 1 baseline.
See user_data/info/CrossSectionalMomentum_Deep_Dive.md Part 6.

See user_data/info/CrossSectionalMomentum_Dev_Plan.md and Phase 0 summary.

Backtest examples (repo root, PowerShell-friendly one line):

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V01_4h --timerange 20220101-20250101 --timeframe 1h --fee 0.0005

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V01_1d --timerange 20220101-20250101 --timeframe 1h --fee 0.0005

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V02_1d --timerange 20220101-20250101 --timeframe 1h --fee 0.0005

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V03_1d --timerange 20220101-20250101 --timeframe 1h --fee 0.0005
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timezone

from freqtrade.strategy import IStrategy
from freqtrade.persistence import Trade


class XSMomentumStrategy_V01(IStrategy):
    """
    Base cross-sectional momentum. Subclasses set FORMATION_CANDLES and HOLDING_CANDLES
    (1h bars): 4 = 4h, 24 = 1d.
    """

    timeframe = "1h"
    can_short = True

    # --- Risk / exits ---------------------------------------------------------
    minimal_roi = {"0": 100}
    stoploss = -0.12
    use_custom_stoploss = False
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.05
    trailing_only_offset_is_reached = True

    # --- Portfolio knobs ------------------------------------------------------
    TOP_N: int = 4
    BOTTOM_N: int = 4
    MIN_VALID_PAIRS: int = 15

    # Subclasses override (1h candles)
    FORMATION_CANDLES: int = 24
    HOLDING_CANDLES: int = 24

    # V02 sets True in subclasses
    long_only: bool = False

    startup_candle_count: int = 300

    # --- Regime tilt (middle path) — V01/V02: False (control). V03/V04: True. ----------
    # Continuous multipliers, not on/off gates. See CrossSectionalMomentum_Deep_Dive.md.
    REGIME_TILT_ENABLED: bool = False
    REGIME_BENCHMARK_PAIR: str = "BTC/USDT:USDT"
    REGIME_VOL_WINDOW: int = 168  # ~7d of 1h for realized vol
    REGIME_VOL_RATIO_WINDOW: int = 720  # ~30d context for vol ratio
    REGIME_STAKE_VOL_MIN: float = 0.85
    REGIME_STAKE_VOL_MAX: float = 1.0
    REGIME_TREND_BARS: int = 168  # BTC return lookback for bull/bear dial
    REGIME_TREND_TANH_SCALE: float = 40.0
    REGIME_SHORT_BULL_TILT: float = 0.12  # scale down short stake when BTC trend_sig > 0
    REGIME_LONG_BULL_BONUS: float = 0.05  # small boost to long stake in same condition
    REGIME_LEVERAGE_MIN: float = 0.85
    REGIME_LEVERAGE_MAX: float = 1.0
    REGIME_STOP_VOL_WIDEN: float = 0.03  # up to 3pp wider stop when vol ratio high

    # Cross-sectional cache (invalidated when chunk shape / end date changes)
    _sig_cache: tuple | None = None

    def informative_pairs(self) -> list[tuple[str, str]]:
        return [(p, self.timeframe) for p in self.dp.current_whitelist()]

    def _rebalance_mask_for_index(self, ix: pd.DatetimeIndex) -> np.ndarray:
        """True on bars where we allow new entries (UTC hour grid on 1h candles)."""
        hc = int(self.HOLDING_CANDLES)
        pix = pd.DatetimeIndex(ix)
        if pix.tz is None:
            pix = pix.tz_localize("UTC", ambiguous="infer", nonexistent="shift_forward")
        else:
            pix = pix.tz_convert("UTC")
        h = pix.hour.to_numpy(dtype=np.int32)
        if hc == 24:
            return h == 0
        if hc == 4:
            return (h % 4) == 0
        # Fallback: every hc-th bar in this slice (chunk-local)
        return (np.arange(len(ix)) % hc == 0)

    def _build_cross_sectional_signals(self, dates: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        """
        Returns (long_df, short_df, valid_count) indexed by date with one bool column per pair.
        """
        whitelist = list(self.dp.current_whitelist())
        if not whitelist:
            empty = pd.DataFrame(index=pd.DatetimeIndex([], tz="UTC"))
            return empty, empty, pd.Series(dtype=int)

        parts: list[pd.DataFrame] = []
        for p in whitelist:
            df = self.dp.get_pair_dataframe(pair=p, timeframe=self.timeframe)
            if df is None or df.empty:
                continue
            d = df[["date", "close"]].copy()
            d["date"] = pd.to_datetime(d["date"], utc=True)
            d = d.rename(columns={"close": p})
            parts.append(d)

        if not parts:
            empty = pd.DataFrame(index=pd.DatetimeIndex([], tz="UTC"))
            return empty, empty, pd.Series(dtype=int)

        merged = parts[0]
        for d in parts[1:]:
            merged = merged.merge(d, on="date", how="outer")
        merged = merged.sort_values("date").reset_index(drop=True)
        merged = merged.loc[merged["date"].isin(dates.unique())]

        price_cols = [c for c in whitelist if c in merged.columns]
        if len(price_cols) < self.MIN_VALID_PAIRS:
            idx = pd.DatetimeIndex(pd.to_datetime(merged["date"], utc=True))
            empty = pd.DataFrame(False, index=idx, columns=whitelist)
            return empty, empty, pd.Series(0, index=idx)

        closes = merged.set_index("date")[price_cols].sort_index()
        formation = closes.pct_change(periods=int(self.FORMATION_CANDLES), fill_method=None)
        valid_ct = formation.notna().sum(axis=1)
        ok = (valid_ct >= self.MIN_VALID_PAIRS).to_numpy(dtype=bool)[:, np.newaxis]

        r_hi = formation.rank(axis=1, ascending=False, method="first")
        r_lo = formation.rank(axis=1, ascending=True, method="first")
        long_mat = (r_hi <= self.TOP_N).to_numpy(dtype=bool) & ok
        short_mat = (r_lo <= self.BOTTOM_N).to_numpy(dtype=bool) & ok

        long_df = pd.DataFrame(long_mat, index=formation.index, columns=formation.columns)
        short_df = pd.DataFrame(short_mat, index=formation.index, columns=formation.columns)

        rb = self._rebalance_mask_for_index(pd.DatetimeIndex(formation.index))
        long_df = long_df.mul(rb, axis=0)
        short_df = short_df.mul(rb, axis=0)

        return long_df, short_df, valid_ct

    def _build_regime_frame(self, dates: pd.Series) -> pd.DataFrame:
        """BTC-based vol + trend dials → per-date multipliers (continuous, conservative bands)."""
        want = pd.DatetimeIndex(pd.to_datetime(dates.unique(), utc=True)).sort_values()
        df = self.dp.get_pair_dataframe(pair=self.REGIME_BENCHMARK_PAIR, timeframe=self.timeframe)
        if df is None or df.empty:
            return pd.DataFrame(
                {
                    "regime_long_stake_mult": 1.0,
                    "regime_short_stake_mult": 1.0,
                    "regime_leverage_mult": 1.0,
                    "regime_stoploss": float(self.stoploss),
                },
                index=want,
            )

        btc = df[["date", "close"]].copy()
        btc["date"] = pd.to_datetime(btc["date"], utc=True)
        close = btc.set_index("date").sort_index()["close"].astype(float)
        rets = close.pct_change(fill_method=None)
        vw = int(self.REGIME_VOL_WINDOW)
        rw = int(self.REGIME_VOL_RATIO_WINDOW)
        vol_roll = rets.rolling(vw, min_periods=max(vw // 3, 10)).std()
        med = vol_roll.rolling(rw, min_periods=50).median()
        ratio = (vol_roll / (med + 1e-12)).clip(0.5, 2.5)
        sv_span = float(self.REGIME_STAKE_VOL_MAX - self.REGIME_STAKE_VOL_MIN)
        stake_vol_mult = (
            float(self.REGIME_STAKE_VOL_MAX) - sv_span * ((ratio - 0.5) / 2.0)
        ).clip(float(self.REGIME_STAKE_VOL_MIN), float(self.REGIME_STAKE_VOL_MAX))

        tb = int(self.REGIME_TREND_BARS)
        trend_mom = close.pct_change(tb, fill_method=None)
        trend_sig = np.tanh(trend_mom.fillna(0.0) * float(self.REGIME_TREND_TANH_SCALE))
        bull = trend_sig.clip(lower=0.0)

        long_mult = stake_vol_mult * (1.0 + float(self.REGIME_LONG_BULL_BONUS) * bull)
        short_mult = stake_vol_mult * (1.0 - float(self.REGIME_SHORT_BULL_TILT) * bull)
        long_mult = long_mult.clip(0.75, 1.12)
        short_mult = short_mult.clip(0.75, 1.0)
        lev_mult = stake_vol_mult.clip(float(self.REGIME_LEVERAGE_MIN), float(self.REGIME_LEVERAGE_MAX))

        widen = (float(self.REGIME_STOP_VOL_WIDEN) * ((ratio - 0.5) / 2.0)).clip(
            lower=0.0, upper=float(self.REGIME_STOP_VOL_WIDEN)
        )
        # More negative = wider stop. Cap widening at ~10pp beyond base stoploss.
        regime_stop = (float(self.stoploss) - widen).clip(lower=-0.22, upper=float(self.stoploss))

        regime = pd.DataFrame(
            {
                "regime_long_stake_mult": long_mult,
                "regime_short_stake_mult": short_mult,
                "regime_leverage_mult": lev_mult,
                "regime_stoploss": regime_stop,
            },
            index=close.index,
        )
        aligned = regime.reindex(want)
        aligned["regime_long_stake_mult"] = aligned["regime_long_stake_mult"].ffill().bfill().fillna(1.0)
        aligned["regime_short_stake_mult"] = aligned["regime_short_stake_mult"].ffill().bfill().fillna(1.0)
        aligned["regime_leverage_mult"] = aligned["regime_leverage_mult"].ffill().bfill().fillna(1.0)
        aligned["regime_stoploss"] = aligned["regime_stoploss"].ffill().bfill().fillna(float(self.stoploss))
        return aligned

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        if dataframe.empty:
            return dataframe

        dates = dataframe["date"]
        cache_key = (
            len(dataframe),
            dates.iloc[-1],
            self.FORMATION_CANDLES,
            self.HOLDING_CANDLES,
            self.long_only,
            self.TOP_N,
            self.BOTTOM_N,
            self.REGIME_TILT_ENABLED,
        )
        if self._sig_cache is None or self._sig_cache[0] != cache_key:
            long_w, short_w, _vc = self._build_cross_sectional_signals(dates)
            regime_df = self._build_regime_frame(dates) if self.REGIME_TILT_ENABLED else None
            self._sig_cache = (cache_key, long_w, short_w, regime_df)

        _, long_w, short_w, regime_df = self._sig_cache

        d_utc = pd.to_datetime(dataframe["date"], utc=True)
        idx = pd.DatetimeIndex(d_utc)
        if pair not in long_w.columns:
            dataframe["xs_long"] = 0
            dataframe["xs_short"] = 0
            return dataframe

        # reindex signals to this pair's rows (left join on date)
        lcol = long_w[pair].reindex(idx, fill_value=0).to_numpy(dtype=float)
        scol = short_w[pair].reindex(idx, fill_value=0).to_numpy(dtype=float)
        dataframe["xs_long"] = lcol.astype(np.int8)
        dataframe["xs_short"] = scol.astype(np.int8)

        if regime_df is not None:
            dataframe["regime_long_stake_mult"] = (
                regime_df["regime_long_stake_mult"].reindex(idx).ffill().bfill().fillna(1.0).to_numpy()
            )
            dataframe["regime_short_stake_mult"] = (
                regime_df["regime_short_stake_mult"].reindex(idx).ffill().bfill().fillna(1.0).to_numpy()
            )
            dataframe["regime_leverage_mult"] = (
                regime_df["regime_leverage_mult"].reindex(idx).ffill().bfill().fillna(1.0).to_numpy()
            )
            dataframe["regime_stoploss"] = (
                regime_df["regime_stoploss"]
                .reindex(idx)
                .ffill()
                .bfill()
                .fillna(float(self.stoploss))
                .to_numpy(dtype=float)
            )
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        vol = dataframe["volume"] > 0
        dataframe.loc[vol & (dataframe["xs_long"] > 0), "enter_long"] = 1
        if not self.long_only and self.can_short:
            dataframe.loc[vol & (dataframe["xs_short"] > 0), "enter_short"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> str | None:
        open_utc = getattr(trade, "open_date_utc", None) or getattr(trade, "open_date", None)
        if open_utc is None:
            return None
        if open_utc.tzinfo is None:
            open_utc = open_utc.replace(tzinfo=timezone.utc)
        hold_h = (current_time.replace(tzinfo=timezone.utc) - open_utc).total_seconds() / 3600.0
        if hold_h >= float(self.HOLDING_CANDLES):
            return "time_stop"
        return None

    def _regime_row_at(self, pair: str, current_time: datetime) -> pd.Series | None:
        if not self.REGIME_TILT_ENABLED:
            return None
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return None
        ct = current_time
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)
        else:
            ct = ct.astimezone(timezone.utc)
        tcol = pd.to_datetime(df["date"], utc=True)
        mask = tcol <= ct
        if not mask.any():
            return None
        return df.loc[mask].iloc[-1]

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
        if not self.REGIME_TILT_ENABLED:
            return proposed_stake
        row = self._regime_row_at(pair, current_time)
        if row is None:
            return proposed_stake
        if side == "short":
            mult = float(row.get("regime_short_stake_mult", 1.0))
        else:
            mult = float(row.get("regime_long_stake_mult", 1.0))
        scaled = proposed_stake * mult
        lo = float(min_stake) if min_stake is not None else 0.0
        return max(lo, min(scaled, float(max_stake)))

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
        base = min(3.0, float(max_leverage))
        if not self.REGIME_TILT_ENABLED:
            return base
        row = self._regime_row_at(pair, current_time)
        if row is None:
            return base
        mult = float(row.get("regime_leverage_mult", 1.0))
        out = base * mult
        return max(1.0, min(out, float(max_leverage)))

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        if not self.REGIME_TILT_ENABLED:
            return self.stoploss
        row = self._regime_row_at(pair, current_time)
        if row is None:
            return self.stoploss
        return float(row.get("regime_stoploss", self.stoploss))


class XSMomentumStrategy_V01_4h(XSMomentumStrategy_V01):
    FORMATION_CANDLES = 4
    HOLDING_CANDLES = 4


class XSMomentumStrategy_V01_1d(XSMomentumStrategy_V01):
    FORMATION_CANDLES = 24
    HOLDING_CANDLES = 24


class XSMomentumStrategy_V02_4h(XSMomentumStrategy_V01_4h):
    long_only = True
    can_short = False


class XSMomentumStrategy_V02_1d(XSMomentumStrategy_V01_1d):
    long_only = True
    can_short = False


# --- Regime tilt on (compare A/B vs V01/V02 after baseline Phase 1) -----------------


class XSMomentumStrategy_V03_4h(XSMomentumStrategy_V01_4h):
    """V01_4h + stake/leverage regime tilt. Fixed stoploss (-12%); no vol-widened custom_stop."""

    REGIME_TILT_ENABLED = True


class XSMomentumStrategy_V03_1d(XSMomentumStrategy_V01_1d):
    """V01_1d + stake/leverage regime tilt. Fixed stoploss (-12%); no vol-widened custom_stop."""

    REGIME_TILT_ENABLED = True


class XSMomentumStrategy_V04_4h(XSMomentumStrategy_V02_4h):
    REGIME_TILT_ENABLED = True


class XSMomentumStrategy_V04_1d(XSMomentumStrategy_V02_1d):
    REGIME_TILT_ENABLED = True


# --- CLI aliases (identical to V03/V04; kept for older commands and docs) ------------


class XSMomentumStrategy_V03_1d_fair(XSMomentumStrategy_V03_1d):
    """Alias of V03_1d."""

    pass


class XSMomentumStrategy_V04_1d_fair(XSMomentumStrategy_V04_1d):
    """Alias of V04_1d."""

    pass
