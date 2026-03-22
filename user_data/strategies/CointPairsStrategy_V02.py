# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa
"""
CointPairsStrategy_V02 — Phase 1 Backtest: Single-Leg Mean Reversion on BNB/ETH Spread (4h)

Phase 0 finding: BNB/ETH@4h is the only GO pair (6/8 checks). Key properties:
    - Hurst H = 0.251 (strong ratio mean reversion)
    - Rolling β stable: std=0.229 (STABLE — only pair below 0.30 threshold)
    - P(reversion within 1440h) = 27% — adequate for 60-day hold window
    - Fee sweep: ez=3.0, xz=0.5, ZSCORE=84c — net=168bps, ts=0% over 2022-2025
    - EG/Johansen both FAIL universally — no formal cointegration. Trading Hurst
      ratio mean reversion, not a cointegrated spread. β stability is the
      foundational evidence, not formal cointegration tests.

Architecture:
    - Load ETH/USDT:USDT as 4h informative pair (spread anchor).
    - Compute rolling OLS hedge ratio (β) from log(BNB) ~ β * log(ETH).
    - Spread = log(BNB) - β * log(ETH)  [log-price spread, more stable than dollar].
    - Z-score = (spread - rolling_mean) / rolling_std over ZSCORE_WINDOW.
    - Enter LONG  BNB when z < -ENTRY_ZSCORE (BNB underpriced vs ETH equilibrium).
    - Enter SHORT BNB when z >  ENTRY_ZSCORE (BNB overpriced vs ETH equilibrium).
    - Exit when z-score reverts within EXIT_ZSCORE of zero.
    - CRISIS gate: block entries when ATR(14) > rolling-200-period p90.
    - Hard stoploss: -8% from entry.
    - Time stop: MAX_HOLD_CANDLES (360 candles = 60 days at 4h).

Phase plan:
    V01: ETH/BTC@1h design — superseded by Phase 0 results.
    V02 (this): BNB/ETH@4h — Phase 0 GO pair. Single-leg BNB. Validates signal.
    V03: Dual-leg BNB/ETH — add simultaneous ETH hedge leg.
    V04: Kalman filter hedge ratio (dynamic β adapts continuously).

See user_data/info/CointPairsTrading_Deep_Dive.md for full design rationale and Phase 0 results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime

import talib.abstract as ta

from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.persistence import Trade


class CointPairsStrategy_V02(IStrategy):
    """Single-leg ratio mean reversion on BNB using ETH as the spread anchor (4h)."""

    # ── Timeframe ────────────────────────────────────────────────────────────
    timeframe = "4h"
    inf_tf = "4h"

    # ── Capital & risk ───────────────────────────────────────────────────────
    # Primary exit is z-score reversion — ROI disabled.
    minimal_roi = {"0": 100}
    stoploss = -0.25  # Widened from -0.08 — at 2x leverage, -8% fires on 4% BNB moves
    # which are routine at 4h. -25% = -12.5% on underlying, survives normal
    # spread oscillation while still protecting against β breakdown events.
    use_custom_stoploss = False

    # ── Features ─────────────────────────────────────────────────────────────
    can_short = True
    startup_candle_count: int = 400  # > OLS_WINDOW + ZSCORE_WINDOW + margin

    # ── Strategy parameters (candidates for Hyperopt in Phase 4) ─────────────
    # Phase 0 best config: ez=3.0, xz=0.5, ZSCORE=84c — net=168bps, ts=0%
    # Also run ez=2.0 to generate more trades for statistical evaluation.
    ENTRY_ZSCORE: float = 2.0   # lower than Phase 0 best to increase trade count
    EXIT_ZSCORE: float = 0.5

    # Rolling OLS window for hedge ratio (candles at 4h: 30d × 6 = 180)
    OLS_WINDOW: int = 180   # 30 days at 4h

    # Rolling z-score normalisation window (14d × 6 = 84 — best from Phase 0)
    ZSCORE_WINDOW: int = 84  # 14 days at 4h

    # CRISIS gate: ATR rolling window for p90 threshold
    CRISIS_ATR_WINDOW: int = 200

    # Time stop: 60 days at 4h = 360 candles
    MAX_HOLD_CANDLES: int = 360  # 60 days — must be large enough for ratio to revert

    # ── Informative pair ─────────────────────────────────────────────────────
    def informative_pairs(self) -> list[tuple[str, str]]:
        """Declare ETH/USDT:USDT at 4h as the spread anchor."""
        return [("ETH/USDT:USDT", self.inf_tf)]

    # ── Indicators ───────────────────────────────────────────────────────────
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Compute log-price hedge ratio, spread, z-score, and CRISIS gate."""
        # ── ETH informative data ──────────────────────────────────────────────
        eth_df = self.dp.get_pair_dataframe("ETH/USDT:USDT", self.inf_tf)
        if eth_df.empty:
            dataframe["z_score"] = np.nan
            dataframe["crisis"] = 1
            return dataframe

        eth_df = eth_df[["date", "close"]].rename(columns={"close": "eth_close"})
        dataframe = merge_informative_pair(
            dataframe, eth_df, self.timeframe, self.inf_tf,
            ffill=True, date_column="date",
        )
        eth_col = f"eth_close_{self.inf_tf}"

        # ── Log prices ────────────────────────────────────────────────────────
        # Use log-price spread: log(BNB) - β * log(ETH)
        # More stable than dollar spread; β is log-price elasticity.
        log_bnb = np.log(dataframe["close"])
        log_eth = np.log(dataframe[eth_col])

        # ── Rolling OLS hedge ratio on log prices ─────────────────────────────
        dataframe["hedge_ratio"] = self._rolling_hedge_ratio(
            y=log_bnb,
            x=log_eth,
            window=self.OLS_WINDOW,
        )

        # ── Log-price spread ─────────────────────────────────────────────────
        dataframe["spread"] = log_bnb - dataframe["hedge_ratio"] * log_eth

        # ── Z-score ───────────────────────────────────────────────────────────
        spread_mean = dataframe["spread"].rolling(self.ZSCORE_WINDOW).mean()
        spread_std = dataframe["spread"].rolling(self.ZSCORE_WINDOW).std()
        spread_std = spread_std.replace(0, np.nan)
        dataframe["z_score"] = (dataframe["spread"] - spread_mean) / spread_std

        # ── CRISIS gate ───────────────────────────────────────────────────────
        atr14 = ta.ATR(dataframe, timeperiod=14)
        atr_p90 = atr14.rolling(self.CRISIS_ATR_WINDOW).quantile(0.90)
        dataframe["crisis"] = (atr14 > atr_p90).astype(int)

        return dataframe

    # ── Entry ─────────────────────────────────────────────────────────────────
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Enter on z-score extremes when CRISIS gate is clear."""
        not_crisis = dataframe["crisis"] == 0
        has_signal = dataframe["z_score"].notna()

        # Long: BNB underperforms ETH by ENTRY_ZSCORE standard deviations
        dataframe.loc[
            not_crisis & has_signal
            & (dataframe["z_score"] < -self.ENTRY_ZSCORE)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: BNB outperforms ETH by ENTRY_ZSCORE standard deviations
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

        # Exit long: spread has reverted upward
        dataframe.loc[
            has_signal & (dataframe["z_score"] > -self.EXIT_ZSCORE),
            "exit_long",
        ] = 1

        # Exit short: spread has reverted downward
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
        """Time stop: exit if trade has not reverted within MAX_HOLD_CANDLES (4h candles)."""
        trade_duration_candles = int(
            (current_time - trade.open_date_utc).total_seconds() / (4 * 3600)
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
        """Fixed 2x leverage. Single-leg (no ETH hedge) warrants conservative sizing."""
        return min(2.0, max_leverage)

    # ── Helper: rolling OLS on log prices ────────────────────────────────────
    def _rolling_hedge_ratio(
        self, y: pd.Series, x: pd.Series, window: int
    ) -> pd.Series:
        """Compute rolling OLS hedge ratio β where y ≈ β * x (on log prices).

        Uses the demeaned covariance/variance formula (numerically equivalent to
        OLS without intercept on demeaned series). O(n * window).

        Args:
            y: log(BNB) price series.
            x: log(ETH) price series (same index).
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
