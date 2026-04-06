# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
Ensemble Donchian V02 — pure **1d** timeframe (signal and execution both daily).

Same paper lookbacks and logic as V01, but Donchian + ensemble are computed on the
native base dataframe (no merge from informative). Use to compare **hybrid 1d/1h**
(V01) vs **fully daily** execution (fee churn, alignment).

Backtest:

    docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V02 --timerange 20220101-20250101 --timeframe 1d --fee 0.0005 --cache none

See EnsembleDonchianTrend_Deep_Dive.md / Dev_Plan.md.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pandas import DataFrame

from EnsembleDonchianStrategy_V01 import EnsembleDonchianStrategy_V01


class EnsembleDonchianStrategy_V02(EnsembleDonchianStrategy_V01):
    """Daily-only: Donchian on `1d` base OHLCV (inherits risk, exits, sizing pattern)."""

    timeframe = "1d"
    DONCHIAN_TIMEFRAME: str = "1d"
    VOL_SCALING_WINDOW: int = 21  # ~1 month of daily returns
    # No extra pre-window fetch: on-disk data often starts at 2022-01-01; requiring
    # 400+ days *before* the backtest timerange would empty short regime slices.
    # Longest Donchian still warms up via rolling `min_periods` (NaN until enough bars).
    startup_candle_count: int = 0

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        if dataframe.empty:
            return dataframe

        dates = dataframe["date"]
        cache_key = (
            len(dataframe),
            dates.iloc[-1],
            self.LOOKBACK_DAYS,
            "native_1d",
            self.VOL_SCALING_WINDOW,
        )
        if self._vol_cache is None or self._vol_cache[0] != cache_key:
            vol_mult = self._build_vol_stake_mult(dates)
            self._vol_cache = (cache_key, vol_mult)
        _, vol_mult = self._vol_cache

        h = dataframe["high"].astype(float)
        lo = dataframe["low"].astype(float)
        cl = dataframe["close"].astype(float)

        if len(dataframe) < max(self.LOOKBACK_DAYS) + 2:
            for N in self.LOOKBACK_DAYS:
                dataframe[f"sig_{N}"] = np.nan
                dataframe[f"dc_lower_{N}"] = np.nan
            dataframe["ensemble_score"] = np.nan
            dataframe["trail_n_active_min"] = np.nan
        else:
            valid_row = np.ones(len(dataframe), dtype=bool)
            sig_parts: list[np.ndarray] = []
            for N in self.LOOKBACK_DAYS:
                upper = h.rolling(int(N), min_periods=int(N)).max().shift(1)
                valid_row &= upper.notna().to_numpy()
                sig = ((cl > upper) & upper.notna()).astype(np.float64)
                dataframe[f"sig_{N}"] = sig
                sig_parts.append(sig.to_numpy(dtype=float))
                dataframe[f"dc_lower_{N}"] = lo.rolling(int(N), min_periods=int(N)).min().shift(1)

            sig_mat = np.column_stack(sig_parts)
            dataframe["ensemble_score"] = np.where(valid_row, sig_mat.mean(axis=1), np.nan)

            trail_n = np.full(len(dataframe), np.nan)
            look = np.array(self.LOOKBACK_DAYS, dtype=float)
            for i in range(len(dataframe)):
                if not valid_row[i]:
                    continue
                active = look[sig_mat[i, :] > 0.5]
                if active.size:
                    trail_n[i] = float(active.min())
            dataframe["trail_n_active_min"] = trail_n

        prev_close = cl.shift(1)
        tr = pd.concat(
            [
                (h - lo).abs(),
                (h - prev_close).abs(),
                (lo - prev_close).abs(),
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


class EnsembleDonchianStrategy_V02_ATR(EnsembleDonchianStrategy_V02):
    TRAILING_STOP_METHOD = "atr"
