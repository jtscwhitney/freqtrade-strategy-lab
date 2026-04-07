# AlgoTrading Research Log
## Maintained by: [Developer] + Claude (any model)
## Last Updated: 2026-04-07 (Sweep #5 complete — Candidate M promoted to #1)
## Stack: Cursor / Freqtrade / FreqAI / Claude Opus 4.6

---

## READ THIS FIRST — What This File Is and How to Use It

**This file is the shared memory and operating agreement between the developer and Claude across all sessions.** It exists because Claude has no persistent memory between conversations. Every new session — whether in claude.ai or Cursor — starts from zero. This file bridges that gap.

**What it contains:**
- **Roles & Objectives (Sections 1–2):** Who we are to each other and what we're trying to achieve. Claude is an equal partner, not an assistant. Read these sections to understand the working dynamic.
- **Stack & Constraints (Section 3):** The fixed technical realities that every approach must fit within.
- **Approach Registry (Section 4):** Everything we've tried, what's currently active, and what's been identified as a candidate. This is the project memory — check it before suggesting anything to avoid re-treading ground.
- **Sourcing Configuration (Section 5):** Where we look for new strategy ideas and what search terms to use.
- **Evaluation Filter (Section 6):** The 7-point checklist every candidate must pass before we commit development time.
- **Techniques Library (Section 7):** Reusable techniques, tools, and methods that are not standalone strategies but can strengthen candidates during evaluation, development, or operation. Claude should mine this section when evaluating new candidates and when diagnosing deficiencies in active strategies.
- **Sourcing Sweep Log (Section 8):** Record of each research sweep — what was searched, what was found, what was promoted.
- **Lessons & Principles (Section 9):** Hard-won insights from past projects that apply across all future work.
- **Version History (Section 10):** Change log for this file.

**How to use it:**
- **Developer:** Upload this file at the start of every research or strategy session with Claude. When changes are made during a session, download the updated version and replace your local copy. Keep it in version control (`user_data/info/AlgoTrading_Research_Log.md`).
- **Claude:** Read this entire file before doing anything else. Understand the roles, objectives, what's been tried, what's active, and what's next. Do not suggest approaches already in the registry. Do not confirm ideas uncritically — Section 1 requires you to push back, propose alternatives, and check the developer's reasoning. When changes are made during a session, produce an updated file for the developer to download. **Periodically (every 2–3 sessions or after major updates), do a global consistency check:** verify all section cross-references are correct, check that candidate statuses match the Priority Ranking, confirm Sweep Log recommendations align with current candidate statuses (e.g., if a recommended candidate was later archived, note that), and flag any stale or contradictory information.

**This file is also used in Cursor sessions** for strategy implementation. When working in Cursor, Claude should read this file for project context and then refer to the relevant Deep Dive document for implementation-specific details. The Research Log provides the "what and why"; the Deep Dive documents provide the "how."

**Related files:**
- `user_data/info/Regime_Adaptive_Ensemble_Deep_Dive.md` — RAME project (ARCHIVED)
- `user_data/info/RAME_Project_Summary.md` — RAME summary (ARCHIVED)
- `user_data/info/LiquidationCascade_Deep_Dive.md` — LiqCascade project (ACTIVE)
- `user_data/info/CointPairsTrading_Deep_Dive.md` — Candidate F / CointPairs project (ARCHIVED)
- `user_data/info/PathSignatureLeadLag_Deep_Dive.md` — Candidate E / Path Signatures lead-lag (ARCHIVED)
- `user_data/info/CrossSectionalMomentum_Dev_Plan.md` — Candidate G development plan
- `user_data/info/CrossSectionalMomentum_Deep_Dive.md` — Candidate G deep dive (**PARKED** — implementation retained; see entry)
- `user_data/info/CrossSectionalMomentum_Phase0_Summary.md` — Candidate G Phase 0 layman summary
- `user_data/info/CrossSectionalMomentum_Phase1_Summary.md` — Candidate G Phase 1 summary (**PARKED** candidate; results retained)
- `user_data/info/LOB_Microstructure_Dev_Plan.md` — Candidate A development plan (superseded)
- `user_data/info/LOB_Microstructure_Deep_Dive.md` — Candidate A deep dive (ARCHIVED)
- `deploy/digitalocean.md` — DigitalOcean deployment reference (added with Candidate E)
- `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` — Candidate J development plan (**PARKED** — Phase 0 NO-GO, 2026-04-06)
- `user_data/info/EnsembleDonchianTrend_Deep_Dive.md` — Candidate J deep dive (**PARKED** — implementation retained for reference)
- `user_data/info/EnhancedCointPairs_Dev_Plan.md` — Candidate L development plan (NEW)
- `user_data/info/EnhancedCointPairs_Deep_Dive.md` — Candidate L deep dive (ACTIVE; mirrored in `freqtrade-coint-pairs-trading`)
- `user_data/info/AdaptiveTrend_Dev_Plan.md` — Candidate M development plan (ACTIVE — Phase 0 not yet started)
- OracleSurfer strategy — in `Freqtrade` repo (separate): `user_data/strategies/OracleSurfer_v14_PROD.py` (ACTIVE dry-run on DigitalOcean droplet)

**Research & Development Workflow:**

This project follows a two-track workflow, split by platform:

*Track 1 — Research (claude.ai web sessions):*
1. **Sourcing Sweeps:** Claude searches primary and applied sources (Section 5) using rotating search terms. Results are triaged, promising approaches are promoted to Candidates in Section 4.3. Each sweep is logged in Section 8 with sources checked, terms used, and papers reviewed.
2. **Candidate Evaluation:** Each candidate is scored against the 7-point Evaluation Filter (Section 6). During evaluation, Claude checks the Techniques Library (Section 7) for enhancements and Lessons (Section 9) for relevant failure modes. Results are recorded in the candidate entry.
3. **Priority Ranking:** After evaluation, Section 4.4 is updated to reflect the recommended build order with rationale.
4. **Dev Plan Creation:** For the top-ranked candidate, Claude creates a development plan document (similar to `CrossSectionalMomentum_Dev_Plan.md`) that a Cursor session can execute from without needing this conversation's history.

*Track 2 — Implementation (Cursor sessions):*
1. Claude reads this Research Log for context, then reads the relevant Dev Plan for implementation details.
2. Implementation follows the Dev Plan's phase structure with explicit go/no-go gates.
3. **Fee economics sweep (Technique 7.3) is mandatory** before building execution infrastructure — run it in Phase 0 or Phase 1, not after.
4. When a candidate fails, write a full post-mortem in the Archived section (4.1), extract reusable infrastructure, add new lessons to Section 9, and update the Priority Ranking.
5. When a candidate succeeds, promote it to Active (Section 4.2) and create/update a Deep Dive document.

*Syncing between tracks:*
- At the end of any session (web or Cursor), Claude produces an updated Research Log for the developer to download.
- At the start of any session, the developer uploads the latest version of this file.
- The developer may also have a co-developer working in parallel on specific candidates. Their results will be merged into this master log when available. Check candidate entries for parallel development notes before starting duplicate work.

---

## 1. Roles

Claude and the developer are **equal partners** — Co-Investigators, Co-Strategists, and Co-Developers. Claude does not default to confirming the developer's ideas or pursuing only developer-dictated paths. Both parties brainstorm, challenge assumptions, propose alternatives, and check each other's reasoning. The goal is the best possible system, not agreement.

**In practice this means Claude should:**
- Push back when an approach has flaws, even if the developer is enthusiastic
- Proactively suggest alternatives the developer hasn't considered
- Flag when a line of investigation is unlikely to meet objectives, rather than silently building what's asked
- Bring its own research and ideas to sourcing sweeps, not just process what the developer provides

---

## 2. Objectives

**Goal:** Investigate, develop, and deploy crypto algorithmic trading systems — whether novel, adapted from established approaches, or assembled from combinations of known techniques — that significantly outperform traditional investment strategies. The developer already has capital in conventional approaches — the systems built here must justify their complexity with materially higher returns.

**Risk tolerance:** High. Willing to accept elevated risk for elevated returns.

**Trading frequency:** Systems must be active traders — high trade counts per unit time (comparable to scalping frequency, not swing trading). This can be achieved through fast execution timeframes, multiple concurrent trades, multiple concurrent strategies, or any combination. The motivation is practical: low-frequency systems take too long to evaluate in forward testing, and the development horizon is short (weeks, not months).

**Forward-testing realism:** Some approaches will only be testable via dry-run or live forward testing (e.g., strategies requiring real-time data not available historically). This is acceptable as long as evaluation can happen in weeks, not months. The Liquidation Cascade strategy is a precedent for this.

---

## 3. Stack & Constraints

These are the fixed realities that every approach must fit within.

| Constraint | Detail |
|---|---|
| **Framework** | Freqtrade (Python, Docker) with FreqAI for ML models |
| **IDE / AI** | Cursor with Claude Opus 4.6 as co-developer |
| **Compute** | Cloud VPS (currently DigitalOcean) for live/dry-run; local machine for backtesting. Non-GPU preferred but not required — GPU instances are acceptable if a candidate's ROI justifies the cost. |
| **Markets** | Crypto futures primarily (Binance Perpetuals as default). Freqtrade supports many exchanges. See Section 3.1 on cross-asset proxies. |
| **Data budget** | Free or low-cost preferred. CCXT, Binance API, CoinGecko, public APIs. Will consider paid data sources if the potential ROI is compelling or if ongoing development of a proven candidate shows that paid data would materially improve performance. |
| **Leverage** | 2–4x typical |
| **Execution** | Freqtrade's standard execution (not HFT, not co-located) |
| **Developer** | Solo. All code written with AI assistance in Cursor |
| **Libraries** | Python ecosystem: scikit-learn, XGBoost, LightGBM, PyTorch (for inference, not heavy training), TA-Lib, pandas, numpy. Open to others if lightweight |

### 3.1 Cross-Asset Proxy Pairs

All execution must happen via Freqtrade — that constraint is fixed. Our primary exchange is Binance, but Freqtrade supports many exchanges (Bybit, OKX, Kraken, Gate.io, etc.). If a candidate requires a specific exchange feature or a pair only available elsewhere, that's not an automatic rejection — evaluate on merits. However, strategies originating from non-crypto asset classes (gold, equities, forex, commodities) are eligible **if** a liquid proxy pair exists on a Freqtrade-supported exchange. We don't actively sweep non-crypto sources, but if a cross-asset approach surfaces during a normal sweep, we don't reject it on the basis of the underlying asset class alone.

**Before evaluating any cross-asset candidate**, verify the proxy pair exists on a Freqtrade-supported exchange with sufficient liquidity (24h volume > $10M) and that the proxy actually tracks the underlying asset. Tokenized assets can decouple from their reference during stress events.

**Known liquid proxy pairs (Binance examples — check other exchanges too):**

| Asset Class | Underlying | Binance Proxy Pair | Notes |
|---|---|---|---|
| Gold | XAU/USD | PAXG/USDT (spot) | No perpetual futures — spot only. Check if perp has been listed. |
| Forex-like | USD strength | Stablecoin pairs (e.g., EUR-pegged tokens) | Very limited liquidity on most. |
| Equity-correlated | Tech/risk-on | BTC and ETH themselves correlate with NASDAQ in macro regimes | Not a direct proxy but relevant for cross-asset signal strategies. |
| Oil/Energy | Crude oil | No direct proxy | — |
| DeFi index | DeFi sector | Various DeFi tokens (UNI, AAVE, etc.) | Liquid on Binance Futures but loosely correlated to each other. |

*This table is a starting reference, not exhaustive. Exchange listings change. Always verify before committing to a candidate.*

---

## 4. Approach Registry

Status key: `ARCHIVED` = tried and abandoned · `ACTIVE` = currently deployed or under development · `PAUSED` = shelved but not abandoned · `CANDIDATE` = identified but not yet attempted

### 4.1 ARCHIVED

#### RAME — Regime-Adaptive Multi-Strategy Ensemble
- **Status:** ARCHIVED (2026-03-17) — needs total rethink if revisited
- **Duration:** ~2 weeks, 17 backtest runs
- **Core idea:** Classify market into 5 regimes (ACTIVE_BULL, ACTIVE_BEAR, QUIET_BULL, QUIET_BEAR, CRISIS) using ATR/ADX/EMA indicators, then route trades to regime-specific sub-strategies
- **What worked:** The 2×2+CRISIS regime framework is empirically valid (HMM best_n=5). ACTIVE regime labels have statistically significant directional edge at 4h horizon (ETH ACTIVE_BULL p=0.006, BTC QUIET_BEAR p=0.025)
- **Why it failed:**
  1. Edge too small: +0.087% mean per 4h candle — barely above breakeven after fees at any leverage
  2. Consistent late entry: signal fires on candle close, entry on next open — initial move already priced in
  3. Regime indicators oscillate at short timeframes: ADX/ATR cross thresholds 2–3x per 4h period
  4. FreqAI classifier was tautological: 91.7–100% accuracy because it memorized the labeling formula, not future returns
  5. Every exit strategy tested was destructive: regime-change exits had 2–24% win rate across all 9 configs
  6. 2022 bear market exposed fatal flaw: short-term "bullish" signals during macro downtrend caused 70–87% of all losses
- **Key lessons (do NOT re-introduce):**
  - ADX thresholds (oscillation source)
  - EMA21 trend filter (too short, caused bear market losses)
  - Regime-change exit signals (consistently destructive)
  - Quiet regime entries at leverage (edge too small)
  - FreqAI classifier on regime labels (tautological)
- **Salvageable elements:**
  - The regime framework itself (as a context filter, not a signal generator)
  - EMA200 macro trend filter (untested in RAME, adopted by LiqCascade)
  - CRISIS gate using ATR p90 (adopted by LiqCascade)
- **Deep dive:** `Regime_Adaptive_Ensemble_Deep_Dive.md`
- **Summary:** `RAME_Project_Summary.md`

---

#### LOB Microstructure — CatBoost on Order Flow Features
- **Status:** ARCHIVED (2026-03-20) — signal real, fee structure incompatible at retail rates
- **Duration:** 1 day (Phase 1 validation + threshold sweep; Phase 2 never built)
- **Source:** arXiv 2602.00776 (Bieganowski & Ślepaczuk, Jan 2026)
- **Core idea:** Engineer order flow imbalance (OFI) and VWAP deviation features from Binance aggTrades at 1-second frequency. Train CatBoost with a direction-penalized loss (GMADL) to predict 3-second forward mid-price returns. Paper showed profitable taker-execution backtest across 5 assets.
- **What worked:**
  - Signal is real and paper-replicable. Consistent across 3 independent training runs.
  - 3s directional accuracy: 54.2% unconditional, 59.3% top-20% filtered
  - Spearman IC: 0.135 at 3s, decaying to 0.024 at 60s (real but short-lived)
  - Feature importance matched paper: VWAP deviation features #1/#2, OFI #3
  - Signal viable to 15s horizon (dir_acc > 51%); dies between 15s and 60s
  - 109 days of BTC+ETH historical data downloaded and processed (data.binance.vision)
- **Why it failed — fee structure, not signal quality:**
  - BTC 3s move std = 1.68 bps. Binance retail taker fee = 10 bps round-trip. Gap is structural: 6× below fee floor.
  - Threshold sweep across top-50% to top-0.5% signal strength at all horizons (3s, 5s, 15s, 60s, 300s): **zero profitable operating points at any threshold**.
  - Best case (top-0.5% signals, 3s horizon): mean |move| = 5.74 bps, net P&L = −8.97 bps/trade.
  - Fee break-even requires ~63 bps mean move at 3s under normal conditions — structurally impossible.
  - Paper's profitability was almost certainly produced under institutional fee tiers (VIP: 0.02–0.04%/side) or maker execution (which the paper itself flagged as catastrophically failing during flash crashes).
- **Secondary constraint:** bookTicker historical data is not available on data.binance.vision for USD-M Futures. L1 book features (spread, bid/ask qty, vol_imbalance) were NaN throughout training — model used 9 aggTrade-derived features only, not the full feature set from the paper. Whether L1 features would have changed the fee economics is unknown, but the structural 6× gap makes it unlikely.
- **Key lessons:** See Section 9, items 7 and 8.
- **Potential future salvage:** The LOB OFI signal could serve as a timing confirmation filter for LiqCascade entries (no standalone execution required; no fee problem). Not prioritized — pursue only if LiqCascade Phase 3 data shows a high false-positive entry rate.
- **Deep dive:** `LOB_Microstructure_Deep_Dive.md` (ARCHIVED)

