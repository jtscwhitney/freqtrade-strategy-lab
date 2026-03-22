# Cointegration Pairs Trading — Deep Dive
## Version 1 | Started: 2026-03-22 | Status: ARCHIVED — Phase 1 FAIL (2026-03-22)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**
> Combined with `~/.claude/projects/.../memory/MEMORY.md` and `AlgoTrading_Research_Log.md`, this provides full context.

### Current Status
- **Phase:** ARCHIVED — Phase 1 FAIL (2026-03-22)
- **Reason:** Phase 1 backtest (BNB/ETH@4h, 2022–2025) produced -81% total return with profit factor 0.85. Two structural failure modes identified — see Part 9 for full results.
- **Next step:** Archive. Proceed to Candidate E (Path Signatures).

### Key Commands
```
# Download 4h data (covers Phase 1 backtest range)
docker compose run --rm freqtrade download-data --config config/config_cointpairs_V01.json --pairs BNB/USDT:USDT ETH/USDT:USDT --timerange 20220101-20251231 --timeframes 4h

# Backtest V02 (no cache — first run)
docker compose run --rm freqtrade backtesting --config config/config_cointpairs_V02.json --strategy CointPairsStrategy_V02 --timerange 20230101-20251231 --cache none

# Walk-forward: train 2022–2023, test 2024–2025
docker compose run --rm freqtrade backtesting --config config/config_cointpairs_V02.json --strategy CointPairsStrategy_V02 --timerange 20220101-20231231 --cache none
docker compose run --rm freqtrade backtesting --config config/config_cointpairs_V02.json --strategy CointPairsStrategy_V02 --timerange 20240101-20251231 --cache none

# Phase 0 validation (re-run if adding new pairs)
docker compose run --rm --entrypoint python freqtrade user_data/scripts/cointpairs_phase0_validation.py

# Hyperopt (Phase 4)
docker compose run --rm freqtrade hyperopt --config config/config_cointpairs_V02.json --strategy CointPairsStrategy_V02 --hyperopt-loss SharpeHyperOptLoss --spaces entry exit stoploss --epochs 500 --timerange 20230101-20241231
```

### File Locations
| File | Status | Purpose |
|---|---|---|
| `user_data/strategies/CointPairsStrategy_V02.py` | **TO BUILD** | Phase 1 backtest — BNB single-leg, ETH informative, 4h |
| `user_data/strategies/CointPairsStrategy_V01.py` | REFERENCE | Original ETH/BTC@1h design — superseded by Phase 0 results |
| `config/config_cointpairs_V02.json` | **TO BUILD** | 4h BNB/ETH config |
| `config/config_cointpairs_V01.json` | REFERENCE | Original 1h config — superseded |
| `user_data/scripts/cointpairs_phase0_validation.py` | DONE (v4) | Phase 0 validation — reusable for any new pair |
| `user_data/info/CointPairsTrading_Deep_Dive.md` | THIS FILE | Authoritative reference |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Project-wide context and strategy registry |

---

## Part 1: Why We're Here

### 1.1 Research Context

This project is Candidate F from Sourcing Sweep #2 (`AlgoTrading_Research_Log.md`). Key sources:

- **Amberdata blog series (2025):** Comprehensive 5-part crypto pairs trading guide with backtested results — 62% total return over 2021–2024 (Sharpe ~0.93) on BTC/ETH. No leverage, no ML enhancement.
- **arXiv:2109.10662 (Tadi, 2021):** Minute-level cointegration pairs trading on crypto with realistic execution simulation and fee inclusion. Outperforms buy-and-hold.
- **Frontiers in Applied Mathematics (Jan 2026):** DNN/LSTM spread forecasting on Johansen-cointegrated crypto pairs, tested on 2018–2025 data.

Evaluation filter score: **6/7 PASS, 1 CONDITIONAL PASS** (Freqtrade paired-trade coordination architecture). See Research Log Section 4.3 for full evaluation.

### 1.2 Why This Is Different From Prior Work

