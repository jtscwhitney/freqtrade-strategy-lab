# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
CointPairsStrategy_V01 — Phase 1 Backtest: Single-Leg Mean Reversion on ETH/BTC Spread

Architecture:
    - Load BTC/USDT:USDT as 1h informative pair.
    - Compute rolling OLS hedge ratio (β) from ETH ~ β * BTC.
    - Spread = ETH_close - β * BTC_close.
    - Z-score = (spread - rolling_mean) / rolling_std over ZSCORE_WINDOW.
    - Enter LONG  ETH when z < -ENTRY_ZSCORE (ETH underpriced vs BTC equilibrium).
    - Enter SHORT ETH when z >  ENTRY_ZSCORE (ETH overpriced vs BTC equilibrium).
    - Exit when z-score reverts within EXIT_ZSCORE of zero.
    - CRISIS gate: block entries when ATR(14) > rolling-200-period p90 (same as LiqCascade).
    - Hard stoploss: -8% from entry.
    - Time stop: MAX_HOLD_CANDLES (72h).

Phase plan:
    V01: Single-leg ETH, rolling OLS hedge ratio — validates signal before adding BTC hedge.
    V02: Dual-leg coordination — add simultaneous BTC hedge leg.
    V03: Kalman filter hedge ratio (dynamic β adapts continuously).

See user_data/info/CointPairsTrading_Deep_Dive.md for full design rationale.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime

import talib.abstract as ta

from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.persistence import Trade