---

#### Cointegration Pairs Trading (CointPairs) — Candidate F
- **Status:** ARCHIVED (2026-03-22) — Phase 1 FAIL
- **Duration:** 1 day (Phase 0 + Phase 1 backtest)
- **Core idea:** Trade mean reversion of log-price spread between major crypto pairs. Enter when z-score exceeds ±threshold; exit on reversion. Single-leg V02 on BNB/ETH@4h.
- **What worked:** Hurst H≈0.25 for all pairs — genuine mean-reverting ratio structure. Phase 0 fee sweep at 4h with 1440h stop showed ts=0% and solid economics (168bps@ez=3.0). BNB/ETH has stable rolling β (std=0.229). Phase 0 validation framework and fee sweep methodology are reusable.
- **Why Phase 1 failed — two independent failure modes:**
  1. **Single-leg directional exposure.** Without hedging the ETH leg, persistent BNB/ETH directional moves (ETH ETF narrative 2024, Binance regulatory headwinds) bleed the strategy. A -8% stoploss fires on 4% BNB moves (67% stop-rate); widening to -25% reduces stops to 15 but each -25% loss wipes ~4 winning trades. No fixed stop calibration avoids the negative expectancy given single-leg exposure.
  2. **Trade frequency incompatible with the active-trading objective.** 67 trades over 1,400 days = 0.05 trades/day. BNB/ETH@4h is the only Phase 0 GO pair — there is no universe of additional GO pairs to scale frequency across. The strategy is inherently swing-trading frequency.
- **Key lesson:** The Phase 0 fee sweep (no stoploss, 60-day hold) correctly identified the spread mean-reversion signal. The Phase 1 failure is not a signal quality problem — it is a structural single-leg exposure problem and a frequency problem. Dual-leg would fix #1 but not #2.
- **Reusable infrastructure:** `user_data/scripts/cointpairs_phase0_validation.py` (v4) — the Phase 0 validation framework (ADF → EG → Johansen → Hurst → OU half-life → rolling β stability → fee sweep with time-stop rate check) is a complete diagnostic tool reusable for any future mean-reversion candidate.
- **Deep dive:** `CointPairsTrading_Deep_Dive.md` (ARCHIVED)
- **Files:** `user_data/strategies/CointPairsStrategy_V02.py`, `config/config_cointpairs_V02.json`, `user_data/scripts/cointpairs_phase0_validation.py`

---

#### Path Signatures / Lead-Lag (Candidate E)
- **Status:** ARCHIVED (2026-03-23) — Backtest FAIL
- **Duration:** One implementation pass + multi-range Binance futures backtests (2026-03-23)
- **Core idea:** Level-2 path cross-terms (Chen / Lévy antisymmetry) between **leader** (BTC) and **follower** log prices as a lead–lag score; enter ETH/SOL long/short with BTC momentum confirmation (`PathSignatureLeadLag_V01`, 1h).
- **What worked:** Native Freqtrade pattern (informative pairs, futures whitelist); **high trade count**; Docker layer with optional `iisignature`; configs that **omit** `freqai` entirely validate cleanly in Freqtrade 2026.2.
- **Why it failed:**
  1. **Stop losses swamped edge.** Long timerange backtest (~2022-01-06 → 2026-03-23): **profit factor ~0.89**, **~99% drawdown** on 1000 USDT dry-run wallet; **315** exits at **stop_loss** (~−12% each) versus smaller gains on **exit_signal** / **time_stop** — net expectancy negative.
  2. **MVP is directional / unhedged** on followers; literature and Rahimi-style work often emphasize **market-neutral** or **portfolio** construction, not single-leg alt beta.
  3. **Evaluation filter’s conditional pass resolved negatively:** out-of-sample profitability at our execution assumptions was **not** demonstrated.
- **Forward test:** Not run (per plan: skip when backtests decisively fail).
- **Reusable infrastructure:** `Dockerfile.freqtrade`, `config/config_pathsignatures_V01.json`, `docker-compose.pathsignatures.yml`; strategy retained as reference only.
- **Deep dive:** `PathSignatureLeadLag_Deep_Dive.md` (ARCHIVED)

---

### 4.2 ACTIVE

#### Liquidation Cascade Strategy (v1.0)
- **Status:** ACTIVE — Phase 3.5 (OI Filter Deployed, V05), since 2026-04-06
- **Core idea:** Detect forced liquidation cascades via Binance WebSocket data as primary alpha signal. Regime framework demoted to context filter only (CRISIS gate + EMA200 macro trend)
- **Architecture:** Sidecar process (WebSocket liquidation stream + OI polling) → signal file → Freqtrade 5m strategy reads signal → enter with-trend cascade, exit via 2×ATR target / 1×ATR stop / 30min time stop. 4x leverage
- **Current deployment:** DigitalOcean droplet, Docker, 5 pairs dry-run: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT. max_open_trades=5. Strategy V05.
- **Phase plan:** Phase 3 (dry-run) ✓ → Phase 3.5 (OI filter) ACTIVE → Phase 4 (hyperopt) → Phase 5 (additional pairs if needed) → Phase 6 (live capital)
- **Go/no-go for Phase 4:** profit factor >1.0, win rate >40%, time-stop rate <50% — reassess 2026-04-20
- **Phase 3 full results (2026-04-05 — 19 days, 389 trades):**
  - Win rate: 43.4% | Profit factor: 0.473 | Time-stop rate: 60.7% (236 trades, avg -1.18%)
  - Exit breakdown: `roi` avg +0.66% (98.6% win) · `trailing_stop_loss` avg +3.78% (100% win) · `time_stop` 0% win
  - Root cause confirmed: entry thresholds too loose — generates ~20 entries/day; genuine cascades ~1-2/pair/day
  - Raw liquidation USD uninformative — losers averaged HIGHER USD at entry (276K vs 206K)
- **Phase 3.5 OI retrospective (2026-04-06 — 304 trades, March 21–30):**
  - OI change rate discriminates 1.67× overall; 2.3× for short entries specifically
  - Winners mean |oi_change_pct_1m|=0.091; losers mean=0.054
  - Per-pair: XRP 4.74×, BNB 2.60×, ETH 1.36×, SOL 1.26×, BTC 0.96× (none)
  - V05 filter: `|oi_change_pct_1m| >= 0.06` on short entries for ETH/SOL/BNB/XRP only
  - Sidecar JSONL logging bug fixed (unguarded IO exception in `_write_snapshot` → reconnect loop)
- **Open questions:**
  1. Counter-trend cascade quality (short squeezes in bear markets)
  2. OI filter threshold review at 2026-04-20 — tighten if short win rate still <40%
  3. ATR-relative vs fixed ROI targets
  4. Funding rate as entry pre-condition
  5. BTC-specific filter — OI unhelpful; consider tighter CASCADE_MULT in sidecar for BTC only
- **Repo:** `freqtrade-scalper` (local, separate repo) — `strategies/LiqCascadeStrategy_V05.py`, `sidecar/liquidation_monitor.py`
- **Deep dive:** `LiquidationCascade_Deep_Dive.md` (in `freqtrade-scalper` repo)

#### OracleSurfer Strategy (v14 PROD) — *Retroactive entry; pre-dates this Research Log*
- **Note:** Active project in the separate `Freqtrade` repo (not `freqtrade-strategy-lab`). Added retroactively 2026-04-07. Version history spans v6–v14; tracked here from v12 dry-run results onward.
- **Status:** ACTIVE — v14 deployed and running 2026-04-06 (dry-run). Redeployed to DigitalOcean droplet via `git pull` + deploy script. Prior version: v12 (dry-run Feb 22 – Apr 6, 2026, 8 trades).
- **Core idea:** FreqAI XGBoost classifier trained on 4h features to predict 3-class market regime (BEAR / NEUTRAL / BULL) using triple-barrier labeling. Entry on Oracle signal + EMA200 trend alignment + RSI momentum + ADX strength gate. Exits via ROI ladder, trailing stop, or hard stop. Single pair: BTC/USDT:USDT futures, 1h execution timeframe. No sidecar — pure OHLCV + FreqAI.
- **Architecture:** FreqAI (XGBoost) → `&s_regime_class` column → entry filter (EMA200 + RSI + ADX) → Freqtrade execution. 3-year training window, 4h feature timeframe, retrain every 6h live. Features: Choppiness Index, KAMA distance, SMA200 valuation distance, VIX-Fix synthetic fear gauge, OBV oscillator, 5-period ROC.
- **Current deployment:** DigitalOcean droplet (same box as LiqCascade), Docker, BTC/USDT:USDT only, `dry_run: true`. Strategy: `OracleSurfer_v14_PROD`. Config: `config_sniper_BTC_DryRun.json`. FreqAI identifier: `Oracle_Surfer_v12_v2_DryRun`. API port: 8080.
- **v12 dry-run results (2026-02-22 – 2026-04-06, 8 trades):**
  - Win rate: 50% | Profit factor: 0.31 | Net P&L: -8.2% (-$81.20 on $990 starting capital)
  - Exit breakdown: 4× trailing SL (+2.98% avg) · 4× hard SL (-10.27% avg)
  - Root cause: asymmetric stop/reward. -10% hard stop vs ~3% avg winning exit → required ~77% WR to break even. At 50% WR, structurally unprofitable regardless of signal quality.
  - Failure mode: 4 consecutive short entries Feb–Mar stopped out during sustained BTC uptrend (~$63K → $75K). Oracle signal may have been correct directionally at entry but -10% stop gave market too much room to run against position first.
- **v12 → v14 structural overhaul (deployed 2026-04-06):**
  - **Stop tightened:** -10% → -5% (precision over survival — tighter entries need less room)
  - **ROI ladder added:** +10% any time / +7% at 8h / +5% at 16h / +3% at 24h (forces exit on stalling trades; replaces uncapped hold)
  - **Break-even moved earlier:** +3% → +2% (bridges gap before trailing activates at +5%)
  - **Entry tightened:** EMA200 trend alignment + RSI >50 / <50 momentum confirmation + ADX >20 (was >15). MACD removed (lagging vs Oracle signal).
  - **Oracle label horizon:** 96h → 48h (faster regime response); barrier changed to 1.5× ATR; bear priority added (when both barriers simultaneously hit, classify BEAR — safety bias against falling-knife longs)
  - **DCA disabled:** `position_adjustment_enable: false` (was true, max 3 adjustments)
  - **Training expanded:** 1yr → 3yr lookback (captures full BTC cycles); 2 shifted candles added; regularization added (subsample=0.8, colsample_bytree=0.8, n_estimators 100→200, learning_rate 0.1→0.05); retrain 1h → 6h
  - **Breakeven math fixed:** -5% stop vs ~7.5% avg target → breakeven at ~40% WR (robust). v12 required ~77% WR — an impossible bar at realistic signal quality.
- **Go/no-go for v14 continuation:** profit factor >1.0, win rate >45% — reassess after **15 closed trades or 2026-07-07**, whichever comes first. At v12's observed frequency (~1 trade/5–6 days) and v14's tighter entry filters, 15 trades represents ~3 months of swing-frequency forward testing — the minimum for a statistically meaningful read on this strategy class.
- **Open questions:**
  1. v14 dry-run results — assess win rate and PF after structural overhaul; see go/no-go above
  2. BTC-only vs multi-pair expansion — scale only after v14 proves profitable in dry-run
  3. Oracle signal quality at 48h horizon — does faster reaction improve entries or introduce label noise?
  4. Regime context — EMA200 + ADX sufficient or should CRISIS gate from LiqCascade be adopted?
- **Repo:** `Freqtrade` (local, separate repo) — `user_data/strategies/OracleSurfer_v14_PROD.py`, `user_data/config_sniper_BTC_DryRun.json`

---

### 4.3 CANDIDATES

*Approaches identified as potentially promising but not yet evaluated or attempted. Items here should be run through the Evaluation Filter (Section 6) before committing development time.*

#### CANDIDATE B: Funding Rate Arbitrage (Cross-Exchange or Spot-Perp)
- **Source:** Multiple — ScienceDirect (2025), practitioner guides, open-source implementations on GitHub
- **Core idea:** Exploit the funding rate mechanism on perpetual futures by holding delta-neutral positions (long spot + short perp, or long perp on one exchange + short perp on another). Profit comes from funding payments every 4–8 hours, not price direction.
- **Why it's interesting for us:** Structural alpha — exists because of how perpetual contracts are designed, not statistical pattern. Market-neutral by construction. High trade frequency (funding payments every 4–8h across many pairs = many "collection events" per day). Published research shows up to 115.9% over six months with losses capped at 1.92%. Average annual return estimated at ~19% in 2025. Can be automated. Scales across many pairs simultaneously.
- **Potential concerns:** Not a pure Freqtrade strategy — requires simultaneous positions on spot + futures (or two exchanges), which Freqtrade doesn't natively support. Would need custom execution logic. Capital-intensive for meaningful returns (funding payments are tiny per cycle). Funding rates can flip direction unpredictably. Execution risk on position entry/exit (slippage can eat the spread). May not meet the "high ROI" objective — this is more of a steady income strategy than a home-run approach.
- **Evaluation filter score:** Not scored — parked. Requires non-Freqtrade infrastructure; lower ROI potential than active candidates.
- **Complementarity to existing:** HIGH — completely different alpha source (carry/funding vs momentum/microstructure). Could run as a parallel "income floor" strategy while LiqCascade provides upside.

#### CANDIDATE C: Crypto Volatility Commonality Forecasting
- **Source:** SSRN (Djanga, Cucuringu & Zhang, Jan 2025) — Oxford-Man Institute authors
- **Core idea:** Use cross-asset realized volatility commonality (the fact that crypto volatility co-moves across assets) to forecast next-day intraday volatility using ML models. The paper then trades crypto options based on the volatility forecast, but the volatility forecasting framework could be repurposed for volatility-timing a directional strategy.
- **Why it's interesting for us:** Oxford-Man pedigree. Source code published on GitHub. The volatility forecast itself could serve as a dynamic filter for our existing strategies (e.g., scale LiqCascade leverage based on forecasted vol, or time entries during forecasted high-vol windows). Cross-asset features mean more signal from the same data.
- **Potential concerns:** Original application is options trading, which we don't do. Repurposing the vol forecast as a strategy filter is our interpretation, not the paper's claim. Realized volatility computation requires high-frequency data. May add complexity without clear standalone alpha.
- **Evaluation filter score:** Not scored — reclassified as a technique, not a standalone strategy. See Techniques Library if needed as a volatility-timing layer.
- **Complementarity to existing:** MEDIUM — not a standalone strategy but could enhance LiqCascade and future strategies as a volatility-timing layer.

#### CANDIDATE D: CNN Trend Detection on 15m Crypto Data with Stationarity Preprocessing
- **Source:** SSRN (Asareh Nejad et al., Apr 2024)
- **Core idea:** A novel preprocessing method that makes indicator + candlestick data stationary while preserving inter-feature relationships, then feeds it into a CNN for 15-minute trend prediction on crypto. Achieves 53.9% accuracy with 4.18% average biweekly returns, beating buy-and-hold.
- **Why it's interesting for us:** 15m timeframe aligns with active trading frequency objective. The stationarity preprocessing is the novel contribution — could be applied to any model, not just CNN. Directly applicable to crypto. The accuracy is modest but the preprocessing technique might be the real takeaway.
- **Potential concerns:** 53.9% accuracy is barely above coin-flip — reminds us of RAME's lesson about accuracy not equaling edge. Paper is from 2024, no out-of-sample validation mentioned. CNN for time series is somewhat dated compared to newer architectures. May be a "technique to borrow" rather than a "strategy to implement."
- **Evaluation filter score:** Not scored — reclassified as a technique. Preprocessing method captured in Techniques Library (Section 7.2).
- **Complementarity to existing:** MEDIUM — the preprocessing technique could be valuable as infrastructure for any future ML-based strategy.

#### CANDIDATE E: Path Signatures for Lead-Lag Detection
- **Status:** ARCHIVED (2026-03-23) — Backtest FAIL
- **See Section 4.1 Archived for full post-mortem.** Deep dive: `PathSignatureLeadLag_Deep_Dive.md`