| Dimension | RAME | LiqCascade | CointPairs |
|---|---|---|---|
| Alpha source | Lagged indicator regime | Mechanical market event | Statistical equilibrium relationship |
| Market condition | Bull/bear classification | Event-driven (cascades) | Ranging / mean-reverting |
| Direction | Trend-following | Momentum | Mean-reversion |
| Data required | OHLCV + indicators | Real-time WebSocket | OHLCV only |
| Sidecar needed | No | Yes | No |
| Complements LiqCascade | N/A | Self | YES — opposite market conditions |

**Why cointegration has structural grounding:**
Engle and Granger (Nobel Prize, 2003): when two non-stationary price series share a common stochastic trend (i.e., are cointegrated), temporary deviations from their equilibrium ratio are corrected by market forces — correlated participant flows, shared fundamentals, arbitrageur reversion. This is not curve-fitting. It is an econometric property of the assets that has been validated across asset classes for 30+ years.

**For BTC and ETH specifically:** Both are driven by the same macro crypto sentiment, institutional flows, and regulatory events. When one temporarily outperforms the other beyond historical norms, reversion pressure typically follows. The spread between them has historically been mean-reverting at daily and sub-daily timeframes.

### 1.3 Lessons Applied From Prior Projects

| Lesson (source) | How it applies here |
|---|---|
| ML accuracy ≠ trading edge (RAME) | V01 does not use ML. The signal is the z-score — directly interpretable. |
| Validate fee economics first (LOB) | Phase 0 includes explicit fee economics sweep across z-score thresholds before any execution infrastructure. |
| Institutional paper results ≠ retail (LOB) | Amberdata 62% return is with realistic fees — 0.05–0.1% per trade. Must verify our actual fee tier assumptions. |
| Structural alpha > statistical alpha (RAME → LiqCascade) | Cointegration is structural (equilibrium relationship), not a statistical pattern mined from recent data. |
| Short-term indicators lie in macro trends (RAME) | CRISIS gate (ATR p90) blocks entries during extreme volatility when cointegration temporarily decouples. |

---

## Part 2: Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              COINTPAIRS STRATEGY ARCHITECTURE               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BTC/USDT:USDT (1h informative pair — read-only)           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  btc_close_1h → available in ETH strategy df       │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                  │
│                    hedge_ratio (OLS)                        │
│                          │                                  │
│  ETH/USDT:USDT (1h base — executed)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  spread    = eth_close - hedge_ratio * btc_close   │    │
│  │  z_score   = (spread - μ) / σ   [rolling window]  │    │
│  │                                                    │    │
│  │  CRISIS gate: ATR(14) > rolling-200-period p90     │    │
│  │                                                    │    │
│  │  Enter LONG  ETH when z < -ENTRY_ZSCORE            │    │
│  │  Enter SHORT ETH when z >  ENTRY_ZSCORE            │    │
│  │                                                    │    │
│  │  Exit when |z| reverts within EXIT_ZSCORE of zero  │    │
│  │  Stoploss: -8% (spread divergence safety net)      │    │
│  │  Time stop: MAX_HOLD_CANDLES (72h)                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**V01 design choice — single leg (ETH only):**
Phase 1 trades only the ETH leg. The full market-neutral pairs trade would simultaneously short BTC (for long ETH entries) and long BTC (for short ETH entries). This coordination is deferred to V02. Reasons:
1. V01 validates whether the cointegration z-score signal has sufficient edge at our fee tier
2. Single-leg is directly backtestable in standard Freqtrade without coordination logic
3. If signal is marginal, single-leg avoids doubling execution costs during validation

**V02 will add the BTC hedge leg.** See Part 7 (Phase Plan) for full dual-leg architecture design.

---

## Part 3: Cointegration Framework

### 3.1 What Cointegration Is (and Is Not)

**Correlation** measures whether two series move in the same direction at the same time. Highly correlated series can both trend — correlation does not imply mean reversion.

**Cointegration** measures whether two non-stationary series share a common stochastic trend. If cointegrated, their spread (a linear combination of the two) is stationary — it has a stable mean and bounded variance. This stationarity is what makes mean-reversion trading theoretically grounded.

