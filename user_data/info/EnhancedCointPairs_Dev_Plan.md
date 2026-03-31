# Enhanced Cointegration Pairs Trading — Development Plan
## Candidate L from AlgoTrading Research Log
## Created: 2026-03-31 | Status: PRE-DEVELOPMENT

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Also read `user_data/info/AlgoTrading_Research_Log.md` for project-wide context, roles, and objectives.

### What This Project Is
We are implementing an enhanced cointegration pairs trading strategy on crypto futures. The core idea: identify pairs of crypto assets whose price ratio is cointegrated (mean-reverting), then trade deviations from equilibrium — go long the underperformer and short the outperformer when the spread widens beyond a z-score threshold, exit when it reverts. This is the same strategy class as our archived Candidate F (CointPairs), but enhanced with two innovations from recent peer-reviewed literature: (1) an **adaptive trailing stop-loss** calibrated to the spread's rolling volatility, and (2) a **volatility filter** that suppresses entries during high-vol regimes. These directly address the two failure modes that killed F.

This is Candidate L in our Research Log. A co-developer project running in parallel with Candidate J (Ensemble Donchian Trend-Following).

### Current Phase
- **Phase:** 0 — Pair Discovery + Frequency Validation
- **Last completed:** [Not started]
- **Next immediate step:** Run the existing `cointpairs_phase0_validation.py` (v4) pipeline at 1h across a 10-pair matrix (Palazzi's design), identify cointegrated pairs, validate that reversion half-life is compatible with hourly trading
- **Blocking issues:** None

### Key Context from Research Log
- We are Co-Investigators, Co-Strategists, and Co-Developers. Claude pushes back on bad ideas. See Research Log Section 1.
- Our objective is high-ROI, high-frequency crypto trading. See Research Log Section 2.
- **CointPairs (Candidate F) was ARCHIVED** after Phase 1 FAIL. Two independent failure modes: (1) single-leg directional exposure — without hedging the second leg, persistent directional moves bleed the strategy; (2) trade frequency — 0.05 trades/day on the only GO pair (BNB/ETH@4h). See Research Log Section 4.1.
- **What worked in F:** The mean-reverting structure is real (Hurst H ≈ 0.25). Phase 0 fee sweep showed solid economics when stoploss is absent (168bps@ez=3.0). Rolling β was stable. The Phase 0 validation framework is directly reusable.
- **LiqCascade is ACTIVE** in Phase 3 dry-run. Candidate J (Ensemble Donchian) is being built in parallel by the primary developer. L is a diversifying strategy — mean-reversion vs trend-following vs event-driven.
- **Critical lessons that apply here:** Mean-reversion half-life must be compatible with trading frequency (#9). Bull-market validation bias — check long vs short P&L symmetry (#10). Fee economics sweep before infrastructure (#7). Single-leg directional exposure is fatal (#F post-mortem).
- **Reusable infrastructure:** `user_data/scripts/cointpairs_phase0_validation.py` (v4) — complete pipeline (ADF → EG → Johansen → Hurst → OU half-life → rolling β stability → fee sweep with time-stop rate check). `CointPairsStrategy_V02.py` and `config_cointpairs_V02.json` — single-leg strategy code (reference only; L requires dual-leg rewrite).

### How L Differs from Archived F
| Aspect | F (Archived) | L (This Project) |
|---|---|---|
| **Legs** | Single-leg (long underperformer only) | **Dual-leg** (long underperformer + short outperformer) |
| **Stoploss** | Fixed percentage (-8% to -25%) — all calibrations failed | **Adaptive trailing stop** calibrated to spread's rolling volatility (Palazzi 2025) |
| **Entry filter** | None beyond z-score threshold | **Volatility filter** — suppress entries during high-vol regimes (Palazzi 2025) |
| **Pair universe** | BNB/ETH only (sole Phase 0 GO at 4h) | **10 major cryptos, all 45 unique pairs** screened at 1h (Palazzi design) |
| **Timeframe** | 4h | **1h** (targeting higher frequency; IEEE data suggests even shorter may work) |
| **Lookback optimization** | Fixed | **Grid-search optimized** lookback period per pair (Palazzi 2025) |
| **Validation** | In-sample only | **Walk-forward** (75/25 split, rolling) |

---

## Part 1: Strategy Summary

### 1.1 What Enhanced Cointegration Pairs Trading Is
At each candle:
1. For each active cointegrated pair (A, B), compute the **spread**: `S_t = log(price_A) - β × log(price_B)`, where β is the cointegrating vector (hedge ratio)
2. Compute the **z-score** of the spread: `z_t = (S_t - mean(S)) / std(S)` over a rolling lookback window
3. **Enter** when `|z_t|` exceeds entry threshold (e.g., ±2.0):
   - If `z_t > +threshold`: spread is too wide → short A, long B (expect reversion)
   - If `z_t < -threshold`: spread is too narrow → long A, short B
4. **Exit** when spread reverts to zero (z-score crosses back toward 0), OR via adaptive trailing stop, OR via time stop (backup)
5. **Volatility filter:** Suppress entry if the spread's recent rolling volatility exceeds a percentile threshold (e.g., top 10% of historical vol) — high-vol regimes produce false z-score signals
6. **Adaptive trailing stop:** Track the extreme spread value since entry; close position if spread reverses by more than `k × rolling_vol_spread` from the extreme — adapts to current market conditions

The alpha comes from equilibrium reversion: two assets sharing a common stochastic trend (e.g., BTC and ETH both driven by crypto market sentiment) temporarily diverge, then market forces (arbitrageurs, correlated flows, shared fundamentals) pull them back together.

### 1.2 Key Academic Findings
- **Palazzi (J. Futures Markets, Aug 2025, peer-reviewed):** Enhanced pairs trading on 10 major cryptos with adaptive trailing stop + vol filter. Consistently outperforms conventional pairs trading and passive approaches. Positive performance across both bull and bear regimes. Walk-forward validated.
- **Tadi & Witzany (Financial Innovation, 2025):** Copula-based pairs trading on Binance USDT-margined futures. Outperforms standard cointegration and copula approaches. Weekly pair re-selection using BTC as reference asset. Tested on our exact venue.
- **IEEE Xplore (2020):** Pairs trading on 26 cryptos at 5-min, 1h, and daily frequencies on Binance. Daily distance method returns −0.07%/month; **5-min returns 11.61%/month**. Higher frequency dramatically improves performance. Intraday mean-reverting behavior exists but is absent in daily data.
- **Our own F post-mortem:** Signal is real (Hurst H ≈ 0.25), fee economics are viable at 4h with no stoploss. Failure was structural (single-leg, frequency), not signal quality.

### 1.3 Why This Candidate Is Different from Our Failures
| Previous Failure | Why L Avoids It |
|---|---|
| F: single-leg directional exposure | **Dual-leg** — long underperformer + short outperformer simultaneously. Market-neutral by construction. |
| F: 0.05 trades/day frequency | **10 cryptos = 45 pairs** screened (vs F's 1 pair). **1h timeframe** (vs F's 4h). IEEE data shows frequency improves returns. |
| F: fixed stoploss all calibrations failed | **Adaptive trailing stop** calibrated to spread's rolling volatility — not a fixed percentage. Adjusts to current market conditions. |
| F: no entry filter | **Volatility filter** suppresses entries during high-vol regimes (false z-score signals). |
| RAME: edge too small | Spread mean-reversion moves are typically 50–300+ bps at 1h — well above fee floor. F's Phase 0 showed 168bps@ez=3.0 at 4h. |
| G: regime instability | Market-neutral pairs are structurally regime-agnostic — the spread doesn't care whether both assets are going up or down, only whether their ratio is reverting. Palazzi confirms positive performance in both bull and bear. |

### 1.4 The Dual-Leg Coordination Challenge
This is the primary engineering challenge (F's criterion 3 conditional pass). Freqtrade treats every trade as independent — it has no native concept of "paired legs." We need to ensure:

1. **Simultaneous entry:** When z-score crosses the threshold, both the long leg and the short leg must open together. If one leg fails to fill, the other must be cancelled or immediately closed.
2. **Simultaneous exit:** When the spread reverts (or trailing stop fires), both legs must close together. A half-closed pair is a naked directional position — exactly what killed F.
3. **Paired P&L tracking:** The strategy must track combined P&L across both legs, not per-leg P&L.

**Architecture approach:**
- Use `bot_loop_start()` to compute spreads and z-scores across all pairs
- Store pair state (paired_trade_id, entry_z, entry_time, extreme_spread) in `custom_info`
- `confirm_trade_entry()`: only confirm if the other leg can also be entered (check available margin, open trade count)
- `custom_exit()`: when one leg triggers exit, also exit the paired leg by setting its exit signal
- `max_open_trades`: set to 2× the number of desired concurrent pairs (e.g., 2×5 = 10 for 5 simultaneous pairs)
- **Fallback safety:** If only one leg is open for > 2 candles without the other, force-close it and log the error

---

## Part 2: Architecture

```
┌──────────────────────────────────────────────────────────┐
│   ENHANCED COINTEGRATION PAIRS TRADING ARCHITECTURE (V01) │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Freqtrade Strategy (1h candles, 10 assets = 45 pairs)   │
│  ┌───────────────────────────────────────────────────┐   │
│  │  bot_loop_start():                                │   │
│  │    For each cointegrated pair (A, B):             │   │
│  │      Load OHLCV for both assets via DataProvider  │   │
│  │      Compute spread: log(A) - β × log(B)         │   │
│  │      Compute z-score (rolling lookback window)    │   │
│  │      Compute spread rolling vol                   │   │
│  │      Check volatility filter                      │   │
│  │      Update adaptive trailing stop levels         │   │
│  │    Store all pair states in custom_info            │   │
│  │                                                   │   │
│  │  populate_entry_trend():                          │   │
│  │    IF z-score > +threshold AND vol_filter OK:      │   │
│  │      enter_short on A, enter_long on B            │   │
│  │    IF z-score < -threshold AND vol_filter OK:      │   │
│  │      enter_long on A, enter_short on B            │   │
│  │                                                   │   │
│  │  confirm_trade_entry():                           │   │
│  │    Check: can the paired leg also be opened?      │   │
│  │    Check: max concurrent pairs not exceeded       │   │
│  │                                                   │   │
│  │  custom_exit():                                   │   │
│  │    IF z-score reverted to 0 → close both legs     │   │
│  │    IF adaptive trailing stop triggered → close     │   │
│  │    IF time stop exceeded → close both legs        │   │
│  │    IF orphan leg detected → force close + log     │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  SHARED with LiqCascade / Candidate J:                   │
│  - DigitalOcean droplet infrastructure                   │
│  - Docker compose (new profile: cointpairs_v2)           │
│  - Separate Freqtrade instance + config + DB             │
│                                                          │
│  REUSES from F: Phase 0 validation pipeline              │
│  (cointpairs_phase0_validation.py v4)                    │
│                                                          │
│  NO sidecar needed. Standard OHLCV data.                 │
│  Dual-leg coordination via custom_info + callbacks.      │
└──────────────────────────────────────────────────────────┘
```

### 2.1 Key Design Decisions

**Asset universe:** 10 major cryptos selected per Palazzi's design — 5 PoW + 5 PoS by market cap. Suggested starting set (verify current market caps):
- PoW: BTC, DOGE, LTC, BCH, ETC
- PoS: ETH, BNB, SOL, ADA, XRP

This yields **45 unique pairs** for cointegration screening. Not all will be cointegrated — expect 10–15 to pass ADF/Johansen tests based on Palazzi's 37/90 hit rate.

**Timeframe:** 1h candles. F used 4h; IEEE data shows higher frequency improves returns. Phase 0 must validate that OU half-life is compatible with 1h trading (Lesson #9).

**Cointegration testing:** Engle-Granger (primary) + Johansen (confirmation). Re-test monthly or on a rolling basis — cointegration can break down.

**Lookback window for z-score:** Grid-search optimized per pair in Phase 0 (per Palazzi). Start range: 48h–720h (2 days to 30 days).

**Volatility filter:** Suppress entry when the spread's rolling volatility (e.g., 24h trailing std) exceeds the 90th percentile of its historical distribution. This prevents entering during regime breaks where cointegration is temporarily stressed.

**Adaptive trailing stop:**
- Track `extreme_spread`: the minimum spread value (for long-spread trades) or maximum (for short-spread trades) since entry
- Close position if spread reverses by `k × rolling_vol_spread` from the extreme
- `k` is a hyperparameter — Palazzi uses volatility-adaptive calibration
- This replaces F's fixed -8% to -25% stoploss that failed at every calibration

**Position sizing:**
- Each pair trade uses two legs with equal notional exposure
- `max_open_trades`: 2 × N_concurrent_pairs (e.g., 10 for 5 simultaneous pair trades)
- Per-leg stake: total_stake / (2 × N_concurrent_pairs)
- Leverage: 2x initially per leg
- `tradable_balance_ratio`: 0.90 (lower than J's 0.95 because dual-leg ties up more margin)

---

## Part 3: Phase Plan

### Phase 0: Pair Discovery + Frequency Validation (Days 1–2)

**Goal:** Identify which pairs are cointegrated at 1h, validate that OU half-lives are compatible with hourly trading, and run fee-inclusive signal validation. **Reuse `cointpairs_phase0_validation.py` (v4)** — adapt, don't rebuild.

**Tasks (Day 1 — Pair Discovery):**
1. Download 1h OHLCV for the 10-asset universe, 2022–2026
   ```
   freqtrade download-data --config config/config_cointpairs_v2.json --timerange 20220101-20260331 --timeframe 1h
   ```
2. Run cointegration screening across all 45 pairs using the existing Phase 0 pipeline:
   - ADF test on each asset (confirm non-stationarity of levels)
   - Engle-Granger cointegration test on each pair (p < 0.05)
   - Johansen test for confirmation
   - For each cointegrated pair: compute Hurst exponent, OU half-life, rolling β stability
3. **Critical check (Lesson #9):** For each cointegrated pair, compare OU half-life to the intended hold horizon. If half-life > 168h (7 days) at 1h, the pair may be too slow for our frequency objective. **Do not discard** — log it and flag for 4h testing. But prioritize pairs with half-life < 72h (3 days).
4. Output: cointegration matrix (45 pairs × pass/fail), ranked by OU half-life (fastest reversion first), with Hurst H and rolling β stability for each.

**Tasks (Day 2 — Fee-Inclusive Signal Validation):**
5. For each cointegrated pair, run a sweep on the existing Phase 0 fee-sweep tool (adapted for 1h):
   - Z-score entry thresholds: 1.5, 2.0, 2.5, 3.0
   - Lookback windows: 48h, 96h, 168h, 336h, 720h
   - Exit: z-score reversion to 0 (no stoploss — match F's Phase 0 approach that correctly identified the signal)
   - Fee: 10 bps per side × 2 legs = **20 bps round-trip total** (both legs!)
   - Track: per-trade P&L, profit factor, trade count, time-stop rate, avg hold duration
   - **Lesson #10 check:** For each pair, verify that long-spread and short-spread entries produce comparable P&L. If one side is +200bps and the other is -300bps, the signal is the market direction, not mean reversion.
6. Regime-split results: 2022 (bear), 2023 (range), 2024–2025 (bull), 2026 (recent)
7. **Fee note: dual-leg doubles the fee cost.** F's Phase 0 used 10 bps round-trip (single leg). L uses 20 bps round-trip (both legs). The spread move must be > 20 bps per trade for profitability. Check this explicitly.
8. Output: pair ranking by profitability, regime stability matrix, fee-sensitivity analysis.

**Go/No-Go for Phase 1:**
- At least **3 cointegrated pairs** with OU half-life < 72h at 1h resolution
- At least **1 pair** showing profit factor > 1.3 after 20 bps dual-leg fees in the sweep
- **Long-spread and short-spread P&L are roughly symmetric** (within 30% of each other) — confirming the signal is mean-reversion, not directional bias (Lesson #10)
- Time-stop rate < 50% (if using a time stop as backup) — confirms reversion is happening within the hold window (Lesson #9)
- Trade frequency across all GO pairs combined > 0.5 trades/day

**If no pairs pass at 1h:** Test 4h as fallback (same pipeline, just change timeframe). If 4h also fails, the OU half-lives may be fundamentally incompatible with active trading — this is the same failure mode as F, and we STOP.

**If pairs pass but dual-leg fee cost wipes out edge:** The 20 bps dual-leg cost is the structural challenge. If mean spread moves are 25–40 bps, the margin is razor-thin. Consider: (a) maker execution on one leg to reduce fees, (b) wider z-score thresholds to capture larger spread moves, (c) fewer but higher-quality pairs. If no workaround exists, STOP — Lesson #7 applies.

---

### Phase 1: Dual-Leg Freqtrade Implementation (Days 3–5)

**Prerequisite:** Phase 0 GO — at least 3 cointegrated pairs with viable economics.

**This is the engineering-heavy phase.** The dual-leg coordination logic is the primary implementation challenge — allocate an extra day vs J's timeline.

**Tasks:**
1. Create `config/config_cointpairs_v2.json`: all 10 assets in StaticPairList, futures mode, 1h, fees 0.05%/side, leverage 2x, `max_open_trades` = 2 × N_concurrent_pairs
2. Create `user_data/strategies/EnhancedCointPairsStrategy_V01.py`:
   - `informative_pairs()`: all 10 assets at 1h
   - `bot_loop_start()`: load all pair data, compute spreads + z-scores + rolling vol for all cointegrated pairs, store in `self.custom_info`
   - `populate_entry_trend()`: for each asset, check if it's the "entry leg" of any pair where z-score crossed the threshold and vol filter passes. Set `enter_long` or `enter_short` accordingly.
   - `confirm_trade_entry()`: **critical** — verify the paired leg can also be opened (margin available, not already in a conflicting trade). If not, reject the entry.
   - `custom_exit()`: check (a) z-score reversion to exit band, (b) adaptive trailing stop, (c) time stop, (d) orphan leg detection. When triggered, close both legs.
   - `custom_stake_amount()`: equal notional per leg, total per pair = 1/N_concurrent_pairs of available capital
3. **Build and test the dual-leg coordination** incrementally:
   - Step 1: Get paired entries working (both legs open on same candle)
   - Step 2: Get paired exits working (both legs close together)
   - Step 3: Add orphan detection (if one leg is open without partner for > 2 candles, force close)
   - Step 4: Add the adaptive trailing stop
   - Step 5: Add the volatility filter
4. Backtest on 2022–2026 using Phase 0's top 3–5 pairs and best parameters
5. **Diagnostic checks:**
   - Are both legs opening simultaneously? Check trade logs for timing mismatches.
   - Orphan rate: how often does only one leg open/close? Should be 0% ideally, < 5% acceptable.
   - Combined pair P&L: does the strategy actually capture spread reversion, or is one leg dominating?
   - Adaptive trailing stop fire rate: should be < 20% (it's a safety net for cointegration breakdown, not the primary exit)
   - Per-pair performance: which pairs contribute most? Any pair consistently losing?

**Go/No-Go for Phase 2:**
- Profit factor > 1.2 on full backtest
- Orphan leg rate < 5%
- Profitable in at least 2 of 3 regime periods (bear, range, bull)
- **Long-spread and short-spread trades have comparable P&L** (the market-neutral check)
- Trade frequency across all pairs > 0.5 trades/day
- Drawdown < 25% (at 2x leverage per leg)

---

### Phase 2: Optimization + OOS Validation (Days 6–7)

**Prerequisite:** Phase 1 GO.

**Tasks:**
1. **Lookback window optimization:** Grid-search per pair (Palazzi's approach): optimize the z-score lookback window to maximize in-sample Sharpe on 2022–2024
2. **Pair re-selection:** Re-run cointegration tests on rolling 6-month windows. Which pairs maintain cointegration throughout? Drop unstable pairs.
3. Hyperopt on 2022–2024:
   - Parameters: z-score entry threshold, z-score exit band, lookback window, vol filter percentile, trailing stop k-factor, time stop duration
4. Out-of-sample validation on 2025–2026
5. Walk-forward: train on rolling 6-month windows, test on 2-month windows, roll forward

**Go/No-Go for Phase 3:**
- OOS profit factor > 1.2
- Walk-forward profitable in at least 5 of 8 windows
- Cointegration stable in at least 3 pairs across the full sample
- Parameters not at extreme edges

---

### Phase 3: Dry-Run Deployment (Week 2+)

**Goal:** Deploy alongside LiqCascade (and possibly J), accumulate forward-testing data. Validate that dual-leg coordination works in live market conditions (not just backtest).

**Tasks:**
1. Add `cointpairs_v2` profile to Docker compose on droplet
2. Deploy as separate Freqtrade instance
3. **Critical live-monitoring:** Watch for orphan legs in the first 48 hours. A coordination failure in live trading is far worse than in backtest.
4. Monitor for 2+ weeks

**Go/No-Go for Phase 4 (live capital):**
- 2+ weeks, minimum 15 completed pair trades (both legs)
- Zero orphan legs in production
- Total return consistent with backtest expectation
- Trade frequency within 30% of backtest
- Stable coexistence with LiqCascade (and J if deployed) on shared droplet

---

## Part 4: What Not To Repeat

| Anti-pattern | Why it's relevant here | Addressed in |
|---|---|---|
| Single-leg directional exposure (F's fatal flaw) | **Dual-leg is mandatory.** If paired coordination can't be built reliably, STOP — don't fall back to single-leg. | Core architecture, orphan detection |
| Fee sweep after infrastructure (Lesson #7) | Phase 0 sweep before any Freqtrade code. **20 bps dual-leg cost** must be survivable. | Phase 0 Day 2 |
| OU half-life incompatible with timeframe (Lesson #9) | Phase 0 explicitly computes half-life and compares to 1h hold horizon. | Phase 0 Day 1 |
| Bull-market validation bias (Lesson #10) | Long-spread vs short-spread P&L symmetry check at every gate. | All go/no-go gates |
| Fixed stoploss on mean-reversion (F's second flaw) | **Adaptive trailing stop** calibrated to spread rolling vol — not fixed %. | Exit mechanism |
| Entering during cointegration breakdown | **Volatility filter** suppresses entries when spread vol is extreme. | Entry filter |
| Assuming cointegration is permanent | Re-test on rolling windows. Drop pairs that lose cointegration. | Phase 2 pair re-selection |
| Assuming paper timeframe transfers to ours | Palazzi uses daily; we need 1h. Phase 0 explicitly validates. | Phase 0 frequency validation |

---

## Part 5: File Locations (Planned)

| File | Purpose | Status |
|---|---|---|
| `user_data/strategies/EnhancedCointPairsStrategy_V01.py` | Dual-leg pairs trading (MVP) | To build (Phase 1) |
| `config/config_cointpairs_v2.json` | Strategy config (10 assets, futures, 1h) | To build (Phase 0) |
| `user_data/scripts/cointpairs_phase0_validation.py` | **EXISTING** Phase 0 pipeline (v4) — adapt for 1h and dual-leg fee calc | Reuse + adapt |
| `user_data/strategies/CointPairsStrategy_V02.py` | **EXISTING** F's single-leg strategy — reference only | Reference |
| `user_data/info/EnhancedCointPairs_Dev_Plan.md` | THIS FILE | Active |
| `user_data/info/AlgoTrading_Research_Log.md` | Project-wide context | Active |
| `user_data/info/CointPairsTrading_Deep_Dive.md` | F's deep dive — failure modes documented | Reference (ARCHIVED) |

### Appendix A: Asset Universe

| # | Asset | Consensus | Notes |
|---|---|---|---|
| 1 | BTC/USDT:USDT | PoW | Anchor — highest liquidity |
| 2 | ETH/USDT:USDT | PoS (since Sep 2022) | Anchor — second highest liquidity |
| 3 | BNB/USDT:USDT | PoS | F's Phase 0 tested BNB/ETH — GO at 4h |
| 4 | SOL/USDT:USDT | PoS | High vol, strong recent trends |
| 5 | XRP/USDT:USDT | PoS-like (RPCA) | Regulatory-sensitive — may break cointegration during legal events |
| 6 | ADA/USDT:USDT | PoS | Lower vol, potential stable cointegration partner |
| 7 | DOGE/USDT:USDT | PoW | Meme-driven — may not cointegrate reliably |
| 8 | LTC/USDT:USDT | PoW | BTC derivative — likely strong BTC/LTC cointegration |
| 9 | BCH/USDT:USDT | PoW | BTC fork — historically cointegrated with BTC |
| 10 | ETC/USDT:USDT | PoW | ETH fork — historically cointegrated with ETH |

*This list follows Palazzi's 5 PoW + 5 PoS design. Adjust based on current Binance Futures availability and liquidity (24h volume > $10M per asset). Phase 0 will determine which of the 45 pairs are actually cointegrated.*

---

## Part 6: Reference Material

### 6.1 Key Papers
- **Palazzi (J. Futures Markets, Aug 2025):** "Trading Games: Beating Passive Strategies in the Bullish Crypto Market" — Primary source. Adaptive trailing stop, vol filter, grid-search lookback optimization, walk-forward validation. 10 cryptos, bull + bear regime performance.
- **Tadi & Witzany (Financial Innovation, 2025):** "Copula-based trading of cointegrated cryptocurrency Pairs" — Copula approach on Binance USDT-margined futures. Weekly pair re-selection. Outperforms standard methods. Our exact venue.
- **IEEE Xplore (2020):** "Pairs Trading in Cryptocurrency Markets" — 26 cryptos at 5-min, 1h, daily on Binance. Critical finding: frequency matters enormously (5-min: +11.61%/month vs daily: −0.07%/month).
- **Our CointPairs (F) post-mortem:** Research Log Section 4.1. Signal real, failure structural. Phase 0 validation framework reusable.

### 6.2 Freqtrade Implementation References
- **Simultaneous long/short:** Freqtrade supports `can_short = True` in futures mode
- **Paired coordination:** `confirm_trade_entry()` for pre-entry validation, `custom_exit()` for paired exits, `bot_loop_start()` for cross-pair state management
- **Custom trailing stop:** `custom_stoploss()` — return negative value; can reference `self.custom_info` for spread-based stop levels
- **Informative pairs:** `informative_pairs()` for loading all 10 assets

### 6.3 Relationship to F's Codebase
L reuses:
- `cointpairs_phase0_validation.py` (v4) — adapt fee calculation for dual-leg (20 bps not 10 bps)
- Cointegration testing methodology (ADF, EG, Johansen, Hurst, OU half-life)
- Spread computation and z-score logic

L replaces:
- Single-leg → dual-leg (fundamental architecture change)
- Fixed stoploss → adaptive trailing stop
- No entry filter → volatility filter
- Fixed lookback → grid-search optimized lookback
- Single-pair → multi-pair universe

### 6.4 Coordination with Candidate J
J and L are designed to be **uncorrelated and concurrent:**
- J is long-only trend-following (serial correlation). L is market-neutral mean-reversion (equilibrium reversion).
- J performs best in trending markets. L performs best in ranging markets.
- J uses 20 pairs independently. L uses 10 assets in paired combinations.
- They share infrastructure (droplet, Docker) but run as separate Freqtrade instances with separate DBs.
- If both validate, deploying them together provides genuine strategy diversification.

---

*Document maintained by: Claude + co-developer*
*Last updated: 2026-03-31 — Initial creation*