#### Cointegration Pairs Trading (CointPairs) — formerly Candidate F
- **Status:** ARCHIVED (2026-03-22) — Phase 1 FAIL
- **See Section 4.1 Archived for full post-mortem.**
- **Source:** Multiple — Amberdata blog series (2025, comprehensive 5-part guide), arXiv:2109.10662 (Tadi, 2021), Frontiers in Applied Mathematics (Jan 2026, DNN/LSTM on crypto pairs), extensive practitioner literature.
- **Core idea:** Identify crypto pairs that are cointegrated (stable long-term equilibrium relationship), compute the spread between them, and trade mean reversion of that spread. Go long the underperformer and short the outperformer when the spread deviates beyond a z-score threshold; close when it reverts. Market-neutral by construction.
- **Why it's interesting for us:** Well-established strategy class with decades of evidence across asset classes — this is exactly the kind of "established approach that could be enhanced" our updated Objectives encourage. Works on standard OHLCV data (no sidecar). Freqtrade supports simultaneous long/short on different pairs. Market-neutral = lower drawdowns. High trade frequency if run across many pairs simultaneously (each pair generates independent signals). Can be enhanced with multiple Techniques Library items: fractional differentiation for spread preprocessing, conformal prediction for entry confidence, Kalman filter for dynamic hedge ratios. A Jan 2026 Frontiers paper uses DNN/LSTM to forecast the spread, adding ML on top of the statistical foundation. Amberdata's backtested example shows 62% total return over multi-year period with Sharpe ~0.93 and ~16% annualized — and that's without leverage or ML enhancement.
- **Potential concerns:** Cointegration relationships can break down, especially during regime changes (our RAME experience is relevant — we know regimes shift). Requires holding simultaneous long+short positions, which ties up capital. The 16% annualized from the Amberdata example may not clear our "materially outperform traditional investments" bar without leverage or ML enhancement. Pair selection is critical and needs periodic re-evaluation. Transaction costs on both legs eat into the spread profit.
- **Key implementation question:** Can Freqtrade manage simultaneous long/short positions on two different pairs as a single "trade"? If not, we'd need a coordination layer. This is an architecture question to resolve early.
- **Evaluation filter score:** Scored 2026-03-22 — see below
- **Complementarity to existing:** HIGH — market-neutral (vs directional LiqCascade), mean-reversion (vs momentum), multi-pair by nature. Could run as a concurrent strategy providing steady returns while LiqCascade captures explosive moves.

**CANDIDATE F — EVALUATION FILTER:**

| # | Criterion | Assessment | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Standard OHLCV data only. Cointegration tests, spread computation, z-scores — all computed from price data available via Binance API / CCXT. No special data source needed. | **PASS** |
| 2 | **Compute fit** | Engle-Granger and Johansen cointegration tests are lightweight (statsmodels). Z-score computation is trivial. Even the DNN/LSTM spread forecasting variant from the Frontiers paper could train on a local machine in hours, not days. Inference is CPU-only. | **PASS** |
| 3 | **Freqtrade compatibility** | Freqtrade supports simultaneous long/short positions on different pairs in futures mode. The strategy would: (1) compute spread and z-score in `populate_indicators()` using informative pairs, (2) enter long on the underperformer and short on the outperformer when z-score exceeds threshold, (3) exit both when z-score reverts to zero. The coordination challenge is managing the two legs as a logical unit — Freqtrade treats them as independent trades. This requires careful logic in `confirm_trade_entry()` and `custom_exit()` to ensure both legs open/close together. Nontrivial but architecturally feasible — no sidecar needed. | **CONDITIONAL PASS** — feasible but requires custom coordination logic for paired entries/exits |
| 4 | **Out-of-sample evidence** | Strong. The Amberdata backtested example shows 62% total return with Sharpe ~0.93 over a multi-year period (2021–2024) including bull and bear markets. The arXiv paper (Tadi, 2021) uses minute-level data with realistic execution simulation and outperforms buy-and-hold. The Frontiers paper (Jan 2026) uses dynamic Johansen cointegration with DNN/LSTM and tests on 2018–2025 data. Multiple independent validations across different time periods and methodologies. | **PASS** |
| 5 | **Clear mechanism** | Yes. Cointegration is a well-established econometric concept (Engle & Granger, Nobel Prize 2003). The mechanism: when two assets share a common stochastic trend (e.g., BTC and ETH both driven by overall crypto market sentiment), temporary deviations from their equilibrium ratio are corrected by market forces — arbitrageurs, correlated flows, and shared fundamentals pull them back together. This has been validated across asset classes for 30+ years. | **PASS** |
| 6 | **Complementarity** | HIGH. LiqCascade is directional, event-driven, momentum. This is market-neutral, continuous, mean-reversion. They're almost perfectly negatively correlated in terms of when they perform best — mean reversion thrives in ranging markets where momentum fails, and vice versa. Running both concurrently would provide genuine strategy diversification. | **PASS** |
| 7 | **Implementation scope** | 1 week is feasible for an MVP. Day 1: download multi-pair data, run cointegration tests (Engle-Granger + Johansen) across candidate pairs (BTC/ETH, ETH/SOL, BTC/SOL, etc.), identify 2–3 cointegrated pairs. Day 2: compute spread, hedge ratio, z-score time series. Validate stationarity (ADF test) and mean-reversion intensity (Hurst exponent). Day 3: build Freqtrade strategy with paired entry/exit logic. Day 4: backtest with fee-inclusive simulation. Day 5: fee economics sweep + out-of-sample validation. All on standard OHLCV data. | **PASS** |

**Filter score: 6/7 PASS, 1/7 CONDITIONAL PASS → Overall: PASS**

#### CANDIDATE G: Cross-Sectional Crypto Momentum
- **Status:** **PARKED (2026-03-29)** — **Empirically weak** after Phase 1 baseline backtests. **All code, configs, and docs retained** in freqtrade-strategy-lab (`XSMomentumStrategy_V01.py`, `config_xsmom.json`, `CrossSectionalMomentum_*.md`). **Not** a live-trading **GO**. **Active development paused** until a **reopen trigger** (below) is met.

- **Layman's summary (Phase 1 — read this first):** We built a simple “horse race” on ~22 futures: rank coins by recent performance, **buy the leaders**, and in the main version **also bet against the laggards** (shorts), then repeat on a fixed schedule (daily or every few hours). No ML—just prices and rules. **Only the slower, daily, long+short version** was **modestly positive** over the full test window, and even that was **fragile** (gains and losses **mostly offset**, profit factor ~**1**, **large drawdowns**). The **faster (4h) version** and **long-only** versions **failed** badly in backtest. **Shorts mattered** for dollar P&amp;L in the winning configuration—dropping them hurt, contrary to a naive “winners only” story. **Year-by-year**, results were **not steady**: strong in one slice, weak in another, **sharply negative in 2024** in the test. **Bottom line:** implementation is **sound for reuse**, but the **economic case** for deploying this baseline **as-is** is **weak**—hence **PARKED**.

- **Parking policy / reopen triggers:** **Do not** continue “routine” Phase 2 tuning on G without a **new lever**. **Reopen** Candidate G (resume research or open a child project) **only** when at least one of the following is true: (1) A **named add-on or tool** is available that **plausibly addresses a documented weakness** (e.g. **2024** attribution / regime breakdown, **funding**-aware simulation, **narrower universe** hypothesis, **vol-targeted** risk layer, **external** filter from Techniques Library, or a **new ranking signal** such as a **validated** signature/lead-lag design — see **Candidate I**). (2) **New data or constraints** change the test (e.g. different venue, fee tier, or mandate). **Do not** reopen for unfocused hyperopt on the same baseline alone.

- **Historical note:** Phase 1 complete **2026-03-29** — see **`CrossSectionalMomentum_Phase1_Summary.md`:** **V01_1d** ~**+17%** full-sample 2022–2025 but **unstable by year** (+71% / +14% / −40% calendar slices); **4h grid** and **long-only** **NO-GO**; regime tilt **not** a net win vs control when fairly compared.

- **Source:** Drogen, Hoffstein & Otte (SSRN 2023) "Cross-sectional Momentum in Cryptocurrency Markets"; Han, Kang & Ryu (SSRN 2023) "Time-Series and Cross-Sectional Momentum: Comprehensive Analysis under Realistic Assumptions"; ScienceDirect (2025) "Cryptocurrency market risk-managed momentum strategies"; Rohrbach et al. (2017) high-frequency momentum on crypto.
- **Core idea:** Rank a universe of 10–30 crypto assets by recent returns (formation period: 1h to 30 days). Go long the top-ranked winners and short the bottom-ranked losers. Rebalance at the holding period frequency. The cross-sectional variant exploits relative performance differences across assets rather than absolute price direction.
- **Why it's interesting for us:** Directly addresses our two biggest recent failure modes. (1) **High frequency by design:** with hourly formation periods across 20+ pairs, this generates many trades per day — the opposite of CointPairs' 0.05 trades/day problem. (2) **Per-trade moves well above fee floor:** hourly crypto momentum moves are typically 50–300+ bps, far above our 10 bps round-trip fee. Works on standard OHLCV data, no sidecar needed. Established strategy class with strong academic evidence. Multiple enhancement paths: risk-managed variants (volatility-scaling), winner-only variants (losers rebound — documented by Han et al.), and **future** path-signature-style ranking (**Candidate I** — *not* the archived Candidate E MVP). The literature specifically finds that cross-sectional momentum works *better* for crypto than for traditional currencies (Rohrbach et al.).
- **Potential concerns:** Momentum crashes are documented in crypto (Grobys 2025) — can experience severe tail losses. Han et al. (2023) find that under realistic assumptions (fees, daily price fluctuations, liquidation risk), many momentum portfolios are actually liquidated and statistically significant returns become insignificant. The momentum effect is concentrated among winners — losers often rebound and inflict losses. Risk-managed variants partially address crashes but add complexity. Need to validate that the effect persists at our specific formation/holding periods on Binance Futures perpetuals.
- **Combination potential (→ Candidate I):** In principle, **signature-derived features** or other **add-ons** could augment ranking if they target a **specific** Phase 1 weakness. **Candidate E (Path Signatures) MVP is archived (2026-03-23)** — treat that implementation as closed. **Candidate I** remains **reserved** as one **possible** reopen path **only** with a **new** validated design — **not** tied to “G must work standalone first” (**G** is **parked**, not a blocking milestone for scoping I as a **separate** hypothesis).
- **Evaluation filter score:** Scored 2026-03-22 — see below
- **Complementarity to existing:** HIGH — LiqCascade is event-driven (discrete cascades), this is systematic (continuous ranking). LiqCascade trades single assets, this trades relative performance across a universe. Different alpha source, different timing, different market conditions.

**CANDIDATE G — EVALUATION FILTER:**

| # | Criterion | Assessment | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Standard OHLCV data only. Returns computed from close prices across 10–30 pairs. All available via Binance API / CCXT / freqtrade download-data. No special data source needed. | **PASS** |
| 2 | **Compute fit** | Trivial compute. Returns calculation, ranking, and rebalancing are basic pandas operations. Even with 30 pairs at 1h timeframe, the entire pipeline runs in milliseconds. No ML model needed for the base version (pure ranking). Risk-managed variant adds volatility scaling — still trivial. No GPU needed. | **PASS** |
| 3 | **Freqtrade compatibility** | Requires a cross-pair ranking mechanism that Freqtrade doesn't natively provide. Workaround: load all pair data via `DataProvider.get_pair_dataframe()` in `populate_indicators()`, compute returns and rank across pairs, store rankings in `custom_info` dict or compute in `bot_loop_start()`. Only issue entry signals for top-ranked (long) and bottom-ranked (short) pairs. This pattern has been discussed in Freqtrade GitHub issues and is architecturally feasible. More elegant than CointPairs' paired-trade coordination — each trade is independent, just entry-filtered by ranking. | **PASS** |
| 4 | **Out-of-sample evidence** | Strong and specific to crypto. Drogen et al. (SSRN 2023): consistent excess returns vs BTC benchmark using 30-day/7-day formation/holding. Han et al. (SSRN 2023): comprehensive analysis under realistic assumptions (fees, liquidation risk) — time-series momentum is strong, though cross-sectional is weaker and winner-concentrated. ScienceDirect (2025): risk-managed momentum validated on crypto. Rohrbach et al.: high-frequency hourly momentum tested on 7 cryptos with positive results. Multiple independent teams, different time periods, different methodologies. | **PASS** |
| 5 | **Clear mechanism** | Yes. Crypto momentum is driven by information diffusion asymmetry, behavioral overreaction/underreaction, and attention-driven capital flows. Unlike equities where momentum is well-arbitraged, crypto markets remain less efficient due to: fragmented liquidity, retail-dominated participation, narrative-driven capital rotation, and 24/7 trading without institutional circuit breakers. The academic literature specifically documents that momentum works *better* in crypto than in traditional markets (higher Sharpe for more volatile assets). | **PASS** |
| 6 | **Complementarity** | HIGH. LiqCascade is event-driven momentum on single assets — it trades *specific events* (liquidation cascades). Cross-sectional momentum trades *relative performance* across a universe — it doesn't need any specific event, just persistent return dispersion across assets. Different signal source, different entry timing, different market conditions. LiqCascade fires during volatility spikes; cross-sectional momentum captures steady capital rotation during trending periods. | **PASS** |
| 7 | **Implementation scope** | 1 week is feasible for an MVP. Day 1: download 1h OHLCV for 20+ pairs, compute formation-period returns, build ranking logic. Day 2: implement strategy in Freqtrade using `custom_info` for cross-pair ranking; long top N, short bottom N. Day 3: backtest with fee-inclusive simulation (10 bps round-trip). Day 4: fee economics sweep (Technique 7.3) across formation periods (1h, 4h, 24h, 7d) and holding periods (1h, 4h, 24h). Day 5: risk-managed variant (volatility-scaled position sizing) + out-of-sample validation. Winner-only variant if losers underperform (per Han et al. finding). All on standard OHLCV data, no infrastructure to build. | **PASS** |

**Filter score: 7/7 PASS → Overall: STRONG PASS**