Formally: `spread_t = ETH_t - β * BTC_t` is stationary if ETH and BTC are cointegrated with hedge ratio β.

### 3.2 Pair Validation Protocol (Phase 0)

Before any backtesting, run the following tests on historical data:

**Step 1 — Augmented Dickey-Fuller (ADF) test on each individual series:**
- Both ETH and BTC should be non-stationary (ADF p > 0.05 for the price levels)
- Both should be I(1) — stationary after first-differencing
- This confirms the precondition for cointegration testing

**Step 2 — Engle-Granger cointegration test:**
1. Regress ETH on BTC: `ETH = α + β * BTC + ε`
2. Run ADF test on the residuals `ε`
3. If residuals are stationary (ADF p < 0.05), the pair is cointegrated
4. Record the hedge ratio β, cointegration strength (ADF statistic), and p-value

**Step 3 — Johansen test (confirmatory):**
- Multivariate cointegration test — more robust than Engle-Granger for 2 series
- Should confirm at least 1 cointegrating vector

**Step 4 — Hurst exponent on the spread:**
- H < 0.5 confirms mean-reverting behaviour
- H close to 0.3–0.4 is ideal — strong mean reversion
- H ≥ 0.5 indicates random walk or trend — do not trade this pair

**Step 5 — Half-life of mean reversion:**
- Fit an Ornstein-Uhlenbeck process to the spread: `dS_t = κ(θ - S_t)dt + σdW_t`
- Half-life = `ln(2) / κ`
- Target: half-life of 10–100 hours (for 1h timeframe trading)
- < 10h: reversion too fast — fees dominate
- > 100h: reversion too slow — capital tied up too long

**Candidate pairs to test (order by priority):**
1. ETH/USDT + BTC/USDT — canonical, highest liquidity, most studied
2. SOL/USDT + ETH/USDT — high correlation, both layer-1 smart contract platforms
3. BNB/USDT + ETH/USDT — exchange token, correlated but potentially noisier cointegration
4. SOL/USDT + BTC/USDT — may be less stable cointegration given different volatility profiles

### 3.3 Cointegration Stability Concern

**Known failure mode:** Cointegration relationships can break down during:
- Regime changes (bull → bear transitions)
- Asset-specific shocks (ETH merge events, BTC halving)
- De-correlation periods (alt season — ETH outperforms BTC for extended periods)

**Safeguards:**
1. CRISIS gate (ATR p90) blocks entries during extreme volatility events that commonly trigger decoupling
2. Hard stoploss of -8% prevents unlimited loss if spread diverges indefinitely
3. Time stop of 72h forces position closure if no reversion — better to realize small loss than hold a decoupled pair
4. Periodic manual ADF re-validation (quarterly) — if p-value drifts above 0.10, pause the strategy

---

## Part 4: Spread Construction and Signal

### 4.1 Hedge Ratio

**V01 — Rolling OLS:**
At each candle, regress ETH on BTC over the trailing `OLS_WINDOW` candles:
```
β_t = cov(ETH_{t-W:t}, BTC_{t-W:t}) / var(BTC_{t-W:t})
```
Using the covariance/variance formula (equivalent to OLS intercept-excluded, numerically stable).

The hedge ratio is dimensioned: "1 unit of ETH is equivalent to β units of BTC." Typical range: 0.05–0.15 (ETH/BTC price ratio is ~0.05–0.08 in 2024–2025 at USD prices).

**V01 parameter:** `OLS_WINDOW = 720` (30 days at 1h). Long enough to capture the stable relationship, short enough to adapt to structural shifts over months.

**Known limitation:** Rolling OLS has a ~2-week lag when BTC/ETH ratio undergoes a structural shift (e.g., ETH underperforms BTC for 3 months straight). The Kalman filter hedge ratio (V03 upgrade) adapts more quickly because it continuously updates using a Bayesian state estimate.

### 4.2 Spread and Z-Score

```
spread_t      = ETH_close_t - β_t * BTC_close_t
spread_mean_t = rolling_mean(spread, ZSCORE_WINDOW)
spread_std_t  = rolling_std(spread, ZSCORE_WINDOW)
z_score_t     = (spread_t - spread_mean_t) / spread_std_t
```

