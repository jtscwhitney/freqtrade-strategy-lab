# Cross-Sectional Crypto Momentum — Development Plan
## Candidate G from AlgoTrading Research Log
## Created: 2026-03-22 | Status: PRE-DEVELOPMENT

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Also read `user_data/info/AlgoTrading_Research_Log.md` for project-wide context, roles, and objectives.

### What This Project Is
We are implementing a cross-sectional momentum strategy for crypto futures. The core idea: rank a universe of 10–30 crypto assets by recent returns, go long the top-ranked winners and short the bottom-ranked losers, rebalance at regular intervals. This is Candidate G in our Research Log — the first candidate to achieve a clean 7/7 PASS on our evaluation filter.

### Current Phase
- **Phase:** 0 — Data Download + Exploration
- **Last completed:** [Not started]
- **Next immediate step:** Download 1h OHLCV data for 20+ Binance Futures pairs, compute formation-period returns, explore return distributions and cross-sectional dispersion
- **Blocking issues:** None

### Key Context from Research Log
- We are Co-Investigators, Co-Strategists, and Co-Developers. Claude pushes back on bad ideas. See Research Log Section 1.
- Our objective is high-ROI, high-frequency crypto trading. See Research Log Section 2.
- **Three previous candidates failed:** RAME (edge too small), LOB Microstructure (fee economics), CointPairs (trade frequency + single-leg exposure). See Research Log Section 4.1 and Lessons #1–11.
- **LiqCascade is ACTIVE** in Phase 3 dry-run. This strategy would run concurrently, not replace it.
- **Candidate E (Path Signatures)** is being implemented by a co-developer in parallel. If both E and G validate, Candidate I (combination) is reserved.
- **Critical lessons that apply here:** Fee economics sweep before infrastructure (#7). Bull-market validation bias (#10). Time-stop rate as diagnostic (#11). Momentum effect is winner-concentrated — losers rebound (#academic, Han et al.).

---

## Part 1: Strategy Summary

### 1.1 What Cross-Sectional Momentum Is
At each rebalancing point:
1. Compute returns for all assets in the universe over a lookback ("formation") period
2. Rank assets by return — highest to lowest
3. Go **long** the top N assets (winners)
4. Go **short** the bottom N assets (losers) — *or skip shorts entirely (winner-only variant)*
5. Hold for the "holding" period, then repeat

The alpha comes from return continuation: assets that outperformed recently tend to continue outperforming in the near term (and vice versa for underperformers).

### 1.2 Key Academic Findings Specific to Crypto
- **Cross-sectional > time-series for crypto** (Rohrbach et al.) — ranking across assets works better than absolute momentum on individual assets
- **Winner-concentrated effect** (Han et al., 2023) — the long (winner) side drives most of the profit; losers often rebound and inflict losses. **Implication: winner-only variant may be superior to long/short**
- **Short formation periods work** — unlike equities (where 3–12 month formation is standard), crypto momentum works at 1-hour to 30-day formation periods
- **Higher volatility = higher Sharpe** (Rohrbach et al.) — crypto's extreme volatility is an *advantage* for momentum, not a problem
- **Momentum crashes exist** (Grobys, 2025) — severe tail losses documented. Risk-managed variant (volatility-scaling) partially mitigates this
- **Realistic assumptions matter** (Han et al., 2023) — many portfolios that look profitable in theory are actually liquidated when you account for fees and daily price fluctuations. **We must validate with our actual fee tier (10 bps round-trip)**

### 1.3 Why This Candidate Is Different from Our Failures
| Previous Failure | Why G Avoids It |
|---|---|
| RAME: edge too small per trade | Momentum moves at 1h horizon are 50–300+ bps — well above fee floor |
| LOB: fee economics killed it | Per-trade moves are an order of magnitude above 10 bps fees |
| CointPairs: 0.05 trades/day | 20+ pairs × hourly rebalancing = many trades per day by design |
| CointPairs: single-leg exposure | Each trade is independent (not a paired leg). Winner-only variant eliminates short-side risk entirely |
| RAME: tautological ML | No ML needed for base version — pure return ranking. ML enhancements (Candidate I) deferred until base validates |

---

## Part 2: Architecture

```
┌─────────────────────────────────────────────────────────┐
│         CROSS-SECTIONAL MOMENTUM ARCHITECTURE            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Freqtrade Strategy (1h candles)                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  bot_loop_start() or populate_indicators():      │   │
│  │    For each pair in universe:                    │   │
│  │      Load OHLCV via DataProvider                 │   │
│  │      Compute formation-period return             │   │
│  │    Rank all pairs by return                      │   │
│  │    Store ranking in custom_info dict             │   │
│  │                                                  │   │
│  │  populate_entry_trend():                         │   │
│  │    IF this pair is in top N (winners):            │   │
│  │      enter_long = 1                              │   │
│  │    IF this pair is in bottom N (losers):          │   │
│  │      enter_short = 1  [or skip — winner-only]    │   │
│  │                                                  │   │
│  │  Exit: holding-period time stop                  │   │
│  │        + trailing stop for crash protection       │   │
│  │        + ROI target (optional)                   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  SHARED with LiqCascade (if running concurrently):      │
│  - DigitalOcean droplet infrastructure                  │
│  - Docker compose setup (new profile: xsmom)            │
│  - Separate Freqtrade instance + config + DB            │
│                                                         │
│  NO sidecar needed. NO special data source.             │
│  Pure OHLCV strategy running natively in Freqtrade.     │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Key Design Decisions

**Universe:** Start with 20 liquid Binance Futures perpetuals. Use VolumePairList or StaticPairList. Exclude stablecoins, leverage tokens, and pairs with < $10M 24h volume.

**Timeframe:** 1h candles. Formation period and holding period as hyperparameters.

**Formation periods to test:** 1h, 4h, 24h, 7d (168h), 30d (720h)
**Holding periods to test:** 1h, 4h, 24h, 7d

**N (number of winners/losers):** Top/bottom 3–5 out of 20. Hyperparameter.

**Variants to build and compare (in order):**
1. **V01 — Long/Short baseline:** Long top N, short bottom N, hold for holding period
2. **V02 — Winner-only:** Long top N only, no short side (per Han et al. finding that losers rebound)
3. **V03 — Risk-managed:** V02 + volatility-scaled position sizing (reduce exposure when recent cross-sectional volatility is high)

---

## Part 3: Phase Plan

### Phase 0: Data Download + Exploration (Day 1)

**Goal:** Download historical data, explore cross-sectional return distributions, confirm that momentum dispersion exists at our target timeframes.

**Tasks:**
1. Download 1h OHLCV data for 20+ Binance Futures pairs, 2022–2025 (covers bull, bear, and ranging markets)
   ```
   freqtrade download-data --config config/config_xsmom.json --timerange 20220101-20260101 --timeframe 1h
   ```
2. Compute formation-period returns for each pair at multiple horizons (1h, 4h, 24h, 7d, 30d)
3. Compute cross-sectional dispersion at each horizon: std of returns across pairs per time step
4. Compute autocorrelation of cross-sectional rankings: do winners persist as winners?
5. Visualize: return heatmap (pairs × time), dispersion time series, ranking persistence

**Go/No-Go for Phase 1:**
- Cross-sectional dispersion is consistently > 50 bps at 1h horizon (enough room above fees)
- Ranking persistence (autocorrelation of ranks) is positive and statistically significant at target formation periods
- At least 15 pairs have continuous data coverage 2022–2025

**If dispersion < 50 bps at all horizons:** The momentum opportunity may be too small at our timeframes. Test longer formation periods before abandoning.

---

### Phase 1: Backtest Baseline (Days 2–3)

**Goal:** Implement V01 (long/short) and V02 (winner-only) in Freqtrade and backtest with fee-inclusive simulation.

**Tasks:**
1. Create `user_data/strategies/XSMomentumStrategy_V01.py`:
   - `informative_pairs()`: return all 20 pairs at 1h timeframe
   - `bot_loop_start()` or `populate_indicators()`: load all pair data, compute formation returns, rank, store in `custom_info`
   - `populate_entry_trend()`: enter long if pair is in top N; enter short if in bottom N
   - Exit: pure time stop (holding period) + trailing stop loss for crash protection
2. Create `config/config_xsmom.json` with 20 pairs, futures mode, 10 bps fee assumption
3. Backtest V01 across formation/holding period grid:
   ```
   freqtrade backtesting --strategy XSMomentumStrategy_V01 --config config/config_xsmom.json --timerange 20220101-20250101 --timeframe 1h --export trades
   ```
4. Run fee economics sweep (Technique 7.3): confirm profitable operating points exist at 10 bps
5. Implement V02 (winner-only): duplicate V01 but skip short entries
6. Compare V01 vs V02: if V02 is comparable or better (per Han et al.), proceed with V02

**Go/No-Go for Phase 2:**
- At least one formation/holding combination is profitable after 10 bps fees
- Profit factor > 1.2
- Trade frequency > 1 trade/day average
- Results are not concentrated in a single market regime (check: 2022 bear, 2023 range, 2024 bull separately)
- **Check Lesson #10:** Do short entries mirror long entries in P&L? If longs are profitable but shorts are equally unprofitable, the signal may be a bull-market artifact

**CRITICAL: Run the fee sweep (Technique 7.3) BEFORE building Phase 2 infrastructure.** If no profitable operating point exists at 10 bps, STOP. See Lesson #7.

---

### Phase 2: Risk-Managed Variant + Hyperopt (Days 4–5)

**Goal:** Implement V03 (risk-managed), optimize parameters, validate out-of-sample.

**Tasks:**
1. Implement V03: volatility-scaled position sizing
   - Compute rolling cross-sectional volatility (std of returns across pairs over trailing 24h)
   - Scale stake_amount inversely with volatility: high vol → smaller positions
   - This directly addresses momentum crash risk
2. Hyperopt on 2022–2024 (in-sample):
   - Formation period, holding period, N (number of winners), volatility scaling factor, trailing stop distance
   ```
   freqtrade hyperopt --strategy XSMomentumStrategy_V03 --config config/config_xsmom.json --hyperopt-loss SharpeHyperOptLoss --timerange 20220101-20250101 --epochs 200
   ```
3. Out-of-sample validation on 2025:
   - Run best parameters on 2025 data
   - Compare to in-sample performance — expect some degradation but should remain profitable
4. Walk-forward validation: train on rolling 6-month windows, test on subsequent 1-month windows, roll forward

**Go/No-Go for Phase 3:**
- Out-of-sample Sharpe > 1.0
- Out-of-sample profit factor > 1.3
- Walk-forward: profitable in at least 4 of 6 test windows
- Parameters are not at extreme edges of search ranges (overfitting signal)
- Trade frequency remains > 1 trade/day in out-of-sample period

---

### Phase 3: Dry-Run Deployment (Week 2+)

**Goal:** Deploy to droplet alongside LiqCascade, accumulate forward-testing data.

**Tasks:**
1. Add `xsmom` profile to Docker compose on droplet
2. Deploy as separate Freqtrade instance (own DB, own port, own config)
3. Monitor for 2+ weeks: compare dry-run results to backtest expectations
4. Confirm no interference with LiqCascade operation

**Go/No-Go for Phase 4 (live capital):**
- 2+ weeks dry-run data
- Total return within 30% of backtest expectation
- Trade frequency within 30% of backtest frequency
- No single week loss > 5% of portfolio
- Sidecar (LiqCascade) and momentum strategy running stably on same droplet

---

## Part 4: What Not To Repeat

| Anti-pattern | Why it's relevant here |
|---|---|
| Building infrastructure before fee sweep | Run Technique 7.3 in Phase 1 before any Phase 2 work. LOB Microstructure lesson. |
| Trusting bull-market backtests | Check 2022 bear performance independently. CointPairs Lesson #10. |
| Ignoring trade frequency | Must validate > 1 trade/day. CointPairs died at 0.05 trades/day. |
| Using ML before validating base case | V01/V02 are pure ranking — no ML. Only add ML (signatures, Candidate I) after base case validates. RAME lesson. |
| Optimizing exits before checking entries | If V01 loses money, check whether the ranking signal has forward predictive power at all before tuning stops. RAME Lesson #2. |
| Single-leg directional exposure in market-neutral framing | V02 (winner-only) is explicitly directional long-only. Don't pretend it's market-neutral. If we want market-neutral, V01 is the right variant — but test V02 separately because Han et al. show winners drive the profit. |

---

## Part 5: File Locations (Planned)

| File | Purpose | Status |
|---|---|---|
| `user_data/strategies/XSMomentumStrategy_V01.py` | Long/short baseline | To build (Phase 1) |
| `user_data/strategies/XSMomentumStrategy_V02.py` | Winner-only variant | To build (Phase 1) |
| `user_data/strategies/XSMomentumStrategy_V03.py` | Risk-managed variant | To build (Phase 2) |
| `config/config_xsmom.json` | Strategy config (20 pairs, futures, 1h) | To build (Phase 0) |
| `user_data/scripts/xsmom_phase0_exploration.py` | Phase 0 data exploration | To build (Phase 0) |
| `user_data/info/CrossSectionalMomentum_Dev_Plan.md` | THIS FILE | Active |
| `user_data/info/AlgoTrading_Research_Log.md` | Project-wide context | Active |

---

## Part 6: Reference Material

### 6.1 Key Papers
- **Drogen, Hoffstein & Otte (SSRN 2023):** "Cross-sectional Momentum in Cryptocurrency Markets" — 30-day/7-day formation/holding, consistent excess returns vs BTC
- **Han, Kang & Ryu (SSRN 2023):** "Time-Series and Cross-Sectional Momentum: Comprehensive Analysis under Realistic Assumptions" — critical paper; shows winners drive profit, losers rebound, many portfolios liquidated under realistic fees
- **ScienceDirect (2025):** "Cryptocurrency market risk-managed momentum strategies" — volatility-scaling for crash protection
- **Rohrbach et al. (2017):** High-frequency momentum on crypto — hourly formation tested, cross-sectional preferred for crypto
- **Grobys (2025):** Momentum crashes in crypto — documents severe tail losses, motivates risk-managed variant

### 6.2 Freqtrade Implementation References
- **Cross-pair ranking:** GitHub issue #6452 — use `DataProvider` + `custom_info` dict
- **Informative pairs:** Freqtrade docs strategy-customization + InformativeSample strategy
- **Advanced strategy features:** `bot_loop_start()`, `custom_info`, `confirm_trade_entry()`

### 6.3 Candidate I (Future)
If this strategy validates, Candidate I (Path Signature-Enhanced Momentum) would replace the simple return-based ranking with signature-derived features. This is documented in the Research Log (Candidates E, G, and I entries). **Do not implement Candidate I features in this codebase.** Build G clean and standalone first.

---

*Document maintained by: Claude + project co-developer*
*Last updated: 2026-03-22 — Initial creation*
