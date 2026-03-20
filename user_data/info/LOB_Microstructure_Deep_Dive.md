# LOB Microstructure Strategy — Deep Dive
## Version 1 | Started: 2026-03-20 | Status: ACTIVE — Phase 0 (Data Collection)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**
> Also read `user_data/info/AlgoTrading_Research_Log.md` for project-wide context, roles, and objectives.

### Current Status
- **Phase:** 0 — LOB Data Collection (ACTIVE — run historical download to populate training data)
- **Last completed:** All Phase 0 code built and committed. `lob_features.py`, `lob_collector.py`, `lob_historical.py`, `Dockerfile.lob`, docker-compose service `lobcollect` all in place.
- **Next immediate step:** Run the historical downloader to collect 30+ days of training data, then proceed to Phase 1.
- **Open decisions:** None blocking.

### Run Historical Download (do this now)
```
# Default: last 30 days, BTC + ETH (~8 GB download, outputs to sidecar/data/lob_raw/)
python sidecar/lob_historical.py

# Longer history for better regime diversity (recommended: 90 days)
python sidecar/lob_historical.py --start 2024-12-01 --end 2025-03-19

# Check output
ls sidecar/data/lob_raw/BTCUSDT/
```

### Key Commands
```
# Run freqtrade CLI commands
docker compose run --rm freqtrade <command> --config config/config-dev.json

# Start LOB collector (once built)
docker compose --profile lobcollect up -d

# Check LOB collector logs (once deployed)
docker compose --profile lobcollect logs --tail 50 lob_collector

# Verify data files are being written
ls -lh sidecar/data/lob_raw/
```

### File Locations
| File | Status | Purpose |
|---|---|---|
| `sidecar/lob_features.py` | **BUILT** | Feature engineering functions — pure, no I/O, shared by sidecar + training |
| `sidecar/lob_collector.py` | **BUILT** | Live WebSocket LOB capture (bookTicker + aggTrade), 1s snapshots, Parquet output |
| `sidecar/lob_historical.py` | **BUILT** | Historical data downloader — data.binance.vision bookTicker + aggTrades → same Parquet schema |
| `sidecar/Dockerfile.lob` | **BUILT** | Docker image for live collector |
| `sidecar/logs/lob_collector.log` | Auto-created | Sidecar health log |
| `sidecar/data/lob_raw/` | Auto-created | 1-second LOB feature snapshots (Parquet, partitioned by symbol/date) |
| `sidecar/data/download_cache/` | Auto-created | Cached ZIP downloads — safe to delete after processing |
| `user_data/models/lob_catboost_v01.cbm` | To create (Phase 1) | Trained CatBoost model |
| `user_data/data/lob_signal_data.json` | To create (Phase 2) | Live inference output — read by Freqtrade strategy |
| `user_data/strategies/LOBMicroStrategy_V01.py` | To build (Phase 2) | Freqtrade strategy |
| `user_data/info/LOB_Microstructure_Deep_Dive.md` | THIS FILE | Authoritative reference |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Project-wide context and strategy registry |

---

## Part 1: Why We're Here

### 1.1 Research Context

This project is Candidate A from the first sourcing sweep in `AlgoTrading_Research_Log.md`. The source paper is:

> **"Explainable Patterns in Cryptocurrency Microstructure"**
> Bieganowski & Ślepaczuk, arXiv 2602.00776, January 2026

The paper uses limit order book (LOB) features and CatBoost with a direction-aware loss function to predict 3-second forward mid-price returns on Binance Futures perpetual contracts across 5 assets (BTC, LTC, ETC, ENJ, ROSE). It passed our 7-point evaluation filter (5/7 PASS, 2/7 CONDITIONAL PASS) and was the top recommendation from Sweep #1.

### 1.2 Why This Is Different From RAME

RAME failed because it tried to predict market regimes from lagged indicator data — the edge per trade was too small (+0.087% mean at 4h), entry was always late, and the signal oscillated at short timeframes.

This project operates on an entirely different alpha source:

- **RAME:** Lagged indicator-based regime classification → route to sub-strategy
- **LiqCascade:** Detect mechanical market events (forced liquidations) in real time → enter the cascade
- **LOB Microstructure:** Measure real-time order book state (imbalance, spread pressure, adverse selection) → predict next 3 seconds of price direction