**V01 parameter:** `ZSCORE_WINDOW = 720` (30 days at 1h). This defines what "normal" spread is. Larger windows are more stable but slower to adapt; smaller windows are noisier but more responsive.

**Interpretation:**
- z_score = 0: spread is at its historical mean — no signal
- z_score = +2: ETH has outperformed BTC by 2 standard deviations — enter SHORT ETH (expect reversion downward)
- z_score = -2: ETH has underperformed BTC by 2 standard deviations — enter LONG ETH (expect reversion upward)

### 4.3 Entry / Exit Thresholds

| Signal | z-score condition | Action | Rationale |
|---|---|---|---|
| Enter long | z < −ENTRY_ZSCORE (default −2.0) | Buy ETH | ETH 2σ below equilibrium — expect reversion up |
| Enter short | z > +ENTRY_ZSCORE (default +2.0) | Sell ETH | ETH 2σ above equilibrium — expect reversion down |
| Exit long | z > −EXIT_ZSCORE (default −0.5) | Close long | Spread has reverted — take profit |
| Exit short | z < +EXIT_ZSCORE (default +0.5) | Close short | Spread has reverted — take profit |

**Why exit at ±0.5 and not at 0:**
- Exiting exactly at 0 misses the trade-off between capturing more reversion vs increased time in trade
- ±0.5 is a standard practitioner threshold — captures the bulk of the move without waiting for perfect equilibrium
- Can be optimised in Phase 4 Hyperopt

---

## Part 5: CRISIS Gate (Volatility Filter)

**Same gate as LiqCascade, same rationale:**

```
ATR(14)_1h > rolling-200-period-p90(ATR14_1h)  →  CRISIS = True  →  ALL entries blocked
```

**Why pairs trading needs a CRISIS gate:**
During extreme volatility events, cointegration temporarily decouples. Forced liquidations, exchange-specific issues, or macro shocks can drive one asset far from the other for hours or days — well beyond normal z-score thresholds. Entering a pairs trade during CRISIS exposes the position to the spread diverging further rather than reverting.

**What CRISIS does NOT do:**
- Does not close existing trades (the reversion may still happen even during high volatility)
- Does not differentiate between the two assets (it is a global gate on the trading pair)

---

## Part 6: Risk Management

### 6.1 Stoploss

**Value:** −8% from entry (at 2x leverage = 4% price move)

**Rationale:** In V01 single-leg trading, the stoploss protects against:
1. Cointegration breakdown — spread keeps diverging instead of reverting
2. Black swan events specific to ETH (merge complications, major ETH hack, regulatory action)

At 1h timeframe, ETH ATR is typically 0.5–1.5%. A 4% adverse price move is 3–8 ATR — wide enough to avoid premature exits on normal volatility noise but tight enough to limit loss if the trade thesis is wrong.

**This is NOT a trailing stop.** Pairs trades are not momentum holds — we want to stay in the position while the spread is still in the reversion zone, not trail a trend.

### 6.2 Time Stop

**Value:** `MAX_HOLD_CANDLES = 72` (72 hours at 1h = 3 days)

**Rationale:** If a spread has not reverted within 3 days, the cointegration relationship may have temporarily broken down, or we entered during a structural shift in the hedge ratio. Better to exit at a small loss and re-enter when the spread recovers to a new z-score extreme from a clean baseline.

**Implementation:** `custom_exit()` returns `"time_stop"` when trade has been open ≥ MAX_HOLD_CANDLES.

### 6.3 Leverage

**V01:** 2x fixed leverage.

**Rationale:** Single-leg pairs trading is directional (no hedge), so it carries the full price risk of ETH. 2x is conservative relative to LiqCascade (4x) but appropriate given:
- Longer trade duration (hours vs minutes) — more time for adverse moves to compound
- Mean reversion is probabilistic, not mechanical — higher probability of eventual reversion but not guaranteed
- No hedge to offset ETH-specific risk

