# LOB Microstructure Strategy — Development Plan
## Candidate A from AlgoTrading Research Log
## Created: 2026-03-20 | Status: PRE-DEVELOPMENT (Data Collection Phase)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Also read `user_data/info/AlgoTrading_Research_Log.md` for project-wide context, roles, and objectives.

### What This Project Is
We are implementing a trading strategy based on arXiv paper 2602.00776 ("Explainable Patterns in Cryptocurrency Microstructure" by Bieganowski & Ślepaczuk, Jan 2026). The paper uses CatBoost on limit order book (LOB) features to predict short-horizon crypto returns on Binance Futures. It was evaluated and approved as Candidate A in our Research Log (Section 4.3).

### Current Phase
- **Phase:** 0 — LOB Data Collection Sidecar
- **Last completed:** [Not started]
- **Next immediate step:** Build the LOB data collection sidecar process
- **Blocking issues:** None

### Key Context from Research Log
- We are Co-Investigators, Co-Strategists, and Co-Developers. Claude pushes back on bad ideas, proposes alternatives, and checks the developer's reasoning. See Research Log Section 1.
- Our objective is high-ROI, high-frequency crypto trading systems. See Research Log Section 2.
- We already have a running LiqCascade strategy on a DigitalOcean droplet using a WebSocket sidecar pattern — this project follows the same architectural pattern.
- The RAME project (ARCHIVED) taught us critical lessons: ML accuracy ≠ trading edge, entry quality > exit optimization, structural alpha > statistical alpha. See Research Log Section 8.

---

## Part 1: Paper Summary

### 1.1 What the Paper Does
- Engineers features from Binance Futures LOB snapshots and trade data at 1-second frequency
- Trains CatBoost with a direction-aware loss function (GMADL) to predict 3-second forward mid-price log returns
- Validates via walk-forward cross-validation with temporal purging
- Tests on 5 assets spanning large-cap to small-cap (BTC, LTC, ETC, ENJ, ROSE)
- Shows stable, portable feature importance across all assets via SHAP analysis
- Validates tradability via conservative taker backtest and maker backtest
- Stress-tests during Oct 10, 2025 flash crash

### 1.2 Key Features Used (from paper Section 3)
Three feature families, all computed from top-of-book data:

1. **Top-of-book metrics:** mid price, spread (as ratio to mid), L1 bid/ask volumes
2. **Order flow / trade imbalance:** net traded volume (signed), cumulative order flow
3. **VWAP-to-mid deviations:** separate for buy and sell trades — captures how far recent trading activity occurred from midpoint

Deep order book levels are deliberately excluded. All features use relative/ratio measures for cross-asset portability.

### 1.3 Model Details
- **Model:** CatBoost (gradient-boosted decision trees)
- **Objective:** GMADL (Generalized Mean Absolute Directional Loss) — rewards correct direction prediction weighted by move magnitude
- **Target:** `log(mid_{t+3s} / mid_t)` — 3-second forward log return
- **Validation:** Rolling walk-forward CV with purge gap between train and test sets
- **No feature scaling needed** — tree models are scale-invariant

### 1.4 What the Paper Proved
- Feature rankings and SHAP dependence shapes are stable across assets with very different liquidity profiles
- Order flow imbalance is the dominant predictive feature (consistent with Kyle, 1985)
- Taker execution strategy is profitable and survives flash crash conditions
- Maker execution strategy is profitable in calm markets but suffers massive adverse selection during flash crash — confirms we should use taker execution only

---

## Part 2: Our Adaptation

### 2.1 Key Differences from Paper
| Paper | Our Implementation |
|---|---|
| 1-second features, 3-second prediction | Start at 1s; test signal survival at 5s, 15s, 1m, 5m aggregation levels |
| Standalone Python backtesting | Sidecar for data + inference → signal file → Freqtrade strategy reads signal |
| 5 assets | Start with BTC/USDT + ETH/USDT (match LiqCascade pairs), expand later |
| Historical data from Jan 2022 | Forward-collected data only (no free historical LOB source) |
| Academic backtest | Forward dry-run testing on DigitalOcean droplet |