The LOB signal is not lagged. It reflects the current state of supply and demand at the bid and ask — the information that market makers and HFTs already use. Order flow imbalance predicting short-term price impact is not a statistical artifact; it is the mechanism by which prices move in a continuous double auction (Kyle, 1985).

### 1.3 Complementarity with LiqCascade

These two strategies are from genuinely different alpha sources:

| Dimension | LiqCascade | LOB Microstructure |
|---|---|---|
| Signal type | Discrete event detection | Continuous state measurement |
| Frequency | Rare (hours between events) | Continuous (every few seconds) |
| Edge source | Mechanical forced liquidation | Order flow imbalance + adverse selection |
| Prediction horizon | 15–30 minutes | 3–15 seconds |
| Capital utilization | Idle most of the time | Potentially high utilization |

One risk: during a LiqCascade event, LOB features will also fire strongly (the cascade creates extreme order flow imbalance). The two strategies may enter simultaneously — correlated exposure. Monitor and manage if concurrent positions become problematic.

---

## Part 2: Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              LOB MICROSTRUCTURE ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Binance Futures WebSocket (public, free)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  btcusdt@depth@100ms  →  local order book           │    │
│  │  btcusdt@aggTrade     →  trade buffer               │    │
│  │  (same for ethusdt)                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│              lob_collector.py (sidecar)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Every 1 second:                                    │    │
│  │    1. Snapshot top-5 bid/ask levels                 │    │
│  │    2. Compute features via lob_features.py          │    │
│  │       (imbalance, spread, VWAP deviations)          │    │
│  │    3. [Phase 2+] Run CatBoost inference             │    │
│  │    4. Write to lob_signal_data.json                 │    │
│  │                                                     │    │
│  │  Continuously:                                      │    │
│  │    Append 1-second snapshot to Parquet files        │    │
│  │    (sidecar/data/lob_raw/ — for training data)      │    │
│  └─────────────────────────────────────────────────────┘    │
│                         │                                   │
│              lob_signal_data.json                           │
│                         │                                   │
│  Freqtrade Strategy (LOBMicroStrategy_V01.py, 5m candles)   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  populate_indicators():                             │    │
│  │    Read signal file (freshness check ≤ 5s stale)   │    │
│  │    Apply regime context (CRISIS gate + EMA200)      │    │
│  │                                                     │    │
│  │  populate_entry_trend():                            │    │
│  │    Enter when prediction exceeds threshold          │    │
│  │    Direction from sign of prediction                │    │
│  │                                                     │    │
│  │  Exit: ROI table + ATR stop + time stop             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  SHARED INFRASTRUCTURE (reused from LiqCascade):           │
│  - CRISIS gate (ATR p90 on 1h informative pair)            │
│  - EMA200 macro trend filter (1h)                          │
│  - DigitalOcean droplet + Docker Compose                   │
│  - Atomic JSON write pattern (temp file → rename)          │
└─────────────────────────────────────────────────────────────┘
```

**Design principle:** The sidecar and the Freqtrade strategy are loosely coupled via a JSON signal file — the same pattern proven with LiqCascade. The sidecar owns all real-time data capture and inference. The strategy is a thin consumer that translates the signal into trades.

---

## Part 3: Paper Summary

### 3.1 Data
- Binance Futures perpetual contracts: BTC, LTC, ETC, ENJ, ROSE
- 1-second frequency LOB snapshots + trade data
- January 2022 – October 2025 (~3.8 years)
- Both order book depth updates and aggregated trade data

### 3.2 Feature Engineering (three families, all top-of-book)

**Family 1 — Top-of-book metrics:**
- Mid price: `(best_bid + best_ask) / 2`
- Relative spread: `(best_ask - best_bid) / mid`
- L1 bid volume, L1 ask volume (absolute and ratio)

**Family 2 — Order flow / trade imbalance:**
- Net signed trade volume over rolling window (buys − sells, in USD)
- Cumulative order flow imbalance
- Captures the directional pressure from market takers

**Family 3 — VWAP-to-mid deviations:**
- Buy VWAP deviation: how far above mid recent buy trades occurred
- Sell VWAP deviation: how far below mid recent sell trades occurred
- Captures adverse selection pressure — market makers moving quotes away from informed flow

**Deep book levels deliberately excluded.** The paper found that deep book features add noise without improving predictive power. Top-of-book is sufficient and more portable across assets.

### 3.3 Model
- **Algorithm:** CatBoost (gradient-boosted decision trees)
- **Custom objective:** GMADL (Generalized Mean Absolute Directional Loss)
  - Standard MSE: treats a correct-direction small move the same as a wrong-direction small move
  - GMADL: rewards correct direction prediction, weighted by move magnitude — aligns loss function with trading P&L
- **Target:** `log(mid_{t+3s} / mid_t)` — 3-second forward log return of mid price
- **Validation:** Rolling walk-forward cross-validation with temporal purge gap between train and test splits (prevents leakage)
- **No feature scaling:** CatBoost is scale-invariant

### 3.4 Key Results
- Feature importance is **stable and portable** across all 5 assets via SHAP analysis — order flow imbalance consistently dominates
- Taker execution backtest: profitable across all assets
- Maker execution backtest: profitable in calm markets, **massive adverse selection losses during Oct 10, 2025 flash crash**
- **Conclusion for us:** Taker execution only. Never attempt maker execution.

### 3.5 What the Paper Did Not Test
- Sub-1-second inference latency impact
- Signal survival at timeframes > 3 seconds (we must test this)
- Execution on a standard VPS (not a co-located server)
- Integration with an off-the-shelf trading framework like Freqtrade

---

## Part 4: Our Adaptation and Key Differences

| Dimension | Paper | Our Implementation |
|---|---|---|
| Feature computation frequency | 1-second | 1-second (matched) |
| Prediction horizon | 3-second | 3s → test survival at 5s, 15s, 1m, 5m |
| Execution framework | Custom Python | Freqtrade strategy via sidecar signal file |
| Historical data | Jan 2022 – Oct 2025 | Forward-collected only (no free historical LOB source) |
| Backtesting | Academic walk-forward CV | Phase 1: offline validation on collected data; Phase 2: live dry-run |
| Assets | BTC, LTC, ETC, ENJ, ROSE | BTC/USDT:USDT + ETH/USDT:USDT initially; expand later |
| Execution type | Taker (conservative) | Market orders (taker) — same |

### 4.1 Critical Open Question: Timeframe Survival

The paper's edge is at the 1–3 second horizon. Freqtrade's minimum timeframe is 1 minute. Two execution paths:

**Path A (preferred): Signal survives at 1m–5m**
Standard Freqtrade integration. Signal file updated every second by sidecar; Freqtrade reads it on each 5m candle close. Architecturally simple.

**Path B (bigger change): Signal dies above ~15s**
The edge requires sub-minute execution. The sidecar must place orders directly via Binance API, bypassing Freqtrade's candle logic entirely. This is a significant architectural change — discuss before implementing if Phase 1 testing indicates this path.

**Phase 1 explicitly tests signal survival** before we commit to either path.

---

## Part 5: Phase Implementation Plan

---

### Phase 0: LOB Data Collection Sidecar — IN PROGRESS

**Goal:** Build and deploy a sidecar that captures LOB + trade data from Binance Futures WebSocket, stores raw snapshots as Parquet files for model training, and runs 24/7 on the droplet without disturbing LiqCascade.

**Deliverables:**
1. `sidecar/lob_collector.py` — WebSocket connection, local order book maintenance, 1-second snapshot loop, Parquet write
2. `sidecar/lob_features.py` — Feature engineering functions (shared by sidecar + offline training pipeline)
3. Docker Compose service `lob_collector` under profile `lobcollect`

**Data storage estimate:**
- ~86,400 snapshots/day/symbol × 2 symbols = ~172,800 rows/day
- ~50 features × 8 bytes/row = ~400 bytes/row → ~69 MB/day uncompressed
- Parquet compression → ~15–20 MB/day
- 2 weeks = ~200–300 MB total. Negligible on 30 GB droplet.

**Parquet schema (one row per 1-second snapshot):**
```
timestamp (UTC), symbol, mid, spread_rel, bid_vol_l1, ask_vol_l1,
ofi_net (order flow imbalance), cum_ofi, buy_vwap_dev, sell_vwap_dev
```

**Go/No-Go for Phase 1:**
| Criterion | Threshold |
|---|---|
| Sidecar uptime | Stable for 48+ hours |
| Data quality | Mid price matches Binance spot check, spread always positive, no NaN features |
| LiqCascade impact | No performance degradation, no port conflicts |
| Data volume | Files being written at expected rate (~15 MB/day/symbol) |

**Key discovery (2026-03-20):** Binance's public data portal (`data.binance.vision`) provides free historical `bookTicker` and `aggTrades` downloads for USD-M Futures going back to ~2020. Both contain exactly the fields needed for our feature set. This eliminates the 14-day live collection wait — months of training data are available immediately via `lob_historical.py`.

**Note on bookTicker data quality:** Files from January 2024 onward contain rows interleaved out of chronological order (known Binance bug, unresolved). The historical script handles this by sorting on `(event_time, update_id)` after load.

**Results:**
- Code complete: `lob_features.py`, `lob_collector.py`, `lob_historical.py`, `Dockerfile.lob`, docker-compose service
- Historical download not yet run — **do this before proceeding to Phase 1**

---

### Phase 1: Feature Validation + Model Training

**Goal:** Validate the paper's feature engineering on our collected data, train a first CatBoost model with GMADL objective, and — critically — determine at which aggregation level the predictive edge survives.

**Pre-requisite:** At least 7 days (preferably 14) of Phase 0 data collected.

**Tasks:**
1. Pull Parquet data from droplet to local machine
2. Compute all features offline using `lob_features.py`
3. Verify feature distributions match paper:
   - OFI roughly symmetric around zero
   - Spread always positive, mean in range 0.001%–0.05%
   - VWAP deviations centered near zero
   - If distributions look wrong, debug the feature computation before training
4. Train CatBoost with GMADL objective:
   - Walk-forward CV: 70% train / 15% validation / 15% test
   - Temporal purge gap: discard 5 minutes between splits to prevent leakage
   - Tune iterations, depth, learning_rate via early stopping on validation set
5. Signal survival test (the critical gate):
   - Aggregate 1-second predictions to 5s, 15s, 1m, 5m windows (mean of predictions in window)
   - At each aggregation level, compute: directional accuracy, GMADL score, simulated P&L with fixed-size position + taker fee
   - Record the finest aggregation level at which directional accuracy drops to ≤ 51% — that is the execution boundary

**GMADL Implementation:**
```python
# Custom CatBoost objective
class GMAdlObjective:
    def calc_ders_range(self, approxes, targets, weights):
        # Gradient: direction-weighted MAE
        # grad = -sign(target) * |target| if sign(approx) != sign(target) else 0
        ...