**V02 dual-leg:** With BTC hedge, effective leverage can increase because the net exposure is to spread movement rather than absolute price. 3–4x on the spread (but 2x per leg) becomes reasonable.

---

## Part 7: Phase Plan

### Phase 0 — Cointegration Validation ✓ COMPLETE (2026-03-22)
**Result:** CONDITIONAL GO. BNB/ETH@4h is the only GO pair (6/8). EG/Johansen fail universally — strategy is ratio mean reversion, not strict cointegration. See Part 9 for full results.

### Phase 1 — Single-Leg Backtest (BNB/ETH@4h)
**Strategy:** `CointPairsStrategy_V02.py` — BNB single-leg, ETH as informative anchor, 4h

**Target parameters from Phase 0:**
- `timeframe = "4h"`, `inf_tf = "4h"`
- `OLS_WINDOW = 180` (30d × 6 candles/day at 4h)
- `ZSCORE_WINDOW = 84` (14d × 6 — best performing window from Phase 0)
- `MAX_HOLD_CANDLES = 360` (60d × 6 — corresponds to 1440h stop)
- `ENTRY_ZSCORE = 3.0` (best fee sweep config from Phase 0; lower to 2.0 for more trades)
- `EXIT_ZSCORE = 0.5`
- Traded pair: `BNB/USDT:USDT`; Informative: `ETH/USDT:USDT`

**Tasks:**
1. Build `CointPairsStrategy_V02.py` (adapt V01: swap pairs, set 4h, update parameters)
2. Build `config/config_cointpairs_V02.json` (BNB whitelist, 4h)
3. Backtest on full period 2022–2025
4. Walk-forward: train 2022–2023, test 2024–2025
5. Analyse: trade count, win rate, profit factor, avg hold, drawdown
6. Verify: are exits via z-score reversion (not stoploss/time stop)?

**Go/no-go for Phase 2:** ≥20 trades (adjusted down from 50 — inherently low frequency at 4h/ez=3.0), profit factor > 1.2, win rate > 45%, ≥80% of exits via z-score reversion (not stoploss/time stop).

### Phase 2 — Dual-Leg Coordination (Days 6–8)
**Strategy:** CointPairsStrategy_V02

**Architecture change:**
- When entering LONG ETH → simultaneously enter SHORT BTC (hedged)
- When entering SHORT ETH → simultaneously enter LONG BTC (hedged)
- Implementation via `confirm_trade_entry()` cross-pair coordination:
  - Leg A (ETH) fires `enter_long/short` signal
  - `confirm_trade_entry()` on ETH checks if BTC leg is already open — if so, reject duplicate
  - Strategy also runs on BTC pair, reading a shared signal file to determine whether to enter as hedge leg
- Exit coordination: `custom_exit()` on ETH checks if paired BTC trade exists and signals both legs

**Key risk:** Freqtrade processes pairs sequentially. There is a window where one leg is open and the other is not (single-leg exposure). This is an inherent architecture limitation — mitigate by running both pairs on the fastest available cycle.

**Go/no-go for Phase 3:** Dual-leg shows improvement in Sharpe ratio vs V01 (lower drawdown expected from delta-neutrality).

### Phase 3 — Dry Run (2+ Weeks)
**Deploy to DigitalOcean droplet alongside LiqCascade.**

Go/no-go for Phase 4: 20+ trades, profit factor > 1.0, win rate > 50%, sidecar (no sidecar needed — all OHLCV) uptime N/A.

### Phase 4 — Hyperopt
**Parameters to optimise:**
- ENTRY_ZSCORE (range: 1.5–3.5)
- EXIT_ZSCORE (range: 0.2–1.0)
- OLS_WINDOW (range: 480–2160)
- ZSCORE_WINDOW (range: 240–1440)
- MAX_HOLD_CANDLES (range: 24–120)
- stoploss (range: -0.04 to -0.15)

### Phase 5 — Multi-Pair Expansion
Add SOL/ETH or SOL/BTC as a second independent pair if Phase 0 validation passes for those pairs. Multiple concurrent pairs increase trade frequency. Run each pair independently (separate strategy instances or single strategy with dynamic pair-based z-score state).