### 2.2 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              LOB MICROSTRUCTURE ARCHITECTURE              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Sidecar Process (runs independently, 24/7)             │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Binance Futures WebSocket:                      │   │
│  │    @depth@100ms  (order book depth updates)      │   │
│  │    @aggTrade     (aggregated trades)              │   │
│  │                                                  │   │
│  │  Local Order Book maintained via DepthCache      │   │
│  │                                                  │   │
│  │  Every N seconds:                                │   │
│  │    1. Snapshot LOB state + recent trades          │   │
│  │    2. Compute features (imbalance, spread, VWAP) │   │
│  │    3. Run CatBoost inference                     │   │
│  │    4. Write prediction to signal file            │   │
│  │       (lob_signal_data.json)                     │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                               │
│                   signal file                           │
│                         │                               │
│  Freqtrade Strategy (5m candles)                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  populate_indicators():                          │   │
│  │    Read lob_signal_data.json                     │   │
│  │    Apply regime context (CRISIS gate, EMA200)    │   │
│  │                                                  │   │
│  │  populate_entry_trend():                         │   │
│  │    Enter when LOB signal exceeds threshold       │   │
│  │    Direction from signal sign                    │   │
│  │                                                  │   │
│  │  Exit: ROI table + stop loss + time stop         │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  SHARED with LiqCascade:                                │
│  - CRISIS gate (ATR p90 on 1h)                         │
│  - EMA200 macro trend filter                            │
│  - DigitalOcean droplet infrastructure                  │
│  - Docker compose setup                                 │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Critical Open Question: Timeframe Survival

The paper's edge is at 1–3 second horizon. We need to determine the shortest actionable timeframe for our stack. The plan includes explicit signal-survival testing at multiple aggregation levels before committing to a Freqtrade integration approach.

**If edge survives at 1m–5m:** Standard Freqtrade integration via signal file (like LiqCascade).
**If edge dies above 15s:** We need sub-minute execution from the sidecar itself (bypassing Freqtrade for order placement). This is a bigger architectural change — discuss with developer before proceeding.

---

## Part 3: Phase Plan

### Phase 0: LOB Data Collection Sidecar (Week 1)

**Goal:** Build and deploy a sidecar process that captures LOB snapshots and trade data from Binance Futures WebSocket, stores raw data for later model training, and runs 24/7 on the droplet.

**Tasks:**
1. Create `sidecar/lob_collector.py`:
   - Connect to Binance Futures WebSocket streams: `btcusdt@depth@100ms` and `btcusdt@aggTrade` (+ same for ethusdt)
   - Maintain local order book using `python-binance` DepthCacheManager or equivalent
   - Every 1 second: snapshot top-5 bid/ask levels + compute mid, spread, L1 volumes, order flow imbalance, buy/sell VWAP-to-mid
   - Write raw snapshots to compressed Parquet files (one file per hour, partitioned by symbol)
   - Log sidecar health (connection status, message rate, any gaps)

2. Create `sidecar/lob_features.py`:
   - Feature engineering functions matching the paper's feature families
   - Input: raw LOB snapshot + recent trades
   - Output: feature vector (dict or numpy array)
   - Must be callable both in real-time (sidecar) and offline (training pipeline)

3. Deploy to droplet:
   - Add `lob_collector` service to existing `docker-compose.yml` (new profile: `lobcollect`)
   - Verify coexistence with running LiqCascade containers
   - Monitor for 48h: confirm data is collecting, no gaps, no droplet resource issues

**Data storage estimate:**
- ~86,400 snapshots/day/symbol × 2 symbols = ~172,800 rows/day
- At ~50 features × 8 bytes each = ~400 bytes/row → ~69 MB/day uncompressed
- Parquet compression → ~15–20 MB/day. 2 weeks = ~200–300 MB. Negligible.

**Go/No-Go for Phase 1:**
- Sidecar running stably for 48+ hours
- Data files being written correctly (spot-check: mid price matches Binance, spread is reasonable, no NaN features)
- No impact on LiqCascade performance or droplet stability

---

### Phase 1: Feature Engineering Validation + Model Training (Week 2–3)

**Goal:** Validate the paper's feature engineering on our collected data and train a first CatBoost model.

**Tasks:**
1. After 7–14 days of data collection, pull data to local machine
2. Compute all features offline using `lob_features.py`
3. Verify feature distributions match paper's descriptions (order flow imbalance roughly symmetric, spread always positive, VWAP deviations centered near zero)
4. Train CatBoost with GMADL objective:
   - Walk-forward CV: train on first 70% of data, validate on next 15%, test on final 15%
   - Temporal purge gap: discard 5 minutes between train/val/test splits
5. Evaluate:
   - GMADL score on test set
   - Directional accuracy on test set
   - **Signal survival test:** Aggregate features and predictions to 5s, 15s, 1m, 5m windows. At which aggregation level does directional accuracy drop to ~50% (no edge)?