**Co-investigator note:** This is the first candidate to score a clean 7/7 — no conditional passes. The Freqtrade compatibility issue that tripped up CointPairs (criterion 3) is structurally simpler here because each trade is independent (you're just filtering which pairs to enter based on ranking, not coordinating paired legs). The fee economics concern that killed LOB (criterion 1/7 in practice) is naturally addressed because hourly crypto momentum moves are an order of magnitude above the fee floor. The trade frequency concern that killed CointPairs is addressed by design — many pairs × short holding periods = many trades. This candidate has the cleanest path from evaluation to implementation of anything we've seen.

**Phase 1 empirical gate (2026-03-29):** The **7/7 filter** scores **feasibility and literature fit**, not **live profitability**. Multi-year Freqtrade backtests on the baseline grid are a **separate** hurdle: **passed** for “code + one non-absurd variant,” **failed** for “ready to trade” or “stable edge.” Both statements can be true; the **layman's summary** and **parking policy** above reflect the empirical layer.

**Active development (2026-03-29):** **Paused.** G is **PARKED** — treat as **reference implementation**, not a roadmap item, until a **reopen trigger** is satisfied.

#### CANDIDATE H: On-Chain / Whale Flow Signals (reclassified as Technique)
- **Status:** RECLASSIFIED — better suited as a Technique/filter than a standalone strategy
- **Source:** Practitioner ecosystem — Nansen, Glassnode, Whale Alert, Arkham, CryptoQuant, Santiment, Dune Analytics
- **Core idea:** Use exchange inflow/outflow data, whale wallet accumulation/distribution patterns, and stablecoin supply changes as leading indicators for directional trades.
- **Why it didn't become a full candidate:** (1) Data frequency is typically daily or at best hourly — incompatible with our active-trading frequency objective for a standalone strategy. (2) Most tools are designed for discretionary analysis, not automated trading. (3) Signal-to-noise ratio for fully automated execution is unproven. (4) Would require a sidecar to ingest API data, adding infrastructure.
- **Where it fits:** Added to Techniques Library (Section 7) as a potential macro filter — e.g., only take LiqCascade or momentum entries when whale accumulation trend score is favorable. Similar role to the CRISIS gate but using on-chain data instead of ATR.

#### CANDIDATE I: Path Signature-Enhanced Cross-Sectional Momentum (RESERVED)
- **Status:** RESERVED — **Candidate E MVP archived (2026-03-23).** This combination is **not** tied to `PathSignatureLeadLag_V01`.
- **Core idea:** Replace or augment the simple return-based ranking in cross-sectional momentum with signature-derived features that capture the *shape* and *lead-lag structure* of recent multi-asset price paths. Instead of ranking by "which asset had the highest return over the last N hours," rank by "which asset's path signature indicates it is currently a leader in the information diffusion process." This could improve ranking accuracy, reduce momentum crash exposure (signatures may detect when lead-lag structure is breaking down), and provide a richer signal than raw returns.
- **Prerequisites (updated 2026-03-29):** **Candidate G** is **implemented and PARKED** (empirically weak — see G entry). **Do not** wait for “G standalone profit” before **scoping** I. **Build or evaluate I only** when treating it as a **new hypothesis** with **OOS protocol**, and **only if** the proposal **explicitly ties** the signature (or other) layer to a **named weakness** of the parked G baseline (e.g. regime instability, crash risk). **Not** the archived E implementation.
- **Do not evaluate, plan, or build without** the above scoping and a **reopen** decision on G or I.

#### CANDIDATE J: Ensemble Donchian Trend-Following on Rotational Crypto Portfolio
- **Status:** **PARKED (2026-04-06)** — **Phase 0 NO-GO** on fee-inclusive Freqtrade backtests. The **7/7 evaluation filter** remains a score on **literature / feasibility / implementation fit**, not **live edge**; empirical Phase 0 failed Dev Plan gates (profitability, robustness). **Code, config, and sweep artifacts retained** in `freqtrade-strategy-lab` (`EnsembleDonchianStrategy_V01` / `V02`, `config_donchian.json`, `user_data/scripts/donchian_phase0_sweep.py`, `user_data/results/donchian_phase0_sweep_*.md`). **Do not** schedule further work unless reopened as a **new hypothesis** (different universe, filters, or execution assumptions) with a fresh Phase 0 charter.
- **Phase 0 outcome (summary):** Regime splits and full-sample runs **strongly negative** under realistic per-side fees (`--fee 0.0005`); **ATR** trailing worse than Donchian-lower; higher **entry thresholds** reduce loss but do not clear **profit factor / go-forward** bars. See `user_data/results/donchian_phase0_sweep_20260406_105346.md` (representative sweep table).
- **Former paper status:** CANDIDATE — surfaced in Sweep #4, evaluated 2026-03-31
- **Source:** Zarattini, Pagani & Barbon (SSRN, April 2025, revised Oct 2025) — Swiss Finance Institute. "Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins." 38 pages. *Note: originally reviewed in Sweep #1 and dismissed as "conventional trend-following." Re-evaluated after G's parking revealed that the ensemble + rotational portfolio construction is the critical differentiator.*
- **Core idea:** Aggregate multiple Donchian channel breakout models (lookbacks: 5, 10, 20, 30, 60, 90, 150, 250, 360 days) into a single ensemble signal. Go long when price closes above the upper channel, exit via trailing stop at the lower channel. Apply to a rotational portfolio of the top 20 most liquid coins. Volatility-based position sizing (inverse vol scaling). Long-only by design — enters long on breakouts, exits to flat when trend weakens.
- **Why it's interesting for us:** Sharpe > 1.5 net-of-fees. CAGR 30%. Annualized alpha 10.8–14% vs BTC. Survivorship-bias-free dataset 2015–2025. Multi-pair by design = many trades. No ML, no sidecar, pure OHLCV. Transaction cost mitigation explicitly addressed. The Turtle Traders methodology adapted to crypto with genuine novelty in the ensemble aggregation. Reuses G's rotational portfolio infrastructure (`DataProvider`, `custom_info`, vol-scaling).
- **Why it's different from G:** G ranked by *returns* and rebalanced on a schedule — regime-unstable (−40% in 2024). J ranks by *trend state* (breakout above Donchian channel) and exits on *trailing stop*, not periodic rebalance. The ensemble over 9 lookback periods smooths regime transitions. Long-only by design — no short-side losses.
- **Potential concerns:** Paper uses daily timeframe — need to validate at 1h–4h for our frequency objective. Donchian breakout is a simple, well-known signal — alpha may decay. Holding periods can be weeks in the paper (too slow?). Shorter Donchian lookbacks on hourly data may address this but are untested in the paper.
- **Combination potential:** Could combine with K's multi-timeframe confirmation (daily Donchian ensemble as macro filter, hourly for entry timing). Could use G's ranking infrastructure as a universe filter (only apply Donchian to top-ranked pairs).
- **Evaluation filter score:** Scored 2026-03-31 — see below
- **Complementarity to existing:** HIGH — LiqCascade is event-driven (discrete cascades), J is systematic trend-following (continuous breakout detection). Different signal source, different entry timing. LiqCascade fires during volatility spikes; trend-following captures sustained directional moves.

**CANDIDATE J — EVALUATION FILTER:**

| # | Criterion | Assessment | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Standard OHLCV data only. Donchian channels computed from high/low prices across 20 pairs. All available via Binance API / CCXT / freqtrade download-data. No special data source needed. | **PASS** |
| 2 | **Compute fit** | Trivial compute. Donchian channels are rolling max/min — basic pandas/TA-Lib. Ensemble signal is averaging 9 binary breakout signals. Volatility scaling is rolling std. Even with 20 pairs × 9 lookbacks, runs in milliseconds. No GPU needed. | **PASS** |
| 3 | **Freqtrade compatibility** | Excellent. Donchian channels are TA-Lib standard indicators (`ta.MAX`, `ta.MIN`). Ensemble signal is averaging columns. Rotational portfolio uses the same `DataProvider` + `custom_info` pattern already built and tested for G. Trailing stop exit is native to Freqtrade (`custom_stoploss()`). Each trade is independent — no paired-leg coordination. Reuses most of G's architecture. | **PASS** |
| 4 | **Out-of-sample evidence** | Strong. Zarattini et al. (SSRN 2025, Swiss Finance Institute): Sharpe > 1.5, CAGR 30%, alpha 10.8–14% vs BTC on survivorship-bias-free data 2015–2025. Walk-forward tested. Transaction costs explicitly modeled. The underlying Donchian breakout methodology has decades of evidence across traditional asset classes (Turtle Traders, managed futures industry). Beluská & Vojtko (SSRN 2024) confirm trend-following works in BTC through Aug 2024. Mesíček & Vojtko (SSRN Nov 2025) confirm multi-timeframe trend-following on BTC 2018–2025. Multiple independent teams, different periods, different methodologies. | **PASS** |
| 5 | **Clear mechanism** | Yes. Trend-following exploits serial correlation in returns — documented across all asset classes for 40+ years. In crypto specifically: retail-dominated participation, narrative-driven capital flows, and reflexive feedback loops (leverage liquidations amplify trends) create stronger serial correlation than in traditional markets. The Donchian ensemble is mechanistically clear: it detects when price is making new highs/lows relative to multiple historical windows simultaneously, which is a structural definition of a trend. | **PASS** |
| 6 | **Complementarity** | HIGH. LiqCascade is event-driven momentum on single assets during volatility spikes. J is systematic trend-following across a portfolio during sustained directional moves. Different signal source (breakout vs liquidation cascade), different market conditions (trending vs volatile), different entry timing (continuous vs discrete events). Also complements the *parked* G — G used return ranking (relative performance), J uses breakout state (absolute trend). | **PASS** |
| 7 | **Implementation scope** | 1 week is feasible for an MVP. Day 1: download 1h OHLCV for 20+ pairs, compute Donchian channels at 9 lookback periods (converted to hourly equivalents), build ensemble signal. Day 2: fee-inclusive parameter sweep across lookback grids and holding periods — Phase 0 validation before writing Freqtrade code (per Lesson #7). Day 3: implement strategy in Freqtrade reusing G's `DataProvider`/`custom_info` architecture. Day 4: backtest with regime splits (2022 bear, 2023 range, 2024–2025 bull). Day 5: volatility-scaled sizing + out-of-sample validation. All on standard OHLCV data, significant infrastructure reuse from G. | **PASS** |

**Filter score: 7/7 PASS → Overall: STRONG PASS**

**Co-investigator note:** This is the second candidate to score a clean 7/7. The key differentiator from G is the *signal source*: breakout detection (binary: is price above/below the channel?) is mechanistically different from return ranking (continuous: which asset had the highest return?). Breakout signals are inherently robust to the regime instability that killed G — a trend breakout doesn't care whether you're in a bull or bear market, it just detects when a new trend is starting. The ensemble over 9 lookback periods adds further robustness. The paper was dismissed in Sweep #1 as "conventional" — but after seeing G's regime instability firsthand, the ensemble's regime-smoothing property is exactly what we need. Sometimes the established approach *is* the right one, with the right enhancements.

**Update 2026-04-06 — empirical outcome:** Despite the theoretical appeal, **our** implementation and universe did **not** translate into profitable, robust backtests under project fee assumptions and regime splits. The candidate is **PARKED** per Phase 0 NO-GO. **Lesson reinforced:** **7/7 on the evaluation filter does not imply Phase 0 GO** — the filter scores *buildability and evidence in the literature*, not *your* PnL path.

**Important context (historical):** The paper uses *daily* data; the MVP used **`1d` Donchian merged to `1h` execution** (and a pure-`1d` variant) to respect Binance/Freqtrade data limits. Phase 0 **completed** with a clear **NO-GO** for further investment without a redesigned hypothesis.

#### CANDIDATE K: Multi-Timeframe Trend Confirmation (MACD Daily-Hourly)
- **Status:** CANDIDATE — surfaced in Sweep #4, not formally evaluated (recommended as enhancement/filter, not standalone)
- **Source:** Mesíček & Vojtko (Quantpedia/SSRN, Nov 2025) — "How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin." Beluská & Vojtko (SSRN Oct 2024) — "Revisiting Trend-following and Mean-Reversion Strategies in Bitcoin."
- **Core idea:** Use daily MACD as macro trend filter, hourly MACD for entry timing. Only enter when both timeframes agree. Exit via trailing stop. Progressive enhancement: naive → confirmed → trailing exit.
- **Why it's interesting for us:** Directly addresses Lesson #4 (short-term indicators lie in macro trends). The multi-timeframe architecture is essentially a built-in macro filter. Hourly = higher frequency. No ML, no sidecar.
- **Potential concerns:** Single asset (BTC) in the paper. MACD is extremely well-known — edge may be arbitraged. Lower standalone frequency than multi-pair approaches.
- **Best use:** As a **filter/enhancement** for **trend or breakout follow-ons** (e.g. future candidates) or for LiqCascade (only take cascade entries when macro trend confirms direction). *Formerly framed as a J Phase 2 add-on; J is now **PARKED**.* Not recommended as standalone given single-asset scope.
- **Evaluation filter score:** Not formally scored — recommended as technique/filter rather than standalone strategy. If applied as a filter to a **multi-timeframe trend or breakout** design, it adds little data cost, no ML, and addresses Lesson #4 directly.

#### CANDIDATE M: AdaptiveTrend — Systematic Multi-Pair Momentum with Adaptive Portfolio Construction
- **Status:** CANDIDATE — surfaced in Sweep #5 (2026-04-07); **#1 build priority** (§4.4); **Dev Plan created 2026-04-07** (`AdaptiveTrend_Dev_Plan.md`); Phase 0 not yet started
- **Source:** Bui & Nguyen (arXiv 2602.11708, February 2026) — "Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets"
- **Core idea:** Pure rate-of-change momentum signal (`(P_t - P_{t-L}) / P_{t-L}`) on 6h candlesticks across 150+ crypto pairs. Three enhancements over classical TSMOM: (1) ATR-calibrated dynamic trailing stops (`stop = max(prior_stop, price - 2.5×ATR)`), (2) monthly rolling-Sharpe-based pair selection (enter only pairs achieving SR ≥ 1.3 for longs / 1.7 for shorts on prior month's data), (3) 70/30 asymmetric long-short allocation grounded in crypto's empirical upward drift.
- **Why it's interesting for us:** This directly addresses the recurring translation failure in prior sweeps. The signal is pure OHLCV rate-of-change — no ML model, no sidecar, no special data feed. The trailing stop mechanism is essentially identical to what LiqCascade already uses (ATR-based). The multi-pair architecture satisfies our trading frequency objective. The 70/30 allocation provides bear-market protection without going delta-neutral. Classical time-series momentum has decades of live practitioner deployment across asset classes; the portfolio construction enhancements are the modern element. The applied history criterion is strongly satisfied.
- **Performance (OOS: Jan 2022 – Dec 2024, 36 months, 150+ pairs):**

  | Strategy | Ann. Ret. | Ann. Vol. | Sharpe | MDD | Calmar | Sortino |
  |---|---|---|---|---|---|---|
  | **AdaptiveTrend 70/30** | **40.5%** | **16.8%** | **2.41** | **-12.7%** | **3.18** | **3.62** |
  | AdaptiveTrend 50/50 | 34.2% | 15.1% | 2.12 | -14.3% | 2.39 | 3.01 |
  | Vol-Scaled TSMOM | 22.8% | 10.0% | 1.83 | -16.1% | 1.42 | 2.15 |
  | TSMOM-1M | 18.4% | 21.3% | 0.65 | -34.8% | 0.53 | 0.89 |
  | EW Buy-and-Hold | 8.3% | 52.1% | 0.07 | -72.4% | — | — |
  | BTC Buy-and-Hold | 12.6% | 48.7% | 0.17 | -64.1% | — | — |

- **Regime breakdown (rolling 60d BTC return):**

  | Regime | Ann. Return | Sharpe | MDD | Win Rate | Avg Trade PnL |
  |---|---|---|---|---|---|
  | Bull (>+15%) | 68.3% | 3.42 | -7.1% | 54.2% | +1.82% |
  | Sideways | 18.7% | 1.87 | -9.4% | 47.8% | +0.63% |
  | Bear (<-15%) | -4.2% | -0.31 | -12.7% | 41.3% | -0.21% |

  Strategy profits in bull and sideways regimes (covers most calendar time); bear regime loses money but MDD is contained at -12.7% vs -64% for BTC buy-and-hold.

- **Ablation study — component contributions:**

  | Configuration | Sharpe | MDD |
  |---|---|---|
  | Full AdaptiveTrend | 2.41 | -12.7% |
  | w/o Dynamic Trailing Stop | 1.68 | -22.4% |
  | w/o Sharpe Ratio Selection | 1.92 | -19.1% |
  | w/o Market Cap Filter | 2.05 | -17.8% |
  | w/o Asymmetric Allocation | 2.12 | -14.3% |
  | **Fixed Parameters (no monthly opt.)** | **1.34** | **-28.6%** |

  **Critical MVP implication:** monthly optimization contributes +1.07 Sharpe (from 1.34 to 2.41). An MVP with fixed parameters gets ~Sharpe 1.34 — still above 1.0 but materially below headline numbers. The trailing stop is the single highest-value component (+0.73 Sharpe). Since we already implement ATR trailing stops natively (LiqCascade, OracleSurfer), this is the easiest win.

- **Timeframe comparison (net of 4 bps costs):**

  | TF | Sharpe | MDD | Trades/Month |
  |---|---|---|---|
  | H1 | 1.54 | -21.3% | 847 |
  | H4 | 2.08 | -15.6% | 213 |
  | **H6** | **2.41** | **-12.7%** | **142** |
  | H8 | 2.18 | -14.1% | 108 |
  | D1 | 1.63 | -19.4% | 41 |

  H6 is explicitly confirmed as optimal. H1 is significantly worse (Sharpe 1.54) — not just marginally.

- **Fee sensitivity (our cost vs paper):**
  - Paper baseline: 4 bps/trade (likely per side → 8 bps round-trip)
  - Our cost: 5 bps/side → 10 bps round-trip
  - Paper sensitivity: 8 bps → Sharpe 2.01 · 12 bps → Sharpe 1.62
  - At our 10 bps: estimated Sharpe ~1.85 (interpolated). Still strong.

- **Exact algorithm (from paper pseudocode):**
  - Entry: `MOM_t = (P_t - P_{t-L}) / P_{t-L}`; long if `MOM_t > θ_entry`, short if `MOM_t < -θ_entry`
  - Trailing stop: `S_t = max(S_{t-1}, P_t - α × ATR_t)` where α ≈ 2.5 (optimal range: 2.0–3.5)
  - Close when `P_t < S_t`
  - Monthly: grid-search optimize `(θ_entry, α, L)` on prior month; select assets with prior-month SR ≥ 1.3 (longs) / 1.7 (shorts)
  - Long universe: top-15 by market cap. **Short universe: bottom-KS by market cap (lower-liquidity altcoins)**

- **Stack translation assessment:**
  - **Signal (MOM_t):** `PASS` — single arithmetic formula on 6h OHLCV, Freqtrade-native
  - **ATR trailing stop:** `PASS` — identical to existing `custom_stoploss()` in LiqCascade/OracleSurfer
  - **Monthly Sharpe-based selection:** `CONDITIONAL` — grid search over prior month needed; for MVP use fixed params + fixed whitelist. Plan monthly optimization for Phase 1.
  - **70/30 allocation:** `CONDITIONAL` — approximate via `max_open_trades` split (e.g., 10 long slots / 4–5 short slots) and equal stake_amount per slot
  - **Market cap data:** `PASS` — CoinGecko free API daily, or hardcoded top-15 reviewed monthly
  - **Short universe (small caps):** `FLAG` — paper uses bottom-KS by market cap = lower-liquidity assets. For MVP, restrict short universe to liquid alts only (ETH, SOL, BNB, etc.) to avoid slippage surprises
- **Key risks (updated from full paper):**
  - Monthly optimization contributes +1.07 Sharpe — MVP without it gets ~1.34 baseline, not 2.41. This is the most important thing to understand before Phase 0.
  - Short portfolio targets small-cap assets — slippage risk at scale; use liquid alts only for our implementation
  - Bear regime still loses money (-4.2%, Sharpe -0.31) — the strategy reduces but does not eliminate bear exposure
  - 36-month OOS window; includes 2022 bear and 2024 bull but not 2025 data
  - From full paper: paper team is "Talyxion Research, Hanoi, Vietnam" — no institutional pedigree. Bootstrap significance is solid methodology but independent replication not yet available
- **Complementarity:** HIGH — 6h systematic trend-following across 150+ pairs vs LiqCascade's event-driven 5m cascade detection and OracleSurfer's 1h ML regime classification. Different signal, timeframe, market conditions. All three can run concurrently.
- **MVP approach (revised):** Phase 0 — implement signal + ATR trailing stops on fixed whitelist of 15–20 liquid pairs (top-15 by market cap for longs + 5–8 liquid alts for shorts), fixed parameters, 70/30 slot split. Expected baseline Sharpe ~1.34 with fixed params. Run fee-inclusive backtest 2022–2024 with regime splits. Phase 1 — add monthly parameter optimization if Phase 0 clears PF > 1.0.
- **Supporting papers analyzed (2026-04-07):**

  **Karassavidis et al. (SSRN 5821842)** — "Quantitative evaluation of volatility-adaptive trend-following models in cryptocurrency markets"
  - Architecture: SMA(10/38) crossover + RSI filter (RSI must touch ≤44 within 5 days prior) + ATR trailing stop on H8 bars. BTC+ETH only, joint cross-asset objective. ~22 trades/year.
  - **Fatal caveat: ALL results are in-sample (2020–2025). No walk-forward validation.** Reported SR 1.67, CAGR 22%, MaxDD 11% are upper bounds, not production expectations.
  - 2020-2025 window includes the largest crypto bull run in history — favorable regime selection.
  - **Key M contribution:** Independently validates ATR trailing stop as highest-value exit component (+0.73 SR in Bui ablation study; Karassavidis ablation confirms similar). EMA slope exit explicitly tested and discarded — do not implement.
  - **ATR trail trigger (8.57 ATR):** Suspiciously precise — treat as in-sample artifact. M MVP uses always-on trailing (no profit-trigger threshold).
  - **Not a standalone candidate:** ~22 trades/year fails our frequency objective. In-sample-only results fail Evaluation Filter criterion 4. SMA+RSI entry architecture is a potential Phase 1 signal enhancement for M, not a separate build.

  **Huang, Sangiorgi & Urquhart (SSRN 4825389, 2024)** — "Cryptocurrency Volume-Weighted Time Series Momentum"
  - Volume-weighted WML portfolio outperforms capital-weighted TSMOM. Optimal lookback: 3–7 days (aligns with M's 6-day default). Effect attenuated post-2018 — genuine concern for current deployment.
  - Transaction costs material at 20 bps (our 10 bps is less severe; still relevant).
  - Portfolio-level evidence only — no single-pair validation.
  - **Not a standalone candidate:** Structurally similar to Candidate G (cross-sectional momentum, PARKED). Post-2018 attenuation means standalone candidacy would require fresh OOS validation we don't have. Better as a Phase 1 signal enhancement: weight ROC signal by rolling volume ratio before comparing to θ_entry.

- **Evaluation filter score:** Scored 2026-04-07 — see below

**CANDIDATE M — EVALUATION FILTER:**

| # | Criterion | Assessment | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Standard OHLCV at 6h (available via Binance/CCXT). Daily market cap for asset filtering (CoinGecko free API or hardcoded top-15 list). No special data feed required. | **PASS** |
| 2 | **Compute fit** | Rate-of-change signal is arithmetic. ATR is TA-Lib standard. Monthly grid search optimization is CPU-only, runs in minutes on 150 pairs. No GPU, no ML training overhead. | **PASS** |
| 3 | **Freqtrade compatibility** | 6h timeframe: supported. ATR trailing stops: native `custom_stoploss()`. Multi-pair: supported. Monthly Sharpe-based selection and 70/30 portfolio allocation require custom logic but have clear MVP simplifications (fixed whitelist + max_open_trades split). Not a blocker — conditional pass. | **CONDITIONAL PASS** |
| 4 | **Out-of-sample evidence** | 36-month walk-forward (2022-2024) including full bear-recovery cycle. Tested vs TSMOM benchmarks with p < 0.001 statistical significance. Rate-of-change momentum has decades of out-of-sample evidence across equities, futures, and FX — crypto is the most recent extension. Multiple independent papers confirm TSMOM works in crypto (Beluška & Vojtko 2024, Huang et al. 2024, CTBench 2025). | **PASS** |
| 5 | **Clear mechanism** | Serial return autocorrelation (trend persistence) is one of the most documented anomalies in finance — 40+ years of evidence across asset classes. In crypto, narrative-driven capital flows, leverage liquidation cascades, and retail-dominated markets create stronger serial correlation than traditional markets. The three enhancements (ATR stops, Sharpe selection, asymmetric allocation) are mechanistically grounded, not curve-fitted add-ons. | **PASS** |
| 6 | **Complementarity** | HIGH. Different signal (momentum vs cascade vs ML regime), timeframe (6h vs 5m vs 1h), and market conditions (trending vs volatile vs ML-classified). No signal overlap with LiqCascade or OracleSurfer. | **PASS** |
| 7 | **Implementation scope** | Phase 0 MVP feasible in 3–4 days: download 6h OHLCV for 15–20 pairs, implement rate-of-change signal + ATR trailing stop, run fee-inclusive backtest with regime splits. No model training, no sidecar for MVP. Phase 1 (rolling Sharpe selection) adds 2–3 more days. | **PASS** |

**Filter score: 6/7 (1 conditional pass) → Overall: PASS**

**Co-investigator assessment:** This is the cleanest stack-to-paper fit we've seen since LiqCascade. The signal is a single arithmetic formula. The exit mechanism is already proven in our stack. The multi-pair architecture is native Freqtrade. The applied history criterion — which the user specifically requested for Sweep #5 — is as strong as it gets: rate-of-change momentum has been deployed in live funds for decades. The novel element (portfolio construction layer) is an enhancement, not a prerequisite — the MVP can skip it and still test the core edge. The main risk is the 36-month test window and the potential that the bear-market protection (which drives the Sharpe) depends critically on the 70/30 allocation being implemented correctly. But this is diagnosable in Phase 0.

#### CANDIDATE L: Enhanced Cointegration Pairs Trading with Adaptive Trailing Stop + Volatility Filter
- **Status:** CANDIDATE — surfaced in Sweep #4; full-paper analysis completed 2026-04-07; **priority revised downward — see co-investigator note below**
- **Source:** Palazzi (Journal of Futures Markets, Aug 2025, peer-reviewed) — "Trading Games: Beating Passive Strategies in the Bullish Crypto Market." Tadi & Witzany (Financial Innovation, 2025) — copula-based pairs on Binance Futures. IEEE Xplore (2020) — "Pairs Trading in Cryptocurrency Markets" (5-min frequency finding).
- **Core idea:** Cointegrated pairs trading on 10 major cryptos, enhanced with: (1) dynamic trailing stop-loss (2.5%) adapting to spread's rolling volatility, (2) volatility filter (entry blocked when vol > 1.5× avg), (3) systematic grid-search optimization of lookback period (50–350 days), (4) walk-forward validation. Z-score entry threshold ±0.7 (vs standard ±2.0 — very aggressive, many signals at daily frequency).

**Full-paper performance — Palazzi 2025 (daily data, Jan 2019–May 2024, LTC/DOGE best pair):**

| Strategy | Ann. Return | Sharpe | Calmar | MDD |
|---|---|---|---|---|
| Simple pairs (EGER) | 18% | 0.54 | — | — |
| BTC Buy-and-Hold | 99% | 1.37 | — | — |
| **Optimized (OOS, best pair)** | **71%** | **2.12** | **4.95** | **14%** |

**Regime breakdown (OOS, LTC/DOGE):**

| Regime | Ann. Return | Sharpe | MDD |
|---|---|---|---|
| Bull (full OOS) | ~65% | 1.84 | ~14% |
| Bear (full OOS) | ~80% | 2.24 | -8.55% |

**Walk-forward stability (23 rolling windows, OOS):**
- Sharpe range: -2.10 to +7.68 | Mean: 0.89 | Std Dev: 2.54 | Positive windows: ~60%

**Lookback sensitivity (key operational risk):**
- 50–100 day: best OOS returns; 90-day best OOS Sharpe
- 350-day: best drawdown control (in-sample only; shows overfitting in OOS)
- 300–360 day lookbacks: significant overfitting — long lookbacks unreliable
- Minimal degradation regime: 30–60 day lookbacks (stable but lower return)

- **Critical findings from full-paper analysis (2026-04-07):**
  - **Daily data only** — Palazzi uses CoinMarketCap daily prices. NOT intraday, NOT Binance futures. The 5-min frequency result (11.61%/month) came from the IEEE Xplore (2020) paper — a separate, older study. The two claims cannot be combined.
  - **Single best pair** — LTC/DOGE was selected as best-performing from 37 cointegrated pairs. **Only 35% of those 37 pairs showed positive OOS returns.** The headline Sharpe 2.12 is the top survivor, not the portfolio average.
  - **Walk-forward highly variable** — Std Dev 2.54 on Sharpe across windows. A strategy that is negative in 40% of rolling periods is operationally unreliable.
  - **Extreme lookback sensitivity** — optimum shifts dramatically between IS and OOS. Grid search on IS to select lookback likely overfits. No adaptive lookback mechanism described.
  - **Beta to BTC: -0.13** — low market exposure is real; diversification benefit confirmed.
  - **Paper cites ~50% Sharpe decay post-publication** (Falck & Rej 2022). The peer-reviewed Sharpe 2.12 should be discounted accordingly.
  - **Dual-leg coordination** — paper does not address simultaneous long/short execution in a real trading system. Implementation complexity on Freqtrade is unresolved (same blocker as Candidate F).

- **Why it's still interesting:** Dual-leg architecture addresses CointPairs F single-leg failure. Bear-regime Sharpe (2.24) is genuinely attractive. Beta -0.13 offers real diversification. Phase 0 infrastructure (`cointpairs_phase0_validation.py`) is directly reusable. The Tadi & Witzany copula paper on Binance Futures is independent corroborating evidence.

- **Potential concerns (updated):** 35% OOS success rate across pairs = strong selection bias. Daily frequency mismatches our operational stack (hourly/sub-hourly execution). Dual-leg Freqtrade architecture unresolved. Walk-forward Sharpe Std Dev 2.54 is too high for operational confidence. Lookback sensitivity requires adaptive mechanism not described in paper. 5-min frequency claim is from a different (2020) paper — cannot assume Palazzi's strategy works at intraday.

- **Evaluation filter score (formal, 2026-04-07):**
  - ✅ Real exchange data — Binance futures in Tadi; CoinMarketCap daily in Palazzi (daily mismatch noted)
  - ✅ OOS validation — yes, walk-forward OOS in Palazzi
  - ✅ Transaction costs — yes, included (daily rebalancing)
  - ✅ Bear/Bull robustness — yes (bear Sharpe 2.24 > bull; confirmed)
  - ✅ Existing infrastructure reuse — `cointpairs_phase0_validation.py` reusable
  - ⚠️ Freqtrade compatibility — dual-leg coordination unresolved (same as F) — **CONDITIONAL**
  - ❌ Frequency match — paper is daily; we need intraday. 5-min claim is separate paper; not validated in Palazzi's framework
  - **Score: 5/7 with one conditional** (downgraded from preliminary 6/7 estimate — frequency mismatch is decisive)

- **Co-investigator note (2026-04-07):** The full paper materially weakens the case for L. The headline Sharpe 2.12 is the best of 37 pairs; portfolio-level expected Sharpe at daily frequency is closer to 0.89 (walk-forward mean). The frequency gap (daily → intraday) is not bridged by Palazzi — it requires a separate body of work. With M offering a cleaner implementation path and L carrying unresolved architecture and selection-bias problems, **L should remain #2 but not be started until M's Phase 0 is complete.** If M passes Phase 0, reassess whether L's dual-leg complexity is worth pursuing. If M fails, L becomes the primary candidate — but the frequency validation step must be done first (backtest at 1h/4h before committing to implementation).

### 4.4 Current Priority Ranking (as of 2026-04-07)

1. **Candidate M (AdaptiveTrend)** — **Top build priority** as of Sweep #5 (2026-04-07). 6/7 evaluation filter. Cleanest stack-to-paper fit of any candidate to date. Pure OHLCV, ATR trailing stops (already in our stack), Freqtrade-native 6h timeframe, multi-pair. Applied history is decades of live momentum deployment. MVP skips portfolio construction complexity — signal + stops is a 3–4 day Phase 0. **Evaluate before committing to L** — simpler architecture, lower translation risk.

2. **Candidate L (Enhanced CointPairs)** — Remains #2, but **priority revised downward after full-paper analysis (2026-04-07).** Palazzi paper is daily-only; headline Sharpe 2.12 is best-of-37 pairs (only 35% OOS success across pairs); walk-forward mean Sharpe 0.89, Std Dev 2.54. Frequency gap (daily → intraday) unresolved. Dual-leg Freqtrade architecture unresolved. Formal score: 5/7 + 1 conditional. **Do not start until M Phase 0 is complete.** If pursuing: frequency backtest (1h/4h) required before any implementation. Dev plan: `EnhancedCointPairs_Dev_Plan.md`.

3. **Candidate K (Multi-Timeframe Trend)** — Filter/enhancement for M, L, LiqCascade, or future trend work — not standalone.

4. **Candidate G (Cross-Sectional Momentum)** — **PARKED.** Reopen only per G's parking policy.

5. **Candidate J (Ensemble Donchian Trend-Following)** — **PARKED.** Phase 0 NO-GO (2026-04-06).

6. **Candidate I (Signature-Enhanced Momentum)** — RESERVED. Prerequisites unchanged.

7. **Candidates B (Funding Rate Arb), C (Vol Commonality), D (CNN Preprocessing)** — Parked. Unchanged.

*This ranking reflects the state of knowledge as of the date above. Update after any new sweep, evaluation, or project outcome.*

**Queue history:** E archived (2026-03-23, backtest fail). G parked (2026-03-29, empirically weak). J promoted to #1 (2026-03-31, Sweep #4). J parked (2026-04-06, Phase 0 NO-GO). L elevated to #1. **M promoted to #1 (2026-04-07, Sweep #5) — L drops to #2.**

---

## 5. Sourcing Configuration

### 5.1 Primary Sources (Claude checks these during every sweep)

| Source | Type | Access | Focus |
|---|---|---|---|
| **SSRN** | Academic preprints | Free, searchable, most papers full-text | Novel quantitative strategies, financial ML |
| **arXiv (q-fin)** | Academic preprints | Free, full-text | Cutting-edge ML/DL applied to markets |
| **Quantpedia blog** | Strategy database | Free tier (~70 strategies). Premium ($599/yr) unlocks 900+ strategies with out-of-sample backtests and Python code. **See 5.5 for paid access recommendation.** | Academic strategies translated to plain-language trading rules |
| **Oxford-Man Institute** | Academic research | Newsletter + public papers (some link to paywalled journals) | ML for quant finance, market microstructure, regime detection |

### 5.2 Applied / Practitioner Sources

| Source | Type | Access | Focus |
|---|---|---|---|
| **QuantStart** | Blog + courses | Free blog, paid courses | Practical strategy implementation, Python, backtesting infrastructure |
| **Robot Wealth** | Blog + community | Free blog | Practical quant trading for retail, fee-aware analysis, crypto strategies |
| **The Quant's Playbook** (Substack) | Newsletter | Free + paid tiers | Accessible breakdowns of quant strategies, code examples |
| **r/algotrading, r/quant** (Reddit) | Community forums | Free | Practitioner discussion, implementation tips, reality checks on academic claims |
| **QuantConnect community** | Forums + shared strategies | Free | Implemented strategies with backtests, QuantConnect/Lean framework |
| **Freqtrade Discord / GitHub** | Community | Free | Freqtrade-specific strategies, FreqAI examples |
| **QuantInsti blog / Quantra** | Blog + courses | Free blog, paid courses | End-to-end strategy walkthroughs, Python implementations |

### 5.3 Secondary Academic Sources

| Source | Type | Access | Focus |
|---|---|---|---|
| **IEEE Xplore** | Peer-reviewed journals | Abstracts free, papers often paywalled | Signal processing, neural architectures for time series |
| **Journal of Financial Data Science** | Peer-reviewed | Some open access | ML applications in finance |
| **Quantocracy** | Aggregator | Free | Curates blog posts from dozens of quant blogs — good for discovering new sources |

### 5.4 Reference Literature

Key books that inform our approach. Claude cannot access these directly but should reference their concepts when relevant. The developer has or can acquire electronic copies.

| Book | Author | Why It Matters |
|---|---|---|
| **Advances in Financial Machine Learning** | Marcos López de Prado | Foundational. Fractional differentiation (now in our Techniques Library), meta-labeling, triple barrier method, combinatorial purged cross-validation. The methodological standard for ML in trading. |
| **Machine Learning for Algorithmic Trading** (2nd ed.) | Stefan Jansen | Practical companion to de Prado. Feature engineering, model selection, NLP for trading, full Python implementations. 820 pages of applied ML for markets. |
| **Algorithmic Trading: Winning Strategies and Their Rationale** | Ernest P. Chan | Mean reversion, momentum, Kalman filters, regime changes. Practical and honest about what works and what doesn't. |
| **Python for Finance** (2nd ed.) | Yves Hilpisch | Python-specific reference for financial data handling, analysis, and modeling. Useful as a coding reference. |
| **Trading and Exchanges: Market Microstructure for Practitioners** | Larry Harris | Deep understanding of how markets actually work — order types, dealers, market makers. Relevant background for any microstructure-based strategy. |

### 5.5 Paid Access Recommendations

**Quantpedia Premium ($599/yr)** — The single highest-value paid source for our workflow. Premium unlocks 900+ strategy ideas with descriptions, performance characteristics, links to source academic papers, and 800+ out-of-sample backtests with Python code. New strategies are added bi-weekly, and around 5–10 new backtests are added bi-weekly as well. This is essentially a pre-filtered, pre-summarized version of what we do manually during sourcing sweeps — someone has already read thousands of papers and extracted the implementable ones. At $599/yr, if it surfaces even one viable candidate we wouldn't have found otherwise, it pays for itself many times over. **Recommendation: consider subscribing before Sweep #3 or when beginning implementation of Candidate F, whichever comes first.**

**Reference books (~$50–150 total for electronic copies)** — De Prado and Jansen specifically. These aren't sourcing tools but they inform *how* we build. De Prado's methodological framework (purged CV, fractional differentiation, meta-labeling) is already influencing our work indirectly. Having the actual text would let Claude reference specific techniques when relevant during Cursor sessions.

**No other paid sources recommended at this time.** SSRN, arXiv, and the practitioner blogs provide sufficient coverage for sweeps. IEEE Xplore paywalls are annoying but the abstracts usually contain enough to decide if a paper is worth pursuing, and the underlying papers often appear on arXiv anyway.

### 5.6 Search Terms for Sourcing Sweeps

Rotate and combine these across sources:

**Core:** `algorithmic trading strategy`, `crypto trading ML`, `systematic trading`

**Architecture-specific:** `state space model trading`, `temporal fusion transformer finance`, `reinforcement learning trading`, `hawkes process order flow`, `regime detection trading`, `liquidation cascade crypto`, `order flow imbalance`, `path signatures trading`, `rough path finance`

**Technique-specific:** `mean reversion crypto`, `momentum strategy ML`, `volatility forecasting`, `funding rate strategy`, `market microstructure alpha`, `conformal prediction trading`, `fractional differentiation trading`

**Meta/methodology:** `backtesting pitfalls`, `walk-forward validation trading`, `overfitting trading strategies`, `synthetic data augmentation finance`, `transaction cost analysis crypto`

---

## 6. Evaluation Filter

Before committing to implement any candidate approach, score it on these criteria. Minimum passing score: 5/7 criteria met.

| # | Criterion | Question | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Can I get the required data for free or very cheaply via Binance API, CCXT, or public sources? | |
| 2 | **Compute fit** | Can this run inference on a standard VPS (no GPU)? If training needed, can it be done on a local machine in < 24 hours? | |
| 3 | **Freqtrade compatibility** | Can this be implemented as a Freqtrade strategy (with or without FreqAI), or does it require a fundamentally different execution framework? | |
| 4 | **Out-of-sample evidence** | Has anyone (paper authors, Quantpedia, community) shown out-of-sample or walk-forward results — not just in-sample backtests? | |
| 5 | **Clear mechanism** | Is there a plausible reason *why* this edge should exist (structural, behavioral, informational)? Or is it pure curve-fitting? | |
| 6 | **Complementarity** | Does this address a different market condition or alpha source than what's already in the Active/Paused registry? | |
| 7 | **Implementation scope** | Can a working backtest be produced in ≤ 1 week of Cursor + Claude development time? | |

### 6.1 Red Flags (auto-reject or investigate further)

- Paper shows only in-sample results with no holdout period
- Strategy requires tick-level or Level 2 data not available through Binance standard API
- Core alpha depends on latency advantage (sub-second execution)
- Backtested only on equities with no evidence of applicability to crypto
- "Accuracy" metrics reported without any connection to P&L (see RAME lesson)
- Requires continuous GPU inference

---

## 7. Techniques Library

*Techniques, tools, and methods that are not standalone strategies but can strengthen candidates during evaluation, development, or live operation. Claude should scan this section when evaluating new candidates ("would any of these techniques make this candidate stronger?") and when diagnosing deficiencies in active strategies ("could one of these techniques fix this problem?").*

*Status key:* `AVAILABLE` = ready to use, libraries identified · `RESEARCH` = promising but needs investigation before use · `PROVEN` = already used successfully in a project

### 7.1 Uncertainty Quantification / Risk Management

#### Conformal Prediction
- **Status:** AVAILABLE
- **What it does:** Wraps any point-prediction model to produce prediction *intervals* with a mathematical coverage guarantee (e.g., "95% of future observations will fall within this range"). Unlike Bayesian methods, makes no distributional assumptions.
- **Libraries:** `MAPIE` (scikit-learn compatible), `nonconformist`
- **How we'd use it:** Layer on top of any ML-based signal (e.g., CatBoost, path signatures). Only take a trade when the prediction interval is tight and entirely on one side of the entry price. This converts a noisy point estimate into a "statistically bounded" entry filter. Could significantly reduce false entries and drawdowns.
- **When to apply:** During Phase 2+ of any ML-based candidate — after the base model is validated but before live deployment. Adds a confidence filter without changing the underlying signal.
- **Relevant candidates:** Any future ML-based strategy; potentially a **future** signature-based candidate if revisited after a validated design (Candidate E MVP archived 2026-03-23).

### 7.2 Feature Engineering / Preprocessing

#### Fractional Differentiation
- **Status:** AVAILABLE
- **What it does:** Makes time series stationary while preserving long-range memory. Standard differencing (percent change) removes all price-level information; fractional differentiation removes just enough trend to achieve stationarity while retaining predictive memory of historical levels.
- **Libraries:** `fracdiff` (Python, pip-installable)
- **Source:** Marcos López de Prado, "Advances in Financial Machine Learning" (2018), Ch. 5. Resurgence in 2025–2026 IEEE papers on memory-augmented networks.
- **How we'd use it:** Apply as a standard preprocessing step to any ML model that takes price data as input. Replace simple returns or percent changes with fractionally differenced series. Gives the model access to both stationarity (required for ML) and price-level memory (required for detecting support/resistance, trend structure, etc.).
- **When to apply:** During feature engineering for any ML-based candidate. Low effort — one function call per feature column.
- **Relevant candidates:** Any future FreqAI model; a **future** signature-based pipeline if rebuilt (Candidate E MVP archived 2026-03-23).

#### Stationarity-Preserving Preprocessing (CNN-style)
- **Status:** RESEARCH
- **What it does:** A novel method from SSRN (Asareh Nejad et al., 2024) that makes indicator + candlestick data stationary while preserving inter-feature relationships. Different approach from fractional differentiation — transforms the entire feature matrix jointly rather than column-by-column.
- **Source:** Candidate D in this log (Section 4.3). Paper achieved 53.9% directional accuracy at 15m on crypto.
- **How we'd use it:** Alternative to fractional differentiation for multi-feature preprocessing. May be better when features have cross-correlations that should be preserved.
- **When to apply:** If fractional differentiation proves insufficient for a multi-feature model. Lower priority than fractional differentiation (less proven, less widely adopted).

### 7.3 Signal Quality / Entry Filtering

#### Fee Economics Threshold Sweep
- **Status:** PROVEN (used in LOB Microstructure, 2026-03-20)
- **What it does:** Before building execution infrastructure for any signal, sweep across signal-strength thresholds and time horizons to compute expected P&L at our actual fee tier (Binance retail: 5 bps/side = 10 bps round-trip). Identifies whether any profitable operating point exists.
- **How we'd use it:** Run as a mandatory pre-implementation check for any candidate that relies on high-frequency signals. Takes ~30 minutes with a held-out test set. Prevents building infrastructure for signals that can't overcome fee friction.
- **When to apply:** Immediately after Phase 1 (signal validation) for any candidate, before Phase 2 (Freqtrade integration). See Lesson #7 in Section 9.
- **Source:** LOB Microstructure project (ARCHIVED). The sweep saved weeks of potential infrastructure work.

#### LOB Order Flow Imbalance (OFI) as Confirmation Filter
- **Status:** RESEARCH
- **What it does:** Uses the validated OFI signal from the LOB Microstructure project (real signal, IC=0.135 at 3s) as a *confirmation filter* for entries generated by another strategy — not as a standalone trade signal (fee-incompatible for standalone use).
- **How we'd use it:** When a primary strategy (e.g., LiqCascade) generates an entry signal, check whether the LOB OFI at that moment agrees with the direction. If OFI is neutral or opposing, skip the entry. No standalone execution → no fee problem.
- **When to apply:** If LiqCascade Phase 3 data shows a high false-positive entry rate. Not prioritized until that need is demonstrated.
- **Source:** LOB Microstructure project (ARCHIVED). See Section 4.1 "Potential future salvage."

### 7.4 Macro / Context Filters

#### Funding Rate Extreme as Contrarian Entry Filter
- **Status:** RESEARCH (surfaced in Sweep #5, 2026-04-07)
- **What it does:** Uses extreme funding rate readings on perpetual futures as a directional bias filter. Extreme positive funding (>0.1%/8h sustained for 3+ periods) = crowded longs = elevated unwind risk → favour short entries or block long entries. Extreme negative funding = crowded shorts → favour long entries. Funding rate is paid every 8 hours on Binance; the rate reflects the long/short imbalance in open interest.
- **Evidence:** Multiple independent sources (2022–2025): Inan (SSRN 5576424) confirms OOS predictability via DAR models. Coinbase Institutional / GSR research documents statistically significant negative returns following sustained high funding (>0.05%/8h for 3+ consecutive periods). Robot Wealth practitioner tests confirm it works as an entry gate on altcoins; weaker on BTC/ETH alone. Effect is non-linear — only meaningful in top/bottom decile readings.
- **Critical nuance — Funding + OI is the best-documented configuration.** Funding rate alone is a moderate signal; funding rate z-score + simultaneous OI elevation is the strongest predictive combination in the literature (robot wealth, multiple SSRN papers 2023–2025). This directly validates our LiqCascade Phase 3.5 OI filter — adding a funding rate gate on top of OI is the evidence-based next step.
- **Signal decay warning:** The cross-sectional funding sort (long lowest-funding assets, short highest-funding) is the most crowded version of this trade and shows degrading live Sharpe from 2024 onward (Quantpedia documented). The time-series contrarian signal (single-asset, extreme funding → block longs / favour shorts) is less crowded and more robust.
- **Asset scope:** Works materially better on altcoins than BTC/ETH. BTC/ETH funding can stay elevated for weeks during strong trends without reverting. Apply threshold conservatively on BTC (e.g., 90th+ percentile rolling 30d rather than fixed 0.1%).
- **Data sources:** Binance REST API (`GET /fapi/v1/fundingRate`) — free, no special tier. Poll every 8h by sidecar. OI from same endpoint (`GET /fapi/v1/openInterest`).
- **How we'd use it:** Gate on top of existing entry conditions. LiqCascade: when a cascade signal fires AND funding is extreme-positive, short edge is amplified (crowded longs being squeezed + cascade = reinforcing). Block long cascade entries when funding is extreme-positive. OracleSurfer: block BULL entries when funding is at 90th+ percentile. AdaptiveTrend: weight short allocation higher when funding is elevated cross-sectionally.
- **When to apply:** LiqCascade Phase 4 is the natural first application — add as a secondary gate after OI threshold is validated at the April 20 checkpoint.
- **Relevant candidates:** LiqCascade (highest priority — Funding + OI joint gate), OracleSurfer (short entry filter), Candidate M/AdaptiveTrend (entry bias).

#### On-Chain Whale Flow as Macro Filter
- **Status:** RESEARCH (reclassified from Candidate H in Sweep #3)
- **What it does:** Uses exchange inflow/outflow data, whale wallet accumulation/distribution patterns (via Glassnode Accumulation Trend Score or similar), and stablecoin supply changes as a directional bias filter. Not a trade signal — a context gate similar to the CRISIS gate but using on-chain data.
- **Data sources:** Whale Alert API (free), CryptoQuant (free tier), Glassnode (free tier), Santiment. Most provide daily granularity; some hourly.
- **How we'd use it:** Only take long entries (in LiqCascade, momentum, or any directional strategy) when whale accumulation is positive. Reduce exposure or go flat when whale distribution is detected. Similar in concept to our EMA200 macro trend filter but using on-chain fundamentals instead of price.
- **When to apply:** After a directional strategy is profitable but suffering from entries during macro distribution phases. Lower priority — requires sidecar for API ingestion and the signal-to-noise ratio for automated use is unproven.
- **Source:** Sweep #3 practitioner research. Tools: Nansen, Arkham, Glassnode, CryptoQuant, Dune Analytics.

### 7.5 Model Optimization / Meta-Techniques

#### Genetic Algorithm for Strategy Parameter Optimization (CGA-Agent)
- **Status:** RESEARCH
- **What it does:** Uses multi-agent genetic algorithms with real-time market microstructure feedback to optimize trading strategy parameters. Rolling 30-day reoptimization windows.
- **Source:** arXiv 2510.07943 (2025). Reviewed but not promoted in Sweep #1.
- **How we'd use it:** Alternative to Freqtrade's built-in Hyperopt for parameter optimization. Could be applied to any strategy's parameters (thresholds, stops, timeouts). The rolling reoptimization is interesting — addresses regime change better than static Hyperopt.
- **When to apply:** After a strategy is validated but underperforming expectations due to parameter staleness. Lower priority than getting the base strategy right.

---

## 8. Sourcing Sweep Log

*Each sweep gets an entry here. This prevents re-searching the same ground.*

### Sweep #1
- **Date:** 2026-03-20
- **Sources checked:** SSRN, arXiv (q-fin.TR, q-fin.ST, q-fin.CP — Dec 2025 through Feb 2026), Quantpedia blog (Dec 2025 – Feb 2026), Oxford-Man Institute publications, practitioner sources
- **Search terms used:** `crypto trading strategy novel 2025 2026`, `crypto market microstructure scalping`, `funding rate arbitrage perpetual futures automated`, `Quantpedia crypto trading strategy new`, `arXiv quantitative finance crypto`
- **Papers/sources reviewed:** ~25 papers and articles scanned, ~8 read in detail
- **Candidates surfaced:** 4 (A through D, see Section 4.3)
- **Top recommendation from Claude:** Candidate A (Order Book Microstructure) — *Note: subsequently built, tested, and archived (see Section 4.1). Signal was real but fee structure incompatible at retail rates.*
- **Notable papers reviewed but not promoted:**
  - *Catching Crypto Trends* (Zarattini et al., SSRN 2025) — Donchian channel ensemble on crypto. Solid but conventional trend-following; unlikely to significantly outperform simpler momentum approaches we could build ourselves. ***Re-evaluated in Sweep #4 after G's parking revealed ensemble + rotational portfolio construction is the critical differentiator. Promoted to Candidate J.*** *(2026-04-06: **J PARKED** — Phase 0 NO-GO on our Freqtrade implementation; paper remains reference-only for this project.)*
  - *Risk-Aware Deep RL for Crypto Trading* (Bandarupalli, SSRN 2025) — PPO-based RL. Underperformed buy-and-hold (Sharpe 1.23 vs 1.46). RL for trading remains promising in theory but this specific paper is a cautionary example.
  - *CGA-Agent: Genetic Algorithm for Crypto Trading* (arXiv 2025) — Multi-agent genetic algo for parameter optimization. Interesting meta-approach to tuning, but the underlying strategies being optimized are standard TA. Could revisit as an optimization technique rather than a strategy.
  - *BTC Seasonality / 2-hour hold strategy* (Quantpedia/SSRN) — Holding BTC only 2 hours per day based on NYSE open/close timing. Intriguing anomaly but very low frequency, fragile edge, and unclear if it persists post-ETF era.

### Sweep #2
- **Date:** 2026-03-22
- **Focus:** Two targeted angles: (1) crypto-specific validation of path signatures (Candidate E), (2) OHLCV-native strategies from practitioner sources that don't require sidecars.
- **Sources checked:** arXiv (path signatures + trading, lead-lag + crypto), GitHub (Rahimi lead-lag-portfolios), QuantStart (rough path series), Robot Wealth (strategy index), Amberdata (crypto pairs trading series), Frontiers in Applied Mathematics, r/algotrading
- **Search terms used:** `path signatures crypto trading lead-lag`, `"path signature" "lead-lag" trading cryptocurrency financial`, `crypto pairs trading cointegration mean reversion profitable 2025`, `Robot Wealth crypto strategy deployed`
- **Papers/sources reviewed:** ~20 sources scanned, ~10 read in detail
- **Candidates updated/surfaced:**
  - Candidate E (Path Signatures): **Validated for crypto.** Found direct crypto implementation (Rahimi GitHub), signature trading framework (Futter et al.), segmented signatures for pair trading (arXiv May 2025), and QuantStart tutorial series. Ready for formal evaluation.
  - Candidate F (Cointegration Pairs Trading): **NEW.** Comprehensive crypto-specific evidence from Amberdata (5-part blog series with backtested results), Frontiers paper (Jan 2026, DNN/LSTM spread forecasting), and multiple practitioner implementations. Well-established strategy class with clear enhancement path via Techniques Library.
- **Top recommendation from Claude:** Both E and F are strong and complementary — E is more novel (path-dependent features, lead-lag), F is more established (statistical arbitrage, mean reversion). Both work on OHLCV data with no sidecar required. F has a clearer path to profitability with known enhancement techniques, but E has higher upside if the lead-lag signal is strong at our timeframes. Recommend evaluating both through the filter and letting the scores decide.
- **Notable sources reviewed but not promoted:**
  - *Robot Wealth strategy index* — Rich practitioner resource. Their "YOLO" crypto momentum strategy and carry research on Hyperliquid are interesting but tightly coupled to their own infrastructure and paid membership. Noted as a source to revisit if we subscribe. Their emphasis on "what's your edge?" as the first question resonates with our Lessons (#3, #7, #8).
  - *DeltaLag* (ICAIF 2025) — Adaptive learned lead-lag using cross-attention. Outperforms static signature-based approaches but requires deep learning and is applied to equities, not crypto. Filed as a potential future evolution of Candidate E if the base approach works.
  - *Hawkes-based crypto forecasting via LOB data* (arXiv 2023) — Hawkes process on crypto LOB order timing. Promising but requires LOB data (same constraint that limited Candidate A). Filed for future reference.

### Sweep #3
- **Date:** 2026-03-22
- **Focus:** (1) High-frequency OHLCV-native approaches (CointPairs died at 0.05 trades/day). (2) Strategies where per-trade moves > 10 bps (LOB died at fee floor). (3) Complementary to LiqCascade. (4) Additional evidence on Candidate E feasibility.
- **Sources checked:** arXiv (q-fin recent — cross-sectional momentum, volatility-adaptive trend following), SSRN (crypto momentum under realistic assumptions), ScienceDirect (high-frequency momentum, risk-managed momentum), practitioner sources (CoinAPI scalping analysis, Stoic.ai momentum guide, FXEmpire cross-sectional crypto momentum), on-chain analytics ecosystem (Nansen, Glassnode, Whale Alert, Arkham, Dune, Santiment)
- **Search terms used:** `crypto momentum scalping strategy high frequency OHLCV profitable 2025 2026 backtest`, `cross-sectional momentum crypto short-term profitable strategy`, `crypto volatility breakout strategy volume spike 5m 15m`, `on-chain data crypto trading strategy whale tracking automated`
- **Papers/sources reviewed:** ~30 sources scanned, ~12 read in detail
- **Candidates surfaced:** 2 new (G, H)
  - **Candidate G: Cross-Sectional Crypto Momentum** — Rank assets by recent returns, go long winners and short losers. Strong academic evidence specific to crypto: Drogen et al. (SSRN 2023) shows 30-day formation / 7-day holding consistently delivers excess returns vs BTC. Han et al. (SSRN 2023) performs comprehensive analysis under realistic assumptions (fees, liquidation risk) — time-series momentum is strong, cross-sectional is weaker but winner-concentrated. ScienceDirect (2025) introduces risk-managed momentum for crypto. High frequency achievable: hourly formation periods tested successfully. Works on OHLCV across 10–30 pairs simultaneously = many trades. Key concern: momentum crashes (documented in the literature), but risk-managed variants address this.
  - **Candidate H: On-Chain / Whale Flow Signals** — Use exchange inflow/outflow data, whale wallet tracking, and stablecoin supply changes as leading indicators for directional trades. Structural alpha: whale accumulation during fear = contrarian buy signal. Multiple free data sources (Whale Alert API, CryptoQuant, Glassnode free tier). Concern: data is typically daily frequency (too slow for our active-trading objective?), integration with Freqtrade requires a sidecar, and the signal-to-noise ratio for automated trading (vs discretionary analysis) is unproven. May be better as a filter/context layer than a standalone signal.
- **Top recommendation from Claude:** Candidate G (Cross-Sectional Momentum) is the strongest new find. It directly addresses our two biggest failure modes — it's inherently high-frequency (many pairs × short holding periods = many trades per day) and per-trade moves at hourly horizons are well above the fee floor. It's also the most "established approach that could be enhanced with techniques" — exactly what our broadened Objectives encourage. Recommend promoting to formal evaluation immediately. Candidate H is interesting but better suited as a technique/filter than a standalone strategy — add to Techniques Library rather than Candidates.
- **Candidate E additional context:** The cross-sectional momentum literature provides indirect support for path signatures — both approaches exploit the same underlying phenomenon (information diffusion across assets at different speeds). Path signatures capture the *shape* of this diffusion; cross-sectional momentum captures the *ranking*. They could potentially be combined: use signatures to detect *which* assets are leading, then apply momentum to the leaders/laggers ranking.
- **Notable sources reviewed but not promoted:**
  - *CryptoPulse* (arXiv Feb 2025) — Dual-prediction framework combining macro environment, technical indicators, and LLM-based news sentiment for next-day crypto price forecasting. Interesting architecture but daily frequency (too slow for our objective) and requires LLM inference for sentiment scoring (infrastructure complexity).
  - *CTBench* (arXiv Aug 2025) — Crypto time series generation benchmark. Tests cross-sectional momentum as one of its strategy benchmarks using XGBoost on Alpha101 factors. Useful as a methodology reference but not a strategy itself.
  - *Volatility-Adaptive Trend-Following in Crypto* (SSRN Nov 2025, Karassavidis et al.) — Abstract only accessible but the title is directly relevant. Filed for full review if it becomes available.
  - *Whale volatility forecasting from Twitter* (arXiv 2022) — Uses whale-alert Twitter data + CryptoQuant on-chain data with Synthesizer Transformer to forecast BTC volatility spikes. Interesting but requires Twitter/X API access and NLP pipeline. Filed as potential enhancement to LiqCascade (whale flows could predict cascade events).


### Sweep #4
- **Date:** 2026-03-31
- **Focus:** Established strategy classes with modern enhancements, biased toward high trade frequency (shorter timeframes or multi-pair execution). Motivated by G's parking (return-ranking was regime-unstable) and the need for approaches robust across market regimes.
- **Sources checked:** SSRN (crypto trend-following, pairs trading, mean reversion — 2024–2026), arXiv (q-fin recent, Hawkes processes, microstructure), Journal of Futures Markets (Palazzi 2025), ScienceDirect, Financial Innovation (Tadi & Witzany 2025), IEEE Xplore (crypto pairs at multiple frequencies), Quantpedia/Vojtko research group, QuantifiedStrategies, practitioner sources
- **Search terms used:** `crypto algorithmic trading strategy profitable 2025 2026 high frequency`, `SSRN crypto trading strategy multi-asset backtest`, `Donchian channel ensemble crypto trend following`, `grid trading crypto strategy automated`, `"mean reversion" OR "volatility breakout" crypto futures intraday`, `Hawkes process crypto trading order flow`, `cointegrated pairs trading crypto walk-forward adaptive`, `multi-timeframe trend strategy Bitcoin`
- **Papers/sources reviewed:** ~40 scanned, ~15 read in detail
- **Candidates surfaced:** 3 (J, K, L)
  - **Candidate J: Ensemble Donchian Trend-Following** — Zarattini et al. (SSRN 2025, Swiss Finance Institute). Donchian channel ensemble (9 lookbacks) on rotational top-20 crypto portfolio. Sharpe > 1.5, CAGR 30%, alpha 10.8–14% vs BTC. Survivorship-bias-free. Long-only. Vol-scaled position sizing. *Originally reviewed in Sweep #1 and dismissed as "conventional" — re-evaluated after G showed regime instability, which the ensemble addresses.*
  - **Candidate K: Multi-Timeframe Trend Confirmation** — Mesíček & Vojtko (Quantpedia/SSRN Nov 2025). Daily-hourly MACD confirmation + trailing stop on BTC. Improved stability and risk-adjusted returns. Recommended as filter/enhancement for J or LiqCascade, not standalone.
  - **Candidate L: Enhanced CointPairs** — Palazzi (J. Futures Markets, Aug 2025, peer-reviewed). Adaptive trailing stop + vol filter on cointegrated crypto pairs. Positive across bull and bear regimes. Addresses both F failure modes. IEEE Xplore data shows 5-min pairs trading returns 11.61%/month vs −0.07% daily. Second-priority behind J at sweep time; **J later PARKED (2026-04-06)** — see current §4.4.
- **Top recommendation from Claude (as of 2026-03-31):** Candidate J was promoted to formal evaluation and a dev plan (completed MVP + Phase 0 sweep). **Update 2026-04-06:** Phase 0 **NO-GO** — J **PARKED**; see Candidate J entry and §4.4. Historical recommendation preserved for audit trail.
- **Notable sources reviewed but not promoted:**
  - *Dynamic Grid Trading* (arXiv, Dec 2025) — Grid strategy with auto-reset on range break. Strong in ranging markets but fails in trends — opposite of crypto's character. Filed as potential ranging-regime technique only.
  - *Beluská & Vojtko BTC trend/mean-reversion* (SSRN Oct 2024) — Updated through Aug 2024, confirms BTC trends at maxima and reverts at minima. Supports J and K but not a new strategy. Context for signal validation.
  - *Hawkes process LOB forecasting* (arXiv 2023, multiple papers) — Theoretically elegant for modeling self-exciting order flow cascades. Requires LOB data (same constraint as Candidate A). Filed as potential future LiqCascade entry filter enhancement — the self-exciting property maps onto cascade detection.
  - *CryptoPulse* (arXiv Feb 2025) — Already rejected in Sweep #3. Daily frequency, LLM pipeline. No change.
  - *Probabilistic Volatility Forecasting* (arXiv Aug 2025) — Ensemble of HAR/GARCH/ML for conditional vol quantiles. Forecasting framework, not trading strategy. Filed as potential position-sizing technique, similar to Candidate C.
  - *Copula-based crypto pairs trading* (Tadi & Witzany, Financial Innovation 2025) — Supporting evidence for Candidate L. Tested on Binance USDT-margined futures specifically. Outperforms standard cointegration and copula approaches. Integrated into L's evidence base.

### Sweep #5
- **Date:** 2026-04-07
- **Focus:** Applied-history-first bias — strategies with practitioner deployment track records and classical foundations, enhanced with modern elements. Specifically avoiding approaches that fail the stack-translation test. Angles covered: VWAP mean reversion, Bollinger Band regime-switching, volatility breakout, funding rate as directional signal, ATR/momentum systems, multi-pair time-series momentum, single-asset mean reversion, RSI multi-pair.
- **Sources checked:** arXiv (q-fin, Feb 2025–Feb 2026 — emphasis on OHLCV-native strategies), SSRN (targeted abstract retrieval), Quantpedia blog, QuantifiedStrategies.com, Robot Wealth (practitioner practitioner sources)
- **Search terms used:** `VWAP mean reversion crypto futures strategy backtest profitable 2024 2025`, `funding rate signal directional crypto perpetual futures backtest 2024 2025`, `Bollinger Band squeeze volatility breakout crypto backtest 2024 2025`, `volatility regime switching trend mean reversion crypto systematic 2025`, `RSI oversold overbought multi-asset crypto systematic backtest 2025`, `crypto mean reversion single asset short-term 1h 4h SSRN`, `crypto breakout volatility contraction ML filter entry systematic 2025`, `time series momentum crypto short-term 6h systematic multi-pair 2025`
- **Papers/sources reviewed:** ~35 sources scanned, ~10 read in detail
- **Candidates surfaced:** 1 new (M)

**Candidate M: AdaptiveTrend** — Bui & Nguyen (arXiv 2602.11708, Feb 2026). Rate-of-change momentum on 6h OHLCV across 150+ crypto pairs, with three portfolio construction enhancements: ATR dynamic trailing stops, monthly rolling-Sharpe pair selection, 70/30 asymmetric long-short allocation. Sharpe 2.41, Calmar 3.18, max DD -12.7% over 2022-2024. Only -4.2% in 2022 bear. Dramatically outperforms classical TSMOM benchmarks (Sharpe 0.65). Pure OHLCV signal; market cap filter needs daily CoinGecko. MVP simplification: skip monthly Sharpe selection, use fixed pair whitelist, implement signal + ATR stops in 3–4 days. **6/7 evaluation filter — PASS. Promoted to #1 build priority.**

- **New technique added to §7.4:** Funding Rate Extreme as Contrarian Entry Filter (Inan, SSRN 5576424). DAR models confirm OOS predictability of funding rates on Binance/Bybit. Extreme positive funding = crowded longs = short bias amplifier. Applicable to LiqCascade, OracleSurfer, and AdaptiveTrend short entries.

- **Top recommendation from Claude:** Candidate M before Candidate L. The stack translation argument is decisive: M's signal is arithmetic on OHLCV with an ATR trailing stop — both already proven in our stack. L's dual-leg coordination is an unresolved architecture problem that has blocked us once before. Run M Phase 0 first (3–4 days), then decide whether L is worth the coordination complexity.

- **Notable papers reviewed but not promoted:**
  - *Bollinger Bands under Varying Market Regimes* (Arda, SSRN 5775962, Nov 2025) — BTC/USDT July 2017–March 2022 (1m granularity, aggregated to 8 TFs). Long-only, no stop-loss, 0.075% fee. **1h breakout is profitable across all four regimes:** Bear +14.89% (Sharpe 0.36), Accumulation +22.10% (Sharpe 0.24), Bull Run +34.29% (Sharpe 0.87), Distribution +13.10% (Sharpe 0.33). Max drawdowns contained (10–20%). Mean reversion at 1h: only positive in Accumulation (+8.58%) and Bull Run (+78.41%) — fails in Bear (-67%) and Distribution (-11%). **Key finding: 1h breakout (price closes above upper band, exit at mid-band) is regime-agnostic at this timeframe — no macro filter required for long entries.** Short breakout (below lower band) not tested. Test window ends March 2022 — misses 2022 bear and 2024-25 bull. The author explicitly suggests ML regime classifiers to dynamically toggle between modes as future work — which is structurally what OracleSurfer already does. **Potential candidate:** adding short breakout entries (below lower band) + EMA200 macro filter to protect bear exposure would give a fully bidirectional, Freqtrade-native strategy with near-zero special data requirements. Not promoted to full candidate in this sweep — short-side performance unknown. Flag for Phase 0 consideration if AdaptiveTrend (Candidate M) Phase 0 produces a NO-GO.
  - *Predictability of Funding Rates* (Inan, SSRN 5576424) — Filed as technique §7.4 (above).
  - *Volume-Weighted TSMOM* (Huang, Sangiorgi & Urquhart, SSRN 4825389, 2024) — Volume-weighting the momentum signal shows strong recent crypto evidence. Supporting evidence for M's signal quality; could be a Phase 1 enhancement for AdaptiveTrend (weight momentum signal by volume).
  - *Technical Analysis + ML on Bitcoin* (arXiv 2511.00665, Nov 2025) — LSTM achieves 65% cumulative return in < 1 year on BTC. Single asset, black-box architecture, not Freqtrade-native. Not promoted.
  - *Volatility-Adaptive Trend-Following* (Karassavidis et al., SSRN 5821842) — Full text inaccessible (403). Title suggests volatility scaling on crypto trend-following — closely related to M's ATR-adaptive stop mechanism. If accessible, likely provides supporting evidence for M.
  - *VWAP strategies* (QuantifiedStrategies/Zarattini SSRN 4631351) — VWAP mean reversion is well-tested on equities. Crypto application exists (arXiv 2502.13722 — deep learning for VWAP execution) but is focused on execution optimization, not alpha generation. No strong VWAP alpha evidence for crypto futures at the timeframes we target.
  - *RSI on Bitcoin* (QuantifiedStrategies) — Practitioner finding: RSI mean-reversion (buying oversold dips) does NOT work on Bitcoin. RSI works better as momentum confirmation (consistent with our existing OracleSurfer entry filter). Reinforces existing architecture choices.

---

## 9. Lessons & Principles

Hard-won insights that apply across all approaches. Add to this as projects conclude.

1. **ML accuracy ≠ trading edge.** A classifier can achieve 100% accuracy and produce zero profit if it's learning the labeling formula instead of future returns. Always test whether model output predicts forward P&L, not just label match. *(Source: RAME)*

2. **Entry quality > exit optimization.** Across 8 RAME backtest runs, changing exits shuffled where losses appeared but never changed the total. The real lever is being selective about which trades to take. *(Source: RAME)*

3. **Structural alpha > statistical alpha.** Liquidation cascades exist because of market mechanics (forced selling), not because of a statistical pattern that could be arbitraged away. Prefer approaches with a clear *why*. *(Source: RAME → LiqCascade pivot)*

4. **Short-term indicators lie in macro trends.** EMA21 generated "bullish" signals throughout the 2022 bear market. Any short-term signal needs a macro filter (EMA200 or equivalent). *(Source: RAME)*

5. **Regime labels are good context, bad signals.** The 2×2+CRISIS framework is real, but treating it as the primary entry signal doesn't work — the per-trade edge is too small. Use it as a gate/filter, not a signal generator. *(Source: RAME → LiqCascade architecture)*

6. **Test the pipeline, not just the model.** Data acquisition, signal latency, execution slippage, and fee structure can each independently kill a strategy that looks great in a Jupyter notebook. *(Source: general)*

7. **Validate fee economics before building execution infrastructure.** Run a threshold sweep on the held-out test set before committing to any non-trivial execution path. A signal with IC=0.135 and dir_acc=54% is real — but BTC 3s moves average 1.7 bps against a 10 bps round-trip taker fee. No threshold filter can bridge a 6× gap between mean move magnitude and fee floor. The sweep takes 30 minutes; building sub-minute execution infrastructure takes weeks. Do the sweep first. *(Source: LOB Microstructure)*

8. **Institutional paper results do not transfer to retail fee tiers.** A paper demonstrating taker-execution profitability may implicitly assume VIP fee tiers (0.02–0.04% per side) rather than standard retail (0.05% per side = 10 bps round-trip). Always compute expected P&L at your actual fee tier before accepting a paper's profitability claim. This is especially critical for high-frequency microstructure strategies where the fee-to-move-magnitude ratio is the dominant P&L driver. *(Source: LOB Microstructure)*

9. **Mean-reversion half-life must be compatible with the trading frequency objective.** A strategy can have genuine mean-reverting structure (Hurst H ≈ 0.26) and still be untradeable if the reversion timescale is months, not hours. For any mean-reversion candidate, compute the OU half-life before building anything and compare it directly to the intended time stop. If P(reversion within time stop) < 20%, the strategy will exit almost entirely on time stops — making it a directional hold, not mean reversion. Use the 100% time-stop rate in the fee sweep as the executable diagnostic: if all trades time-stop regardless of threshold or z-score window, the half-life is incompatible with the design. *(Source: CointPairs)*

10. **Val-period bull markets manufacture false fee-sweep signals.** If the validation period is a sustained bull market, long-only entries with a fixed time stop will show excellent P&L at any z-score threshold — not because the signal is good, but because you're buying a rising asset and holding 72h. Always check: do short entries mirror long entries in P&L? If longs are +150 bps and shorts are −200 bps, the signal is the bull market, not the strategy. *(Source: CointPairs)*

11. **Time-stop rate > 50% is the primary diagnostic for signal over-sensitivity in event-driven strategies.** When more than half of entries exit via time stop with 0% win rate, the entry thresholds are generating false positives — not genuine signal events. The fix is not to remove or extend the time stop; it is to tighten the entry signal so only high-confidence events trigger entries. The time stop is working correctly as a capital-protection mechanism; the problem is upstream at entry. Corollary: if the roi/trailing exits show excellent win rates (>90%) while time_stops dominate by count, the alpha source is real but insufficiently selective. *(Source: LiqCascade Phase 3 preliminary)*

12. **Lead–lag features ≠ directional edge on followers.** A mathematically meaningful cross-path score (signature / Lévy-type antisymmetry) can be **nonstationary** and still **lose money** when traded as **naked long/short** on a high-beta alt with a **wide fixed stop** — the tail risk from adverse moves dominates the distribution even when many exits are small winners. Literature often uses **market-neutral** or **portfolio** constructions; copying only the feature while ignoring the risk model duplicates the wrong object. *(Source: Candidate E / PathSignatureLeadLag_V01 backtest archive, 2026-03-23)*

---

## 10. Version History

| Date | Change |
|---|---|
| 2026-04-07 | v4.1 — **Candidate L full-paper analysis (Palazzi 2025).** Entry significantly revised: formal 5/7+conditional score (downgraded from 6/7 estimate); performance table and walk-forward stats added; 35% OOS success rate across pairs flagged; frequency mismatch (daily-only) and daily/intraday separation from IEEE paper corrected; lookback sensitivity characterised; §4.4 L entry updated with revised rationale. |
| 2026-04-07 | v4.0 — **Sweep #5 complete.** Candidate M (AdaptiveTrend, arXiv 2602.11708) surfaced and evaluated 6/7 PASS — promoted to **#1 build priority**. L drops to #2. Funding Rate Extreme added to §7.4 Techniques Library. §4.4 priority ranking updated. Sweep #5 logged. |
| 2026-04-07 | v3.9 — **OracleSurfer added retroactively to §4.2 ACTIVE.** Project pre-dates this Research Log. Entry covers: v12 dry-run results (Feb 22–Apr 6, 8 trades, PF 0.31, -8.2%), root cause (asymmetric stop/reward requiring ~77% WR), v12→v14 structural overhaul (stop -10%→-5%, ROI ladder, DCA removed, 3yr training, regularization), and current deployment (v14, DigitalOcean droplet, `dry_run: true`, redeployed 2026-04-06 via git). Related files pointer added. |
| 2026-04-06 | v3.8 — **J parking doc consistency:** `EnsembleDonchianTrend_Deep_Dive.md` **v1.5** — Part 10–12 + lessons table use **closed Phase 0** wording; file table **7/7 ≠ GO** note. `EnsembleDonchianTrend_Dev_Plan.md` artifact table Deep Dive **v1.5** + both Donchian docs **PARKED (reference)**. `EnhancedCointPairs_Dev_Plan.md` Phase 3 goal + **§7.4** reframed for **PARKED** J; footer updated. |
| 2026-04-06 | v3.7 — **Candidate J (Ensemble Donchian) PARKED** — Phase 0 **NO-GO** after fee-inclusive backtests and `donchian_phase0_sweep` (see `user_data/results/donchian_phase0_sweep_*.md`). **§4.4** reordered: **L** elevated to top paper-queue item; **K** decoupled from J; J marked parked with artifact pointers. **§4.3** J status + co-investigator **2026-04-06** update (7/7 ≠ trading GO). **Sweep #4 log** top-recommendation line annotated. Related files list: **Deep Dive** added; Dev Plan marked PARKED. `EnsembleDonchianTrend_*` docs updated to PARKED. |
| 2026-03-31 | v3.6 — **Sweep #4 completed.** 3 new candidates: **J (Ensemble Donchian Trend-Following)** evaluated **7/7 STRONG PASS** — promoted to #1 build priority; **K (Multi-Timeframe Trend)** filed as filter/enhancement; **L (Enhanced CointPairs)** held as second-priority. Sweep #1 Zarattini note updated (re-evaluated). Priority ranking updated. Dev plans created: `EnsembleDonchianTrend_Dev_Plan.md` (J) and `EnhancedCointPairs_Dev_Plan.md` (L). Related files updated. |
| 2026-03-29 | v3.5 — **Candidate G PARKED** (empirically weak; code/docs retained). **Parking policy** and **reopen triggers** (add-on addresses weakness). **Priority ranking §4.4** and **Candidate I prerequisites** updated. Deep Dive / Phase1 / Dev_Plan headers aligned. |
| 2026-03-29 | v3.4 — **Candidate G:** layman's Phase 1 summary, **pursuit recommendation** (limited research / not live GO), and **Phase 1 empirical gate** note added below G's co-investigator note (7/7 ≠ trading go). |
| 2026-03-29 | v3.3 — **Candidate G Phase 1 baseline logged** in `CrossSectionalMomentum_Phase1_Summary.md` (multi-year grid, V01_1d year splits, go/no-go). `CrossSectionalMomentum_Deep_Dive.md` v1.2 (V03/V04 safe defaults, Part 6.3 lesson). `CrossSectionalMomentum_Dev_Plan.md` Quick-Start phase updated. Candidate G status line updated. |
| 2026-03-23 | v3.2 — **Candidate E (Path Signatures) ARCHIVED** after decisive negative backtests. Full post-mortem in Section 4.1; `PathSignatureLeadLag_Deep_Dive.md` added. Priority ranking updated (G first; I deferred; E removed). Candidate I prerequisites updated. Lesson #12 added. `deploy/digitalocean.md` added. |
| 2026-03-22 | v3.1 — Candidate I (Signature-Enhanced Momentum) placeholder added. Combination notes added to E and G entries. CrossSectionalMomentum_Dev_Plan.md created. Related files list updated. |
| 2026-03-22 | v3.0 — Candidate G (Cross-Sectional Momentum) evaluated: STRONG PASS 7/7 — first clean pass in project history. Priority ranking updated: G is #1 for next build. Co-investigator assessment added. |
| 2026-03-22 | v2.9 — Sweep #3 completed. Candidate G (Cross-Sectional Momentum) added — recommended next evaluation. Candidate H (On-Chain Whale Flow) reclassified as Technique (Section 7.4). Priority ranking updated: G is #1 for evaluation, E is #2 (parallel dev in progress). Sweep #3 logged with full findings. |
| 2026-03-22 | v2.8 — LiqCascade Phase 3 preliminary results added (5 days, 129 trades, 59% time-stop rate). Lesson #11 added. Sourcing Sweep #3 initiated (separate browser session). LiqCascade analysis script noted in ACTIVE entry. |
| 2026-03-22 | v2.7 — CointPairs archived after Phase 1 FAIL. Full post-mortem in Archived section. Priority ranking updated: Candidate E is now #1. Related files list updated. Two failure modes documented: single-leg directional exposure + trade frequency. |
| 2026-03-22 | v2.6 — CointPairs Phase 0 complete. BNB/ETH@4h is the only GO (6/8). Phase 1 now targeting BNB/ETH@4h via V02 strategy. Research Log candidate entry updated with full findings and Phase 1 target. |
| 2026-03-22 | v2.5 — CointPairs reverted from ARCHIVED to ACTIVE. Phase 0 1h findings preserved in Candidates entry; 4h sweep now in progress. Priority ranking updated: F first (Phase 0 ongoing), E second. |
| 2026-03-22 | v2.4 — CointPairs archived after Phase 0 NO GO (1h only — premature; reverted in v2.5). Two new lessons added (items 9–10). Related files list updated. |
| 2026-03-22 | v2.3 — Candidate F promoted to ACTIVE. Deep Dive created (`CointPairsTrading_Deep_Dive.md`). Strategy V01 and config scaffolded. Related files list updated. |
| 2026-03-22 | v2.2 — Global consistency check performed. Fixed: Sweep #1 recommendation updated to note Candidate A was subsequently archived. Candidates B/C/D evaluation status clarified (parked/reclassified, not pending). Quantpedia Premium timing recommendation updated (Sweep #2 complete). Added periodic consistency check instruction to Claude preamble. No issues found with section numbering, cross-references, evaluation scores, Techniques Library, or Lessons. |
| 2026-03-22 | v2.1 — Candidates E and F evaluated through filter. Both PASS (6/7 + 1 conditional each). E conditional on out-of-sample profitability proof; F conditional on Freqtrade paired-trade coordination logic. |
| 2026-03-22 | v2.0 — Sweep #2 completed. Candidate E (Path Signatures) validated for crypto with multiple sources. Candidate F (Cointegration Pairs Trading) added. Sourcing section expanded in v1.9. Cross-asset proxy pairs added in v1.8. Techniques Library created in v1.7. Objectives language broadened. |
| 2026-03-22 | v1.9 — Major expansion of Sourcing Configuration (Section 5). Added Applied/Practitioner sources (QuantStart, Robot Wealth, Quant's Playbook, Reddit, QuantInsti). Added Reference Literature table (de Prado, Jansen, Chan, Hilpisch, Harris). Added Paid Access Recommendations (Quantpedia Premium highlighted). Added Quantocracy aggregator. Expanded search terms. |
| 2026-03-22 | v1.8 — Added cross-asset proxy pair guidance to Stack & Constraints (Section 3.1). Proxy pair reference table included. |
| 2026-03-22 | v1.7 — Added Candidate E (Path Signatures). Created Techniques Library (Section 7) with 6 entries: Conformal Prediction, Fractional Differentiation, Stationarity-Preserving Preprocessing, Fee Economics Threshold Sweep, LOB OFI Confirmation Filter, CGA-Agent Parameter Optimization. Renumbered Sections 8–10. |
| 2026-03-21 | v1.6 — LiqCascade Phase 3.5 added: OI instrumentation deployed to sidecar, open question #6 added, phase plan updated in Deep Dive. |
| 2026-03-20 | v1.5 — Candidate A (LOB Microstructure) archived. Moved from Candidates to Archived (Section 4.1). Two new lessons added (now Section 9, items 7–8). Related files list updated. |
| 2026-03-20 | v1.4 — Candidate A promoted to ACTIVE. LOB_Microstructure_Deep_Dive.md created. Dev plan superseded by Deep Dive. |
| 2026-03-20 | v1.3 — Candidate A fully evaluated (PASS with conditions). LOB_Microstructure_Dev_Plan.md created. Preamble rewritten to be fully self-contained across sessions. Related files list added. |
| 2026-03-20 | v1.2 — First sourcing sweep completed. 4 candidates added (A–D). Sweep #1 logged. |
| 2026-03-20 | v1.1 — Added Roles (Section 1) and Objectives (Section 2). Renumbered all sections. |
| 2026-03-20 | v1.0 — Initial creation. Populated from RAME archive, LiqCascade deep dive, and RAME project summary. Evaluation filter and sourcing config established. |