```

**Go/No-Go for Phase 2:**
| Criterion | Threshold |
|---|---|
| Directional accuracy (out-of-sample) | > 52% at the target execution timeframe |
| Signal survival | Edge identifiable at ≥ 5s aggregation (Path A viable) |
| Feature importance | Order flow imbalance in top 3 features (validates paper replication) |
| No data leakage | Accuracy on training set not suspiciously > test set by > 15% |

**If signal dies at all timeframes > 1s:** Archive as "edge too fast for our stack." Do not attempt Path B (direct order placement) without explicit discussion — it is a fundamentally different system requiring order management, risk controls, and latency optimization outside Freqtrade's scope.

**Results (to be filled in):**
> *[Awaiting Phase 1 completion]*

---

### Phase 2: Freqtrade Integration + Dry-Run

**Goal:** Extend the sidecar to run live inference and write predictions to a signal file; build the Freqtrade strategy to consume it; begin dry-run on the droplet.

**Pre-requisite:** Phase 1 model trained, target execution timeframe identified.

**Tasks:**
1. Extend `lob_collector.py` to load trained model and run inference after each 1-second feature computation
2. Write prediction to `user_data/data/lob_signal_data.json` (atomic write — same pattern as LiqCascade):
```json
{
  "timestamp": "...",
  "predictions": {
    "BTC/USDT:USDT": {"prediction": 0.00042, "signal": "LONG", "confidence": 0.67},
    "ETH/USDT:USDT": {"prediction": -0.00018, "signal": "SHORT", "confidence": 0.54}
  }
}
```
3. Build `user_data/strategies/LOBMicroStrategy_V01.py`:
   - Read `lob_signal_data.json` in `populate_indicators()`, stale threshold = 5s
   - Entry: signal exceeds threshold (calibrated from Phase 1 test results)
   - Direction: sign of prediction
   - Regime context: reuse CRISIS gate + EMA200 from LiqCascade (same implementation)
   - Exit: ROI table (calibrate from Phase 1 hold-time analysis) + ATR stop + time stop
   - Leverage: 4x (trend-aligned), 2x (counter-trend)
4. Add `LOBMicroStrategy_V01` as new Docker service under `--profile lobstrategy`
5. Begin dry-run alongside LiqCascade

**Go/No-Go for Phase 3:**
| Criterion | Threshold |
|---|---|
| Trade count | ≥ 20 |
| Profit factor | > 1.0 |
| Win rate | > 45% |
| Sidecar inference latency | < 500ms per cycle (measure and log) |
| LiqCascade interference | None |

**Results (to be filled in):**
> *[Awaiting Phase 2 completion]*

---

### Phase 3: Optimisation + Multi-Pair Expansion

**Goal:** Optimise signal threshold, exit parameters, and expand to additional pairs.

**Pre-requisite:** Phase 2 dry-run meets go/no-go criteria.

**Tasks:**
1. Analyse dry-run trades: which features drove the best/worst entries? (SHAP on individual trades if needed)
2. Hyperopt signal threshold and hold time
3. Retrain model periodically (weekly rolling window)
4. Add pairs — paper shows features are portable, but validate per-pair before adding to live roster
5. Assess concurrent operation with LiqCascade: are simultaneous entries correlated? If yes, add position overlap guard

**Results (to be filled in):**
> *[Awaiting Phase 3 completion]*

---

## Part 6: Feature Engineering Reference

Full reference for `lob_features.py` implementation. All features use relative/ratio measures for cross-asset portability.

### 6.1 Inputs Required Per 1-Second Snapshot
- Order book: top-5 bid levels `(price, qty)`, top-5 ask levels `(price, qty)`
- Trade buffer: all `aggTrade` messages in the past N seconds (N = rolling window, e.g. 30s)

### 6.2 Feature Definitions

```python
# Mid price
mid = (best_bid_price + best_ask_price) / 2