**Go/No-Go for Phase 2:**
- Model achieves >52% directional accuracy at the target timeframe on out-of-sample data
- Signal survival test identifies a viable execution timeframe for our stack
- Feature importance ranking qualitatively matches paper (order flow imbalance dominant)

**If signal dies at all timeframes > 1s:** This approach requires sub-second execution we cannot provide. STOP — archive as "edge too fast for our stack" and move to next candidate.

---

### Phase 2: Freqtrade Integration + Dry-Run (Week 3–4)

**Goal:** Integrate the trained model into a Freqtrade strategy via the sidecar signal pattern and begin dry-run testing.

**Tasks:**
1. Extend `lob_collector.py` to run CatBoost inference in real-time after feature computation
2. Write predictions to `lob_signal_data.json` (same pattern as LiqCascade's `liquidation_data.json`)
3. Create `user_data/strategies/LOBMicroStrategy_V01.py`:
   - Read signal file in `populate_indicators()`
   - Entry: signal exceeds threshold (calibrated from Phase 1 test results)
   - Direction: sign of prediction
   - Exit: ROI table + ATR-based stop + time stop (calibrate from Phase 1 hold-time analysis)
   - Regime context: reuse CRISIS gate + EMA200 from LiqCascade
4. Deploy to droplet alongside LiqCascade
5. Begin dry-run

**Go/No-Go for Phase 3:**
- 20+ trades accumulated
- Profit factor > 1.0
- Win rate > 45%
- No interference with LiqCascade operation

---

### Phase 3: Optimization + Multi-Pair (Week 5+)

**Goal:** Optimize parameters and expand to additional pairs.

**Tasks:**
1. Analyze dry-run trades: which features drove the best/worst trades?
2. Optimize signal threshold, hold time, stop distance
3. Add pairs (SOL, BNB, etc.) — paper shows features are portable, but validate per-pair
4. Retrain model periodically (weekly or biweekly) on rolling window

---

## Part 4: File Locations (Planned)

| File | Purpose | Status |
|---|---|---|
| `sidecar/lob_collector.py` | WebSocket LOB data capture + inference | To build (Phase 0) |
| `sidecar/lob_features.py` | Feature engineering functions | To build (Phase 0) |
| `sidecar/logs/lob_collector.log` | Sidecar health log | Auto-created |
| `sidecar/data/lob_raw/` | Raw Parquet snapshots | Auto-created |
| `user_data/models/lob_catboost_v01.cbm` | Trained CatBoost model | To create (Phase 1) |
| `user_data/strategies/LOBMicroStrategy_V01.py` | Freqtrade strategy | To build (Phase 2) |
| `user_data/info/LOB_Microstructure_Dev_Plan.md` | THIS FILE | Active |
| `user_data/info/AlgoTrading_Research_Log.md` | Project-wide context | Active |

---

## Part 5: Reference Material

### 5.1 Paper
- **Full paper:** https://arxiv.org/abs/2602.00776
- **HTML version:** https://arxiv.org/html/2602.00776v1
- **GitHub (referenced in paper):** Check paper for exact URL

### 5.2 Binance WebSocket Streams (Futures)
- **Partial Book Depth:** `wss://fstream.binance.com/stream?streams=btcusdt@depth@100ms`
- **Diff Book Depth:** `wss://fstream.binance.com/stream?streams=btcusdt@depth`
- **Aggregate Trades:** `wss://fstream.binance.com/stream?streams=btcusdt@aggTrade`
- **Local order book management:** https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly
- **Python libraries:** `python-binance` (DepthCacheManager), `unicorn-binance-local-depth-cache`

### 5.3 CatBoost
- `pip install catboost`
- CPU training and inference (no GPU required)
- Custom objective functions supported (for GMADL implementation)

---

## Part 6: What Not To Repeat (from RAME lessons)

These anti-patterns from previous projects apply here. If a future session is considering any of these, stop and re-read.

| Anti-pattern | Why it's relevant here |
|---|---|
| Training ML to predict labels derived from features | Our target is forward mid-price return, NOT a derived label. If accuracy is suspiciously high (>80%), check for data leakage. |
| Optimizing exits without questioning entry quality | If the strategy loses money, first check whether the signal has forward predictive power at all — don't start tuning stops. |
| Ignoring execution latency | The paper's edge is at 1–3 seconds. If we can't execute that fast, we may have no edge at all. Test this explicitly in Phase 1. |
| Adding complexity before validating the base case | Get the simplest version working first (CatBoost on core features → threshold entry → fixed exit). Add regime filters and multi-pair only after base case works. |

---

*Document maintained by: Claude + project co-developer*
*Last updated: 2026-03-20 — Initial creation*