class CointPairsStrategy_V01(IStrategy):
    """Single-leg cointegration mean-reversion on ETH using BTC as the spread anchor."""

    # ── Timeframe ────────────────────────────────────────────────────────────
    timeframe = "1h"
    inf_tf = "1h"

    # ── Capital & risk ───────────────────────────────────────────────────────
    # Primary exit is z-score reversion — ROI disabled.
    minimal_roi = {"0": 100}
    stoploss = -0.08  # 8% safety net for spread divergence / cointegration breakdown
    use_custom_stoploss = False

    # ── Features ─────────────────────────────────────────────────────────────
    can_short = True
    startup_candle_count: int = 900  # > OLS_WINDOW + ZSCORE_WINDOW + margin

    # ── Strategy parameters (candidates for Hyperopt in Phase 4) ─────────────
    # Z-score entry/exit thresholds
    ENTRY_ZSCORE: float = 2.0
    EXIT_ZSCORE: float = 0.5

    # Rolling OLS window for hedge ratio (candles at 1h = days * 24)
    OLS_WINDOW: int = 720   # 30 days

    # Rolling z-score normalisation window
    ZSCORE_WINDOW: int = 720  # 30 days

    # CRISIS gate: ATR rolling window for p90 threshold
    CRISIS_ATR_WINDOW: int = 200

    # Time stop
    MAX_HOLD_CANDLES: int = 72  # 3 days at 1h

    # ── Informative pair ─────────────────────────────────────────────────────
    def informative_pairs(self) -> list[tuple[str, str]]:
        """Declare BTC/USDT:USDT at 1h as the spread anchor."""
        return [("BTC/USDT:USDT", self.inf_tf)]

    # ── Indicators ───────────────────────────────────────────────────────────
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Compute hedge ratio, spread, z-score, and CRISIS gate."""
        # ── BTC informative data ──────────────────────────────────────────────
        btc_df = self.dp.get_pair_dataframe("BTC/USDT:USDT", self.inf_tf)
        if btc_df.empty:
            dataframe["z_score"] = np.nan
            dataframe["crisis"] = 1
            return dataframe

        btc_df = btc_df[["date", "close"]].rename(columns={"close": "btc_close"})
        dataframe = merge_informative_pair(
            dataframe, btc_df, self.timeframe, self.inf_tf,
            ffill=True, date_column="date",
        )
        btc_col = f"btc_close_{self.inf_tf}"

        # ── Rolling OLS hedge ratio ───────────────────────────────────────────
        dataframe["hedge_ratio"] = self._rolling_hedge_ratio(
            y=dataframe["close"],
            x=dataframe[btc_col],
            window=self.OLS_WINDOW,
        )

        # ── Spread ────────────────────────────────────────────────────────────
        dataframe["spread"] = dataframe["close"] - dataframe["hedge_ratio"] * dataframe[btc_col]

        # ── Z-score ───────────────────────────────────────────────────────────
        spread_mean = dataframe["spread"].rolling(self.ZSCORE_WINDOW).mean()
        spread_std = dataframe["spread"].rolling(self.ZSCORE_WINDOW).std()
        # Avoid division by zero in flat market conditions
        spread_std = spread_std.replace(0, np.nan)
        dataframe["z_score"] = (dataframe["spread"] - spread_mean) / spread_std

        # ── CRISIS gate (same approach as LiqCascade) ─────────────────────────
        atr14 = ta.ATR(dataframe, timeperiod=14)
        atr_p90 = atr14.rolling(self.CRISIS_ATR_WINDOW).quantile(0.90)
        dataframe["crisis"] = (atr14 > atr_p90).astype(int)

        return dataframe

    # ── Entry ─────────────────────────────────────────────────────────────────
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Enter on z-score extremes when CRISIS gate is clear."""
        not_crisis = dataframe["crisis"] == 0
        has_signal = dataframe["z_score"].notna()

        # Long: ETH underperforms BTC by ENTRY_ZSCORE standard deviations
        dataframe.loc[
            not_crisis & has_signal
            & (dataframe["z_score"] < -self.ENTRY_ZSCORE)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: ETH outperforms BTC by ENTRY_ZSCORE standard deviations
        dataframe.loc[
            not_crisis & has_signal
            & (dataframe["z_score"] > self.ENTRY_ZSCORE)
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    # ── Exit ──────────────────────────────────────────────────────────────────
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Exit when z-score reverts within EXIT_ZSCORE of zero."""
        has_signal = dataframe["z_score"].notna()

        # Exit long: spread has reverted upward — z no longer deeply negative
        dataframe.loc[
            has_signal & (dataframe["z_score"] > -self.EXIT_ZSCORE),
            "exit_long",
        ] = 1

        # Exit short: spread has reverted downward — z no longer deeply positive
        dataframe.loc[
            has_signal & (dataframe["z_score"] < self.EXIT_ZSCORE),
            "exit_short",
        ] = 1

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
        """Time stop: exit if trade has not reverted within MAX_HOLD_CANDLES."""
        trade_duration_candles = int(
            (current_time - trade.open_date_utc).total_seconds() / 3600
        )
        if trade_duration_candles >= self.MAX_HOLD_CANDLES:
            return "time_stop"
        return None

    # ── Leverage ──────────────────────────────────────────────────────────────
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
        """Fixed 2x leverage. Single-leg (no BTC hedge) warrants conservative sizing."""
        return min(2.0, max_leverage)

    # ── Helper: rolling OLS ───────────────────────────────────────────────────
    def _rolling_hedge_ratio(
        self, y: pd.Series, x: pd.Series, window: int
    ) -> pd.Series:
        """Compute rolling OLS hedge ratio β where y ≈ β * x.

        Uses the direct covariance/variance formula (numerically equivalent to OLS
        without intercept on demeaned series). O(n * window) — acceptable for 1h data.

        Args:
            y: ETH close price series.
            x: BTC close price series (same index).
            window: Lookback window in candles.

        Returns:
            Series of hedge ratios, NaN for the first (window - 1) rows.
        """
        y_vals = y.values.astype(float)
        x_vals = x.values.astype(float)
        n = len(y_vals)
        betas = np.full(n, np.nan)

        for i in range(window - 1, n):
            y_w = y_vals[i - window + 1 : i + 1]
            x_w = x_vals[i - window + 1 : i + 1]

            # Skip windows with any NaN values
            if np.any(np.isnan(y_w)) or np.any(np.isnan(x_w)):
                continue

            x_mean = x_w.mean()
            y_mean = y_w.mean()
            x_demeaned = x_w - x_mean
            var_x = np.dot(x_demeaned, x_demeaned)

            if var_x < 1e-12:
                # BTC price flat — cannot compute meaningful hedge ratio
                continue

            betas[i] = np.dot(x_demeaned, y_w - y_mean) / var_x

        return pd.Series(betas, index=y.index)
