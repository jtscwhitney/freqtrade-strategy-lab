# Ensemble Donchian Trend-Following — Development Plan
## Candidate J from AlgoTrading Research Log
## Created: 2026-03-31 | Status: PRE-DEVELOPMENT

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Also read `user_data/info/AlgoTrading_Research_Log.md` for project-wide context, roles, and objectives.

### What This Project Is
We are implementing an ensemble Donchian channel trend-following strategy on a rotational portfolio of ~20 crypto futures. The core idea: for each asset, compute Donchian channel breakout signals at 9 different lookback periods and average them into a single ensemble score. Go long when the ensemble score exceeds a threshold (i.e., price is above the upper channel across multiple lookback windows simultaneously). Exit via trailing stop at the lower channel. Volatility-based position sizing. Long-only by design. This is Candidate J in our Research Log — the second candidate to achieve a clean 7/7 PASS on our evaluation filter.

### Current Phase
- **Phase:** 0 — Data Download + Hourly Timeframe Validation
- **Last completed:** [Not started]
- **Next immediate step:** Download 1h OHLCV data for 20+ Binance Futures pairs, compute Donchian channels at hourly-equivalent lookbacks, validate that the ensemble signal has predictive power at hourly resolution (the source paper uses daily data)
- **Blocking issues:** None

