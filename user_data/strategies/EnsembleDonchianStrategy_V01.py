# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
Ensemble Donchian trend-following (Candidate J) — Phase 1 MVP.

Long-only: multiple Donchian lookbacks vote breakout (close > prior upper band);
ensemble score is the mean vote rate. Enter when score > threshold; exit via
trailing stop (Donchian lower on shortest active lookback at entry, or ATR
trailing) plus hard stoploss and time stop. Inverse-vol position sizing across
the futures whitelist (same pattern as Candidate G).

See user_data/info/EnsembleDonchianTrend_Deep_Dive.md and
EnsembleDonchianTrend_Dev_Plan.md.

Backtest (repo root, PowerShell one line). Requires 1h + 1d futures data for
whitelisted pairs (e.g. ``download-data --timeframes 1h 1d``).

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V01 --timerange 20220101-20250101 --timeframe 1h --fee 0.0005 --export trades

ATR trailing variant:

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V01_ATR --timerange 20220101-20250101 --timeframe 1h --fee 0.0005
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, merge_informative_pair


class EnsembleDonchianStrategy_V01(IStrategy):
    """Ensemble Donchian V01 — Donchian-lower trailing stop (ratcheted)."""

    timeframe = "1h"
    # Paper uses calendar-day Donchian windows; implement on 1d and merge to 1h
    # so startup limits on 1h (~2494 bars) do not cap lookbacks at ~100 days.
    DONCHIAN_TIMEFRAME: str = "1d"
    can_short = False

    # --- Risk -----------------------------------------------------------------
    minimal_roi = {"0": 100}
    stoploss = -0.12
    use_custom_stoploss = True
    trailing_stop = False

    # --- Donchian ensemble (paper: 5–360 calendar days) ----------------------
    LOOKBACK_DAYS: tuple[int, ...] = (5, 10, 20, 30, 60, 90, 150, 250, 360)
    ENTRY_THRESHOLD: float = 0.5

    # "donchian_lower" | "atr"
    TRAILING_STOP_METHOD: str = "donchian_lower"
    ATR_PERIOD: int = 14
    ATR_MULTIPLIER: float = 3.0

    VOL_SCALING_WINDOW: int = 168  # ~7d of 1h
    VOL_SCALING_FLOOR: float = 0.5
    VOL_SCALING_CAP: float = 2.0

    TIME_STOP_HOURS: float = 720.0  # 30d backup

    process_only_new_candles = True
    # Only 1h indicators (vol, ATR) need a modest warm-up; Donchian runs on 1d.
    startup_candle_count: int = 400

    # Per-pair state (single position per pair in futures)
    _pair_entry_trail_n: dict[str, int] = {}
    _pair_ratched_stop: dict[str, float] = {}

    # Cached (vol mult crosses pairs on same chunk)
    _vol_cache: tuple | None = None

    def informative_pairs(self):
        tf = self.DONCHIAN_TIMEFRAME
        return [(p, tf) for p in self.dp.current_whitelist()]

    def _build_vol_stake_mult(self, dates: pd.Series) -> pd.DataFrame:
        """Per-date × per-pair vol stake multiplier (median vol / pair vol), clipped."""
        whitelist = list(self.dp.current_whitelist())
        if not whitelist:
            return pd.DataFrame()

        vol_series: dict[str, pd.Series] = {}
        w = int(self.VOL_SCALING_WINDOW)
        for p in whitelist:
            df = self.dp.get_pair_dataframe(pair=p, timeframe=self.timeframe)
            if df is None or df.empty:
                continue
            d = df[["date", "close"]].copy()
            d["date"] = pd.to_datetime(d["date"], utc=True)
            d = d.sort_values("date")
            rets = d["close"].pct_change(fill_method=None)
            d["vol"] = rets.rolling(w, min_periods=max(w // 3, 10)).std()
            vol_series[p] = d.set_index("date")["vol"]

        if not vol_series:
            return pd.DataFrame()

        vol_df = pd.DataFrame(vol_series).sort_index()
        med = vol_df.median(axis=1).replace(0.0, np.nan)
        mult = vol_df.rdiv(med, axis=0)  # med / vol_asset
        mult = mult.clip(float(self.VOL_SCALING_FLOOR), float(self.VOL_SCALING_CAP))
        mult = mult.where(vol_df.notna())
        want = pd.DatetimeIndex(pd.to_datetime(dates.unique(), utc=True)).sort_values()
        return mult.reindex(want).ffill().bfill()

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        if dataframe.empty:
            return dataframe

        dates = dataframe["date"]
        cache_key = (
            len(dataframe),
            dates.iloc[-1],
            self.LOOKBACK_DAYS,
            self.DONCHIAN_TIMEFRAME,
            self.VOL_SCALING_WINDOW,
        )
        if self._vol_cache is None or self._vol_cache[0] != cache_key:
            vol_mult = self._build_vol_stake_mult(dates)
            self._vol_cache = (cache_key, vol_mult)
        _, vol_mult = self._vol_cache

        h1 = dataframe["high"].astype(float)
        lo1 = dataframe["low"].astype(float)
        cl1 = dataframe["close"].astype(float)

        dtf = self.DONCHIAN_TIMEFRAME
        inf = self.dp.get_pair_dataframe(pair=pair, timeframe=dtf)
        if inf is None or inf.empty or len(inf) < max(self.LOOKBACK_DAYS) + 2:
            for N in self.LOOKBACK_DAYS:
                dataframe[f"sig_{N}"] = np.nan
                dataframe[f"dc_lower_{N}"] = np.nan
            dataframe["ensemble_score"] = np.nan
            dataframe["trail_n_active_min"] = np.nan
        else:
            inf = inf.copy()
            h = inf["high"].astype(float)
            lo = inf["low"].astype(float)
            cl = inf["close"].astype(float)

            valid_row = np.ones(len(inf), dtype=bool)
            sig_parts: list[np.ndarray] = []
            for N in self.LOOKBACK_DAYS:
                upper = h.rolling(int(N), min_periods=int(N)).max().shift(1)
                valid_row &= upper.notna().to_numpy()
                sig = ((cl > upper) & upper.notna()).astype(np.float64)
                inf[f"sig_{N}"] = sig
                sig_parts.append(sig.to_numpy(dtype=float))
                inf[f"dc_lower_{N}"] = lo.rolling(int(N), min_periods=int(N)).min().shift(1)

            sig_mat = np.column_stack(sig_parts)
            inf["ensemble_score"] = np.where(valid_row, sig_mat.mean(axis=1), np.nan)

            trail_n = np.full(len(inf), np.nan)
            look = np.array(self.LOOKBACK_DAYS, dtype=float)
            for i in range(len(inf)):
                if not valid_row[i]:
                    continue
                active = look[sig_mat[i, :] > 0.5]
                if active.size:
                    trail_n[i] = float(active.min())
            inf["trail_n_active_min"] = trail_n

            suffix = f"_{dtf}"
            merged = merge_informative_pair(
                dataframe,
                inf,
                self.timeframe,
                dtf,
                ffill=True,
            )
            dataframe = merged
            dataframe["ensemble_score"] = dataframe[f"ensemble_score{suffix}"]
            dataframe["trail_n_active_min"] = dataframe[f"trail_n_active_min{suffix}"]
            for N in self.LOOKBACK_DAYS:
                dataframe[f"sig_{N}"] = dataframe[f"sig_{N}{suffix}"]
                dataframe[f"dc_lower_{N}"] = dataframe[f"dc_lower_{N}{suffix}"]

        # ATR (for ATR trailing) — 1h
        prev_close = cl1.shift(1)
        tr = pd.concat(
            [
                (h1 - lo1).abs(),
                (h1 - prev_close).abs(),
                (lo1 - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        dataframe["atr"] = tr.rolling(int(self.ATR_PERIOD), min_periods=self.ATR_PERIOD).mean()

        d_utc = pd.to_datetime(dataframe["date"], utc=True)
        idx = pd.DatetimeIndex(d_utc)
        if not vol_mult.empty and pair in vol_mult.columns:
            vm = vol_mult[pair].reindex(idx).ffill().bfill().fillna(1.0).to_numpy(dtype=float)
        else:
            vm = np.ones(len(dataframe), dtype=float)
        dataframe["vol_stake_mult"] = vm

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        vol = dataframe["volume"] > 0
        ok = vol & (dataframe["ensemble_score"] > float(self.ENTRY_THRESHOLD))
        ok = ok & dataframe["ensemble_score"].notna()
        ok = ok & dataframe["trail_n_active_min"].notna()
        dataframe.loc[ok, "enter_long"] = 1
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
        """Record shortest active lookback for Donchian trailing stop."""
        if side != "long":
            return True
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return True
        ct = current_time.replace(tzinfo=timezone.utc) if current_time.tzinfo is None else current_time.astimezone(timezone.utc)
        tcol = pd.to_datetime(df["date"], utc=True)
        mask = tcol <= ct
        if not mask.any():
            return True
        row = df.loc[mask].iloc[-1]
        tn = row.get("trail_n_active_min", np.nan)
        if tn is not None and not (isinstance(tn, float) and math.isnan(tn)):
            self._pair_entry_trail_n[pair] = int(tn)
        else:
            self._pair_entry_trail_n[pair] = int(min(self.LOOKBACK_DAYS))
        self._pair_ratched_stop.pop(pair, None)
        return True

    def _cleanup_pair_state(self) -> None:
        open_pairs = {t.pair for t in Trade.get_open_trades()}
        for p in list(self._pair_entry_trail_n.keys()):
            if p not in open_pairs:
                self._pair_entry_trail_n.pop(p, None)
                self._pair_ratched_stop.pop(p, None)

    def bot_loop_start(self, current_time: datetime, **kwargs) -> None:
        self._cleanup_pair_state()

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
        if hold_h >= float(self.TIME_STOP_HOURS):
            return "time_stop_donchian"
        return None

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
        row = self._row_at(pair, current_time)
        if row is None:
            return proposed_stake
        mult = float(row.get("vol_stake_mult", 1.0))
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
        return min(2.0, float(max_leverage))

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

        if self.TRAILING_STOP_METHOD == "atr":
            atr = float(row.get("atr", 0.0) or 0.0)
            peak = float(getattr(trade, "max_rate", None) or current_rate)
            stop_price = peak - float(self.ATR_MULTIPLIER) * atr
            base_sl = (stop_price - current_rate) / max(current_rate, 1e-12)
            return max(base_sl, float(self.stoploss))

        n = self._pair_entry_trail_n.get(pair, int(min(self.LOOKBACK_DAYS)))
        col = f"dc_lower_{n}"
        raw = row.get(col, np.nan)
        if raw is None or (isinstance(raw, float) and (math.isnan(raw) or np.isnan(raw))):
            return self.stoploss
        stop_price = float(raw)
        prev = self._pair_ratched_stop.get(pair, stop_price)
        stop_price = max(stop_price, prev)
        self._pair_ratched_stop[pair] = stop_price

        base_sl = (stop_price - current_rate) / max(current_rate, 1e-12)
        # Freqtrade: negative = below price; cap to hard stoploss (more negative = wider)
        return max(base_sl, float(self.stoploss))


class EnsembleDonchianStrategy_V01_ATR(EnsembleDonchianStrategy_V01):
    """Same ensemble entries; ATR trailing from peak since open."""

    TRAILING_STOP_METHOD = "atr"


# --- Phase 0 threshold grid (one class per value so the strategy resolver can load them)
class EnsembleDonchianStrategy_V01_Entry030(EnsembleDonchianStrategy_V01):
    ENTRY_THRESHOLD = 0.3


class EnsembleDonchianStrategy_V01_Entry070(EnsembleDonchianStrategy_V01):
    ENTRY_THRESHOLD = 0.7


class EnsembleDonchianStrategy_V01_Entry090(EnsembleDonchianStrategy_V01):
    ENTRY_THRESHOLD = 0.9


class EnsembleDonchianStrategy_V01_LookbackAblated(EnsembleDonchianStrategy_V01):
    """Same as V01 but drop 150/250/360d — shorter effective ensemble."""

    LOOKBACK_DAYS: tuple[int, ...] = (5, 10, 20, 30, 60, 90)


class EnsembleDonchianStrategy_V01_LookbackAblated_ATR(EnsembleDonchianStrategy_V01_LookbackAblated):
    TRAILING_STOP_METHOD = "atr"