### Phase 6 — Live Capital
Prerequisites: 4 weeks dry-run, profit factor > 1.2, Sharpe > 1.0.

---

## Part 8: Open Questions

1. **Does cointegration hold across bull/bear cycles in 2022–2025?** BTC/ETH may decouple during altcoin seasons or around major ETH-specific events. Phase 0 must test across the full 2022 bear market.

2. **What is the actual BTC/ETH half-life at 1h in 2024–2025?** If half-life has increased (reversion slower), the time stop and expected P&L per trade may need adjustment.

3. **Does the rolling OLS hedge ratio drift significantly enough to warrant Kalman filter in V01, or is 30-day rolling OLS sufficient?** The answer comes from Phase 0 — plot the rolling hedge ratio over time and measure its stability.

4. **Fee economics at our actual Binance tier.** Amberdata results assume taker fees. Are we VIP-level? Standard retail (5 bps/side = 10 bps round-trip) is the assumption — verify before Phase 1.

5. **Dual-leg coordination race condition.** In Phase 2, how bad is the window between Leg A and Leg B executing? At 1h timeframe the window is at most a few seconds (both pairs analysed within the same Freqtrade cycle) — probably negligible. But needs empirical confirmation.

6. **SOL cointegration stability.** SOL has shorter history and higher idiosyncratic risk than BTC/ETH. Does it form a reliable cointegrated pair with either? Phase 0 tests this.