### Key Context from Research Log
- We are Co-Investigators, Co-Strategists, and Co-Developers. Claude pushes back on bad ideas. See Research Log Section 1.
- Our objective is high-ROI, high-frequency crypto trading. See Research Log Section 2.
- **Five previous candidates failed/parked:** RAME (edge too small), LOB Microstructure (fee economics), CointPairs (frequency + single-leg), Candidate E / Path Signatures (stops swamped edge), Candidate G / Cross-Sectional Momentum (regime-unstable, parked). See Research Log Section 4.1 and Lessons #1–12.
- **LiqCascade is ACTIVE** in Phase 3 dry-run (review scheduled ~2026-04-05). This strategy would run concurrently, not replace it.
- **G's infrastructure is reusable:** `DataProvider` cross-pair loading, `custom_info` storage, vol-scaled position sizing, config structure. Adapt, don't rebuild.
- **Critical lessons that apply here:** Fee economics sweep before infrastructure (#7). Institutional fee tiers don't transfer (#8). Bull-market validation bias (#10). Time-stop rate as diagnostic (#11). Regime instability killed G — ensemble smoothing is the proposed fix.
- **Primary risk:** The source paper (Zarattini et al.) uses *daily* data. We need *hourly* for our frequency objective. Phase 0 must explicitly validate the daily-to-hourly translation before committing to implementation.

---

## Part 1: Strategy Summary

### 1.1 What Ensemble Donchian Trend-Following Is
At each candle:
1. For each asset in the 20-pair universe, compute Donchian channel upper/lower bands at **9 lookback periods** (hourly equivalents of: 5d, 10d, 20d, 30d, 60d, 90d, 150d, 250d, 360d → 120h, 240h, 480h, 720h, 1440h, 2160h, 3600h, 6000h, 8640h)
2. For each lookback, compute a binary breakout signal: `1` if close > upper channel, `0` otherwise
3. Average the 9 binary signals into an **ensemble score** (0.0 to 1.0)
4. **Enter long** if ensemble score > threshold (e.g., > 0.5 means majority of lookbacks confirm uptrend)
5. **Exit** via trailing stop calibrated to the shortest active Donchian lower band (or a fixed ATR-based trailing stop)
6. **Position size** scaled inversely with recent volatility (same approach as G's V01)

The alpha comes from trend continuation: assets breaking out across multiple timeframe-equivalent windows are in confirmed trends, not noise.

### 1.2 Key Academic Findings
- **Zarattini et al. (SSRN 2025):** Ensemble Combo achieves Sharpe 1.58, CAGR 30%, Sortino 2.03, alpha 14% vs BTC on survivorship-bias-free data 2015–2025. Net of fees. Walk-forward tested. Rotational top-20 portfolio.
- **Beluská & Vojtko (SSRN 2024):** Confirm BTC trends at local maxima (trend-following works) and mean-reverts at local minima. Updated through Aug 2024.
- **Mesíček & Vojtko (SSRN 2025):** Multi-timeframe trend confirmation on BTC 2018–2025 improves stability and Sharpe. Supports the multi-lookback ensemble concept.
- **Turtle Traders legacy:** Donchian breakout systems have 40+ years of evidence across managed futures. The methodology is battle-tested in traditional markets.

### 1.3 Why This Candidate Is Different from Our Failures
| Previous Failure | Why J Avoids It |
|---|---|
| RAME: edge too small per trade | Trend-following on hourly crypto captures 50–300+ bps moves — well above fee floor |
| LOB: fee economics killed it | Per-trade moves are orders of magnitude above 10 bps fees; holding periods are hours to days, not seconds |
| CointPairs: 0.05 trades/day | 20 pairs × ensemble signal = many independent entry opportunities per day |
| CointPairs: single-leg exposure | Each trade is independent long-only — no paired legs, no short-side risk |
| G: regime-unstable (−40% in 2024) | Ensemble over 9 lookback periods smooths regime transitions; short lookbacks adapt fast, long lookbacks prevent whipsawing |
| G: return ranking was fragile | Breakout detection (binary: is price above channel?) is mechanistically different and more robust than return ranking (continuous: relative performance) |
| Candidate E: stops swamped edge on unhedged alts | Long-only with trailing stop at Donchian lower band — exit is structurally tied to the signal (lower band break = trend over), not an arbitrary fixed percentage |
| RAME: tautological ML | No ML — pure price channels. Signal is transparent and auditable |

### 1.4 Key Difference from G's Architecture
G ranked assets by **returns** (who gained the most over the formation period?) and **rebalanced on a fixed schedule**. J ranks by **trend state** (is this asset breaking out across multiple timeframe windows?) and **exits when the trend breaks** (trailing stop). This means:
- G's signal was **relative** (cross-sectional rank) — J's signal is **absolute** (per-asset breakout state)
- G's exit was **time-based** (holding period) — J's exit is **signal-based** (trailing stop at Donchian lower band)
- G required all positions to turn over at rebalance — J holds positions as long as the trend persists

---

## Part 2: Architecture

```
┌─────────────────────────────────────────────────────────┐
│    ENSEMBLE DONCHIAN TREND-FOLLOWING ARCHITECTURE (V01)  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Freqtrade Strategy (1h candles, 20 pairs)              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  populate_indicators():                          │   │
│  │    For each pair (via DataProvider):              │   │
│  │      Compute Donchian upper/lower at 9 lookbacks │   │
│  │      Compute binary breakout signal per lookback │   │
│  │      Average → ensemble_score (0.0 to 1.0)      │   │
│  │      Compute trailing stop level (Donchian lower)│   │
│  │    Compute cross-sectional vol (trailing 24h)    │   │
│  │                                                  │   │
│  │  populate_entry_trend():                         │   │
│  │    IF ensemble_score > entry_threshold:           │   │
│  │      enter_long = 1                              │   │
│  │                                                  │   │
│  │  custom_stoploss():                              │   │
│  │    Trailing stop at shortest active Donchian     │   │
│  │    lower band (or ATR-based trailing)            │   │
│  │                                                  │   │
│  │  custom_stake_amount():                          │   │
│  │    stake = base_stake × (target_vol / asset_vol) │   │
│  │    Floor at 50% of base_stake                    │   │
│  │                                                  │   │
│  │  Long-only. No short entries.                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  SHARED with LiqCascade (if running concurrently):      │
│  - DigitalOcean droplet infrastructure                  │
│  - Docker compose setup (new profile: donchian)         │
│  - Separate Freqtrade instance + config + DB            │
│                                                         │
│  REUSES from G: DataProvider cross-pair pattern,        │
│  custom_info storage, vol-scaling logic, config shape.  │
│                                                         │
│  NO sidecar needed. NO special data source.             │
│  Pure OHLCV strategy running natively in Freqtrade.     │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Key Design Decisions

**Universe:** Same as G — top 20 Binance Futures perpetuals by trailing 30-day average volume, excluding stablecoins, wrapped tokens, leverage tokens. StaticPairList. Re-evaluate quarterly. Reuse G's universe if still current.

**Timeframe:** 1h candles. This is the primary risk to validate — paper uses daily.

**Donchian lookback periods (hourly equivalents):**
Paper uses daily: 5, 10, 20, 30, 60, 90, 150, 250, 360 days.
Hourly equivalents (×24): 120, 240, 480, 720, 1440, 2160, 3600, 6000, 8640 hours.
**Phase 0 must test whether all 9 are needed** at hourly resolution or if a subset (e.g., 5 lookbacks from 120h to 2160h) is sufficient. The longest lookback (8640h = 360 days) requires a year of 1h data to compute — verify data availability.

**Ensemble signal construction:**
- Per lookback `i`: `signal_i = 1 if close > donchian_upper_i else 0`
- Ensemble score: `mean(signal_1, ..., signal_9)` → value 0.0 to 1.0
- Entry threshold: `ensemble_score > 0.5` (majority of lookbacks confirm) — hyperparameter

**Exit mechanism — trailing stop:**
- The paper uses the Donchian lower band as a trailing stop. When price breaks below the lower channel, the trend is over.
- **Which lookback's lower band?** Use the shortest lookback period that triggered the entry. This gives the tightest exit — exits quickly when short-term trend breaks.
- Alternative: ATR-based trailing stop (2–3× ATR from peak). Test both.

**Position sizing and max exposure:**
- `max_open_trades`: 5–8 (not all 20 pairs will be in breakout simultaneously)
- `stake_amount`: inverse-volatility weighted (same as G's V01)
- Leverage: 2x initially
- `tradable_balance_ratio`: 0.95

---

## Part 3: Phase Plan

### Phase 0: Data Download + Hourly Timeframe Validation (Days 1–2)

**Goal:** Download historical data, validate that the Donchian ensemble signal has predictive power at hourly resolution. **This is the critical gate** — the paper uses daily data. If the signal doesn't work at hourly, test 4h as a compromise before abandoning.

**Tasks (Day 1 — Data + Donchian Computation):**
1. Download 1h OHLCV for 20+ Binance Futures pairs, 2022–2026
2. Reuse G's universe pair list if still current; otherwise re-derive from volume ranking
3. Compute Donchian upper/lower channels at all 9 hourly-equivalent lookback periods
4. Compute ensemble score time series for each pair
5. Visualize: ensemble score heatmap (pairs × time), histogram of ensemble scores, duration of "in-trend" states per pair

**Tasks (Day 2 — Fee-Inclusive Signal Validation):**
6. Build standalone sweep script (`user_data/scripts/donchian_phase0_sweep.py`):
   - For each pair, simulate the long-only ensemble strategy:
     - Entry: ensemble_score > threshold (sweep: 0.3, 0.5, 0.7, 0.9)
     - Exit: Donchian lower band trailing stop (sweep: use shortest, median, longest active lookback)
     - Compute per-trade returns after 10 bps round-trip fees
   - Track: total P&L, profit factor, trade count, win rate, avg hold duration
   - Split results by regime: 2022 (bear), 2023 (range), 2024–2025 (bull), 2026 (recent)
   - **Lesson #10 check:** Are profits concentrated in bull periods only?
7. **Hourly vs daily comparison:** Run the same sweep at daily resolution to compare with paper's reported results. If hourly degrades significantly, test 4h as intermediate.
8. Output: parameter heatmap, regime splits, hourly-vs-daily comparison table.

**Go/No-Go for Phase 1:**
- Ensemble signal at 1h (or 4h fallback) shows at least one (threshold, trailing-stop-variant) combination with profit factor > 1.2 after 10 bps fees
- Regime split shows profitability in at least 2 of 3 regime periods (bear, range, bull)
- Trade frequency > 0.5 trades/day average (across all 20 pairs) — lower bar than G because trend-following trades are inherently longer-held
- Average hold duration is compatible with our frequency objective (< 7 days preferred; if average is > 14 days, frequency may be too low)
- **If hourly fails but daily works:** Consider 4h as a compromise. If 4h also fails, STOP. The signal may be fundamentally a slow-moving one that doesn't compress to our timeframe.

---

### Phase 1: Freqtrade MVP — Ensemble Long-Only (Days 3–4)

**Prerequisite:** Phase 0 GO — at least one profitable operating point at 1h or 4h.

**Tasks:**
1. Create `config/config_donchian.json`: StaticPairList with 20 pairs, futures mode, 1h (or 4h), fees 0.05%/side, leverage 2x
2. Create `user_data/strategies/EnsembleDonchianStrategy_V01.py`:
   - `informative_pairs()`: all 20 universe pairs at the chosen timeframe
   - `populate_indicators()`: compute Donchian channels at all lookback periods, ensemble score, trailing stop level
   - `populate_entry_trend()`: `enter_long = 1` if `ensemble_score > threshold`
   - `custom_stoploss()`: trailing stop at the Donchian lower band (or ATR-based variant, per Phase 0 results)
   - `custom_stake_amount()`: inverse-vol scaled
   - **No short entries.**
3. Backtest on 2022–2026 using Phase 0's best parameters
4. Regime-split analysis (2022 bear, 2023 range, 2024–2025 bull, 2026 recent)
5. **Diagnostic checks:**
   - Win rate and profit factor per exit type (trailing stop hit vs other)
   - Average hold duration — does it match Phase 0 sweep expectation?
   - Per-pair P&L distribution — concentrated or diversified?
   - Max concurrent open trades — does `max_open_trades` need adjustment?

**Go/No-Go for Phase 2:**
- Profit factor > 1.2 on full backtest
- Profitable in at least 2 of 3 regime periods
- Trade frequency > 0.5 trades/day average
- Drawdown < 30% (at 2x leverage)
- No single pair contributes > 40% of total P&L
- Backtest results are consistent with Phase 0 sweep (no implementation bugs)

---

### Phase 2: Enhancement + Hyperopt + OOS Validation (Days 5–6)

**Prerequisite:** Phase 1 GO.

**Tasks:**
1. **K-filter enhancement (optional):** If Phase 1 is profitable but has excessive entries during counter-trend periods, add Candidate K's multi-timeframe filter: require a higher-timeframe MACD (daily or 4h) to confirm the trend direction before entry. Test with and without to measure impact.
2. Hyperopt on 2022–2024 (in-sample):
   - Parameters: ensemble threshold, trailing stop variant, N lookback periods (subset selection), vol scaling factor
   ```
   freqtrade hyperopt --strategy EnsembleDonchianStrategy_V01 --config config/config_donchian.json --hyperopt-loss SharpeHyperOptLoss --timerange 20220101-20250101 --epochs 200
   ```
3. Out-of-sample validation on 2025–2026
4. Walk-forward: train on rolling 6-month windows, test on subsequent 2-month windows

**Go/No-Go for Phase 3:**
- OOS profit factor > 1.2
- Walk-forward profitable in at least 5 of 8 windows
- Parameters not at extreme edges
- Trade frequency maintained in OOS

---

### Phase 3: Dry-Run Deployment (Week 2+)

**Goal:** Deploy alongside LiqCascade, accumulate forward-testing data.

**Tasks:**
1. Add `donchian` profile to Docker compose on droplet
2. Deploy as separate Freqtrade instance
3. Monitor for 2+ weeks
4. Compare dry-run to backtest expectations

**Go/No-Go for Phase 4 (live capital):**
- 2+ weeks, minimum 20 completed trades
- Total return consistent with backtest expectation
- Trade frequency within 30% of backtest
- No single week loss > 5%
- Stable coexistence with LiqCascade on shared droplet

---

## Part 4: What Not To Repeat

| Anti-pattern | Why it's relevant here | Addressed in |
|---|---|---|
| Building infrastructure before fee sweep | Phase 0 sweep before any Freqtrade code. Lesson #7. | Phase 0 Day 2 |
| Trusting bull-market backtests | Regime splits mandatory at every gate. Lesson #10. | All go/no-go gates |
| Ignoring trade frequency | Must validate > 0.5 trades/day. CointPairs died at 0.05. | Phase 0 gate |
| Using ML before validating base case | V01 is pure Donchian channels — no ML. | V01 design |
| Regime instability (G's failure) | Ensemble over 9 lookbacks smooths regime transitions. | Core signal design |
| Short-side losses (E, G) | Long-only by design. No short entries. | V01 design |
| Assuming paper results transfer to our timeframe | Paper uses daily; we need hourly. Phase 0 explicitly tests this. Lesson #8 generalized. | Phase 0 hourly validation |
| Fixed stops on trending strategy | Trailing stop at Donchian lower band — exits are signal-driven, not fixed %. | Exit mechanism |

---

## Part 5: File Locations (Planned)

| File | Purpose | Status |
|---|---|---|
| `user_data/strategies/EnsembleDonchianStrategy_V01.py` | Long-only ensemble Donchian (MVP) | To build (Phase 1) |
| `config/config_donchian.json` | Strategy config (20 pairs, futures, 1h) | To build (Phase 0) |
| `user_data/scripts/donchian_phase0_sweep.py` | Phase 0 signal validation + fee sweep | To build (Phase 0) |
| `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` | THIS FILE | Active |
| `user_data/info/AlgoTrading_Research_Log.md` | Project-wide context | Active |

### Appendix A: Universe Pair List
*Reuse G's universe if still current. Otherwise populate in Phase 0.*

### Appendix B: Donchian Lookback Period Mapping (Paper → Hourly)

| Paper (daily) | Hourly Equivalent | Notes |
|---|---|---|
| 5d | 120h | Shortest — fastest trend detection, most noise |
| 10d | 240h | |
| 20d | 480h | ~1 month |
| 30d | 720h | |
| 60d | 1440h | ~2 months |
| 90d | 2160h | ~3 months |
| 150d | 3600h | ~6 months |
| 250d | 6000h | ~10 months — requires ~10 months of 1h data |
| 360d | 8640h | ~12 months — requires ~12 months of 1h data |

*Phase 0 should test whether all 9 are needed or if a 5-lookback subset (e.g., 120h through 2160h) is sufficient at hourly resolution. Longer lookbacks may not add value when the base timeframe is already 1h.*

---

## Part 6: Reference Material

### 6.1 Key Papers
- **Zarattini, Pagani & Barbon (SSRN 2025):** "Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins" — The primary source. Donchian ensemble, rotational portfolio, survivorship-bias-free, Sharpe > 1.5.
- **Beluská & Vojtko (SSRN 2024):** "Revisiting Trend-following and Mean-Reversion Strategies in Bitcoin" — Confirms trend-following still works through Aug 2024.
- **Mesíček & Vojtko (SSRN 2025):** "How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin" — Multi-timeframe confirmation improves stability. Supports K-filter enhancement.

### 6.2 Freqtrade Implementation References
- **Donchian channels:** `ta.MAX(dataframe['high'], timeperiod=N)`, `ta.MIN(dataframe['low'], timeperiod=N)`
- **Cross-pair data:** `DataProvider.get_pair_dataframe()` — same pattern as G
- **Custom trailing stop:** `custom_stoploss()` method — return negative value relative to current rate
- **Informative pairs:** `informative_pairs()` — return all 20 pairs at base timeframe

### 6.3 Relationship to G's Codebase
J reuses the following from G:
- `DataProvider` + `custom_info` cross-pair loading pattern
- Vol-scaling logic in `custom_stake_amount()`
- Config structure and pair list
- Phase 0 sweep script pattern (adapt `xsmom_phase0_sweep.py`)

J differs from G in:
- Signal source: Donchian breakout ensemble vs return ranking
- Exit mechanism: trailing stop vs periodic rebalance
- Signal type: absolute (per-asset breakout state) vs relative (cross-sectional rank)
- Direction: long-only vs long/short variants

### 6.4 Enhancement Path (Future)
- **Candidate K filter:** Add daily MACD trend confirmation before entry. Test in Phase 2 if V01 shows excessive counter-trend entries.
- **Adaptive lookback selection:** Instead of fixed 9 lookbacks, use recent regime volatility to weight shorter or longer lookbacks more heavily. Research phase — not in MVP.
- **Sector rotation overlay:** Instead of equal treatment of all 20 pairs, weight toward sectors (DeFi, L1, L2) with strongest recent trend coherence. Research phase — not in MVP.

---

*Document maintained by: Claude + project co-developer*
*Last updated: 2026-03-31 — Initial creation*