# Relative spread (scale-invariant)
spread_rel = (best_ask_price - best_bid_price) / mid

# L1 volumes
bid_vol_l1 = best_bid_qty   # in base currency
ask_vol_l1 = best_ask_qty

# L1 volume imbalance ratio
vol_imbalance = (bid_vol_l1 - ask_vol_l1) / (bid_vol_l1 + ask_vol_l1 + 1e-9)

# Order flow imbalance (signed net trade volume in rolling window)
# BUY trades = positive (takers lifting asks = upward pressure)
# SELL trades = negative (takers hitting bids = downward pressure)
ofi_net = sum(qty * price for buy_trades) - sum(qty * price for sell_trades)

# Cumulative OFI (longer-horizon directional pressure)
cum_ofi = rolling_sum(ofi_net, longer_window)

# Buy VWAP deviation (how far above mid recent buy trades occurred)
buy_vwap = sum(price * qty for buy_trades) / sum(qty for buy_trades)
buy_vwap_dev = (buy_vwap - mid) / mid   # positive = buys above mid (aggressive buyers)

# Sell VWAP deviation (how far below mid recent sell trades occurred)
sell_vwap = sum(price * qty for sell_trades) / sum(qty for sell_trades)
sell_vwap_dev = (sell_vwap - mid) / mid  # negative = sells below mid (aggressive sellers)
```

### 6.3 Feature Computation Windows
Following the paper, compute OFI and VWAP features over multiple rolling windows and include all as separate features:
- Short window: 5 seconds
- Medium window: 30 seconds
- Long window: 120 seconds

This gives the model temporal structure without manually engineering lags.

---

## Part 7: Key Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-20 | Use sidecar + signal file pattern (same as LiqCascade) | Proven architecture in our stack. Loose coupling between data capture and execution. |
| 2026-03-20 | Taker execution only | Paper's maker backtest failed during flash crash. Adverse selection risk unacceptable. |
| 2026-03-20 | Top-of-book features only (exclude deep book) | Paper's finding: deep book adds noise. Portability across assets requires shallow features. |
| 2026-03-20 | Test signal survival before committing to execution path | Paper's edge is 1–3s. We cannot assume it survives Freqtrade's 1m minimum. Explicit test in Phase 1 gates the rest of development. |
| 2026-03-20 | Reuse CRISIS gate + EMA200 from LiqCascade | Already validated as a regime context filter. No reason to re-engineer. |
| 2026-03-20 | Start with BTC/ETH only | Match LiqCascade pairs for cross-strategy analysis. Paper shows features are portable — expand after Phase 2 validation. |
| 2026-03-20 | Use `@bookTicker` stream (not `@depth5@100ms`) | bookTicker gives L1 as complete event-driven snapshots — no diff-based local order book management required. Simpler and more reliable. |
| 2026-03-20 | Historical data via data.binance.vision — no 14-day wait | bookTicker + aggTrades freely available back to 2020. lob_historical.py downloads, resamples to 1s, computes features in same schema as live collector. |
| 2026-03-20 | Vectorized feature computation (pandas rolling) for historical pipeline | Row-by-row Python loop over 86,400 rows/day would be slow. Vectorized rolling ops on 1-second aggregated data is fast and correct. Day-boundary accuracy handled via carry-over trade buffer. |

---

## Part 8: What Not To Re-Introduce

Anti-patterns from prior projects that are specifically relevant here. Re-read before any major design decision.

| Anti-pattern | Why it's relevant here |
|---|---|
| **Training model to predict derived labels** | Target must be forward mid-price return, not a label computed from features. If test accuracy is suspiciously high (> 80%), check for data leakage before celebrating. |
| **Optimising exits before validating entries** | If early dry-run results are poor, first check whether the Phase 1 signal survival test was actually passed. Don't tune stops when the entry signal may have no edge. |
| **Adding regime complexity before validating base case** | Get CatBoost on core features working first. Regime filters, multi-pair, and re-training schedules come after the base case is confirmed. |
| **Ignoring execution latency** | The paper's edge is at 1–3 seconds. If VPS inference latency exceeds ~200ms per cycle, the signal may arrive too late. Measure and log latency from Phase 0 onwards. |
| **Confusing accuracy with edge** | A model predicting 55% directional accuracy sounds good. But if the 45% wrong predictions are larger moves than the 55% correct ones, the model has negative expected value. Always evaluate with simulated P&L including fees. |
| **Maker execution** | Flash crash analysis in the paper is decisive: maker strategy suffers catastrophic adverse selection during extreme events. We trade as taker. |

---

## Part 9: Open Research Questions

Questions to be answered by evidence, not assumptions.

1. **Signal survival:** At what aggregation level (5s, 15s, 1m, 5m) does the directional edge disappear? Is 5m Freqtrade integration viable, or do we need sub-minute execution?

2. **GMADL vs standard MSE:** Does the custom loss function materially improve out-of-sample performance vs simply using MSE as the CatBoost objective? Worth quantifying before committing to the custom implementation complexity.

3. **Optimal rolling window length:** The paper uses multiple windows. Is the model sensitive to window length, or does it learn robust representations regardless?

4. **Regime interaction:** Does LOB signal quality degrade during CRISIS regimes (high ATR)? If so, does the CRISIS gate from LiqCascade cleanly handle this, or does the LOB strategy need its own volatility filter?

5. **LiqCascade correlation:** When LiqCascade fires (genuine liquidation cascade), do LOB features simultaneously produce a strong signal? If yes, are we taking double correlated exposure, or do the signals reinforce each other with genuine independence?

6. **Retraining frequency:** How fast does the model decay without retraining? Is a weekly rolling window sufficient, or does the model need more frequent updates to stay calibrated?

7. **Multi-pair portability:** The paper claims feature importance is stable across assets. Does this hold for SOL and BNB on our collected data, or does each pair require a separate model?

---

*Document maintained by: Claude Sonnet 4.6 + project co-developer*
*Last updated: 2026-03-20 — Phase 0 code complete. lob_features.py, lob_collector.py, lob_historical.py built and committed. Historical download path discovered (data.binance.vision) — eliminates 14-day live collection wait. Ready to run historical download and proceed to Phase 1.*