7. **Funding rate as entry pre-condition (like LiqCascade open question #4).** When the BTC/ETH spread is at an extreme, is the funding rate on the "overpriced" asset consistently negative? If so, it's additional confirmatory evidence of overextension and could be used as an optional entry filter.

---

## Part 9: Results Log

*Populated as backtests and forward tests complete.*

### Phase 0 — Cointegration Validation
- **Date:** 2026-03-22 (v4 script — multi-timeframe, 5 pairs)
- **Script:** `user_data/scripts/cointpairs_phase0_validation.py` (v4)
- **Data:** 2022-01-01 – 2025-12-31 (35,064 candles @ 1h; 8,766 @ 4h)

**Full results table (v4):**

| Pair/TF | EG p | Johansen | Hurst | Half-life | P(revert) | β std | Fee sweep | Passes | Overall |
|---|---|---|---|---|---|---|---|---|---|
| ETH/BTC@1h | 0.095 | FAIL | 0.255 | 968h | 11% | 0.733 | MARGINAL | 4/8 | MARGINAL |
| SOL/ETH@1h | 0.613 | FAIL | 0.261 | 2143h | 5% | 0.348 | PASS | 4/8 | MARGINAL |
| SOL/BTC@1h | 0.406 | FAIL | 0.260 | 2122h | 5% | 0.792 | MARGINAL | 3/8 | NO GO |
| BNB/ETH@1h | 0.796 | FAIL | 0.251 | 3111h | 4% | 0.228 | MARGINAL | 4/8 | MARGINAL |
| BNB/BTC@1h | 0.609 | FAIL | 0.244 | 2156h | 5% | 0.474 | MARGINAL | 4/8 | MARGINAL |
| ETH/BTC@4h | 0.082 | FAIL | 0.251 | 989h | 64% | 0.733 | PASS | 5/8 | MARGINAL |
| SOL/ETH@4h | 0.618 | FAIL | 0.269 | 2409h | 34% | 0.347 | PASS | 5/8 | MARGINAL |
| SOL/BTC@4h | 0.410 | FAIL | 0.261 | 2337h | 35% | 0.791 | PASS | 5/8 | MARGINAL |
| **BNB/ETH@4h** | **0.811** | **FAIL** | **0.251** | **3240h** | **27%** | **0.229** | **PASS** | **6/8** | **GO** |
| BNB/BTC@4h | 0.535 | FAIL | 0.244 | 2280h | 36% | 0.473 | PASS | 5/8 | MARGINAL |

**Key findings:**

1. **EG and Johansen fail universally** — no pair is formally cointegrated over 2022–2025 at any timeframe. We are trading Hurst-based ratio mean reversion (H≈0.25 everywhere), not strict cointegration. The ETH/BTC ratio declined 53% over this period (ETH secular underperformance) — these are trending ratios with overlaid mean reversion, not equilibrium relationships.

2. **Timescale hypothesis validated.** At 1h with 168h stop: ts=48–100% (spreads never revert within hold window). At 4h with 1440h stop: ts=0% universally (positions always exit via z-score, never time stop). The 60-day window is genuinely large enough.

3. **BNB/ETH@4h is the only GO (6/8).** The differentiating check is β stability: std=0.229 (STABLE). All other pairs have β ranging from negative to 3–4x — not tradeable. BNB/ETH's stable β reflects a genuine structural relationship (exchange token vs smart contract platform, BNB quarterly burn mechanism, BSC/ETH competition cycles).

4. **Best fee sweep config for BNB/ETH@4h:** ZSCORE_WINDOW=84c (14d), ez=3.0, xz=0.5, n=7, wr=43%, net=168bps, ts=0%. Also: 180c window shows 674bps but n=4. Trade count is very low (~1.75/year at ez=3.0).

5. **Bull-market artifact confirmed.** At 1h, "PASS" fee sweeps had high ts% and zero profitable short entries. At 4h, both longs and shorts show positive net — directional bias is gone.

- **Decision:** CONDITIONAL GO → Phase 1 with BNB/ETH@4h. Phase 1 go/no-go bar adjusted to ≥20 trades (inherently low frequency at 4h).

### Phase 1 — V02 Backtest Results (BNB/ETH@4h)
- **Date:** 2026-03-22
- **Strategy:** `CointPairsStrategy_V02.py` — BNB/ETH@4h, stoploss=-0.25 (widened from -0.08 after initial run)
- **Period:** 2022-03-08 – 2025-12-31 (1,400 days)

**Initial run (stoploss=-0.08):**
| Exit Reason | Trades | Avg Profit | Win Rate |
|---|---|---|---|
| exit_signal | 34 | +14.64% | 88.2% |
| stop_loss | 73 | -8.16% | 0% |
| TOTAL | 108 | -0.84% | 28.7% |

Result: -83.19%. 67.6% of trades hit the -8% hard stop. Diagnosis: at 2x leverage, -8% fires on 4% BNB moves — routine at 4h.

**Second run (stoploss=-0.25):**
| Exit Reason | Trades | Avg Profit | Win Rate |
|---|---|---|---|
| exit_signal | 51 | +6.39% | 64.7% |
| stop_loss | 15 | -25.17% | 0% |
| TOTAL | 67 | -0.68% | 50.7% |

Result: -81.39%. Stop count reduced from 73 → 15, but each stop now at -25% (≈ -$2,500 per $10k stake). Negative expectancy: 15 losses × $2,500 > 51 wins × $637.

**Month breakdown key observations:**
- 2022–2023: Choppy but mostly signal-positive. Multiple profitable months.
- Jan–Mar 2024: Two massive wins (+$4,984, +$14,359 — best trade +77.49%).
- Apr 2024 – Nov 2025: **18-month sustained drawdown.** BNB/ETH spread trended against long BNB due to ETH ETF narrative and Binance regulatory headwinds. Single-leg exposure absorbed the full directional move.

**Long/short analysis (second run):** Both longs (-75.88%) and shorts (-5.51%) lose — the directional problem is not purely one-sided. The 2024–2025 regime shift affected both directions unevenly.

**Two structural failure modes:**
1. **Single-leg directional exposure.** Without hedging the ETH leg, 18 months of BNB/ETH directional trend bleeds the strategy. No fixed stop calibration resolves the negative expectancy — widening the stop just makes each loss larger. Dual-leg (V03) would address this.
2. **Trade frequency incompatible with active-trading objective.** 67 trades / 1,400 days = 0.05 trades/day. BNB/ETH@4h is the only Phase 0 GO pair — no universe to scale across.

**Decision:** Phase 1 FAIL. Project archived. Signal quality (exit_signal trades) is real but the structural failure modes preclude deployment. Reusable asset: `cointpairs_phase0_validation.py` (v4).
