# AlgoTrading Research Log
## Maintained by: [Developer] + Claude (any model)
## Last Updated: 2026-03-20
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
- **Sourcing Sweep Log (Section 7):** Record of each research sweep — what was searched, what was found, what was promoted.
- **Lessons & Principles (Section 8):** Hard-won insights from past projects that apply across all future work.
- **Version History (Section 9):** Change log for this file.

**How to use it:**
- **Developer:** Upload this file at the start of every research or strategy session with Claude. When changes are made during a session, download the updated version and replace your local copy. Keep it in version control (`user_data/info/AlgoTrading_Research_Log.md`).
- **Claude:** Read this entire file before doing anything else. Understand the roles, objectives, what's been tried, what's active, and what's next. Do not suggest approaches already in the registry. Do not confirm ideas uncritically — Section 1 requires you to push back, propose alternatives, and check the developer's reasoning. When changes are made during a session, produce an updated file for the developer to download.

**This file is also used in Cursor sessions** for strategy implementation. When working in Cursor, Claude should read this file for project context and then refer to the relevant Deep Dive document for implementation-specific details. The Research Log provides the "what and why"; the Deep Dive documents provide the "how."

**Related files:**
- `user_data/info/Regime_Adaptive_Ensemble_Deep_Dive.md` — RAME project (ARCHIVED)
- `user_data/info/RAME_Project_Summary.md` — RAME summary (ARCHIVED)
- `user_data/info/LiquidationCascade_Deep_Dive.md` — LiqCascade project (ACTIVE)
- `user_data/info/LOB_Microstructure_Dev_Plan.md` — Candidate A development plan (superseded)
- `user_data/info/LOB_Microstructure_Deep_Dive.md` — Candidate A deep dive (ARCHIVED)

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

**Goal:** Investigate, develop, and deploy novel crypto algorithmic trading systems that significantly outperform traditional investment strategies. The developer already has capital in conventional approaches — the systems built here must justify their complexity with materially higher returns.

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
| **Compute** | DigitalOcean VPS (no GPU); local machine for backtesting |
| **Markets** | Crypto futures (Binance Perpetuals). Primary: BTC/USDT, ETH/USDT |
| **Data budget** | Free or very low cost. CCXT, Binance API, CoinGecko, public APIs |
| **Leverage** | 2–4x typical |
| **Execution** | Freqtrade's standard execution (not HFT, not co-located) |
| **Developer** | Solo. All code written with AI assistance in Cursor |
| **Libraries** | Python ecosystem: scikit-learn, XGBoost, LightGBM, PyTorch (for inference, not heavy training), TA-Lib, pandas, numpy. Open to others if lightweight |

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
- **Key lessons:** See Section 8, items 7 and 8.
- **Potential future salvage:** The LOB OFI signal could serve as a timing confirmation filter for LiqCascade entries (no standalone execution required; no fee problem). Not prioritized — pursue only if LiqCascade Phase 3 data shows a high false-positive entry rate.
- **Deep dive:** `LOB_Microstructure_Deep_Dive.md` (ARCHIVED)

---

### 4.2 ACTIVE

#### Liquidation Cascade Strategy (v1.0)
- **Status:** ACTIVE — Phase 3 (Live Dry-Run), deployed 2026-03-18
- **Core idea:** Detect forced liquidation cascades via Binance WebSocket data as primary alpha signal. Regime framework demoted to context filter only (CRISIS gate + EMA200 macro trend)
- **Architecture:** Sidecar process (WebSocket liquidation stream) → signal file → Freqtrade 5m strategy reads signal → enter with-trend cascade, exit via 2×ATR target / 1×ATR stop / 30min time stop. 4x leverage
- **Why this is different from RAME:** Alpha source is a mechanical market event (forced liquidations), not indicator prediction. Signal is directionally unambiguous while occurring. Not lagged — detected in real time
- **Current deployment:** DigitalOcean droplet, Docker, BTC/USDT + ETH/USDT futures dry-run
- **Phase plan:** Phase 3 (dry-run, 4+ weeks) → Phase 4 (hyperopt) → Phase 5 (multi-pair) → Phase 6 (live capital)
- **Go/no-go for next phase:** 20+ trades, profit factor > 1.0, win rate > 40%, sidecar uptime > 99%
- **Open questions:**
  1. Counter-trend cascade quality (short squeezes in bear markets)
  2. Optimal proxy thresholds (VOL_SPIKE_MULT, CANDLE_BODY_MULT)
  3. ATR-relative vs fixed ROI targets
  4. Funding rate as entry pre-condition
  5. Cascade failure mode characterization
- **Deep dive:** `LiquidationCascade_Deep_Dive.md`

---

### 4.3 CANDIDATES

*Approaches identified as potentially promising but not yet evaluated or attempted. Items here should be run through the Evaluation Filter (Section 6) before committing development time.*

#### CANDIDATE B: Funding Rate Arbitrage (Cross-Exchange or Spot-Perp)
- **Source:** Multiple — ScienceDirect (2025), practitioner guides, open-source implementations on GitHub
- **Core idea:** Exploit the funding rate mechanism on perpetual futures by holding delta-neutral positions (long spot + short perp, or long perp on one exchange + short perp on another). Profit comes from funding payments every 4–8 hours, not price direction.
- **Why it's interesting for us:** Structural alpha — exists because of how perpetual contracts are designed, not statistical pattern. Market-neutral by construction. High trade frequency (funding payments every 4–8h across many pairs = many "collection events" per day). Published research shows up to 115.9% over six months with losses capped at 1.92%. Average annual return estimated at ~19% in 2025. Can be automated. Scales across many pairs simultaneously.
- **Potential concerns:** Not a pure Freqtrade strategy — requires simultaneous positions on spot + futures (or two exchanges), which Freqtrade doesn't natively support. Would need custom execution logic. Capital-intensive for meaningful returns (funding payments are tiny per cycle). Funding rates can flip direction unpredictably. Execution risk on position entry/exit (slippage can eat the spread). May not meet the "high ROI" objective — this is more of a steady income strategy than a home-run approach.
- **Evaluation filter score:** Not yet scored
- **Complementarity to existing:** HIGH — completely different alpha source (carry/funding vs momentum/microstructure). Could run as a parallel "income floor" strategy while LiqCascade provides upside.

#### CANDIDATE C: Crypto Volatility Commonality Forecasting
- **Source:** SSRN (Djanga, Cucuringu & Zhang, Jan 2025) — Oxford-Man Institute authors
- **Core idea:** Use cross-asset realized volatility commonality (the fact that crypto volatility co-moves across assets) to forecast next-day intraday volatility using ML models. The paper then trades crypto options based on the volatility forecast, but the volatility forecasting framework could be repurposed for volatility-timing a directional strategy.
- **Why it's interesting for us:** Oxford-Man pedigree. Source code published on GitHub. The volatility forecast itself could serve as a dynamic filter for our existing strategies (e.g., scale LiqCascade leverage based on forecasted vol, or time entries during forecasted high-vol windows). Cross-asset features mean more signal from the same data.
- **Potential concerns:** Original application is options trading, which we don't do. Repurposing the vol forecast as a strategy filter is our interpretation, not the paper's claim. Realized volatility computation requires high-frequency data. May add complexity without clear standalone alpha.
- **Evaluation filter score:** Not yet scored
- **Complementarity to existing:** MEDIUM — not a standalone strategy but could enhance LiqCascade and future strategies as a volatility-timing layer.

#### CANDIDATE D: CNN Trend Detection on 15m Crypto Data with Stationarity Preprocessing
- **Source:** SSRN (Asareh Nejad et al., Apr 2024)
- **Core idea:** A novel preprocessing method that makes indicator + candlestick data stationary while preserving inter-feature relationships, then feeds it into a CNN for 15-minute trend prediction on crypto. Achieves 53.9% accuracy with 4.18% average biweekly returns, beating buy-and-hold.
- **Why it's interesting for us:** 15m timeframe aligns with active trading frequency objective. The stationarity preprocessing is the novel contribution — could be applied to any model, not just CNN. Directly applicable to crypto. The accuracy is modest but the preprocessing technique might be the real takeaway.
- **Potential concerns:** 53.9% accuracy is barely above coin-flip — reminds us of RAME's lesson about accuracy not equaling edge. Paper is from 2024, no out-of-sample validation mentioned. CNN for time series is somewhat dated compared to newer architectures. May be a "technique to borrow" rather than a "strategy to implement."
- **Evaluation filter score:** Not yet scored
- **Complementarity to existing:** MEDIUM — the preprocessing technique could be valuable as infrastructure for any future ML-based strategy.

---

## 5. Sourcing Configuration

### 5.1 Primary Sources (Claude checks these during sweeps)

| Source | Type | Access | Focus |
|---|---|---|---|
| **SSRN** | Academic preprints | Free, searchable | Novel quantitative strategies, financial ML |
| **arXiv (q-fin)** | Academic preprints | Free, searchable | Cutting-edge ML/DL applied to markets |
| **Quantpedia blog** | Strategy database | Free tier (~70 strategies) | Academic strategies translated to trading rules |
| **Oxford-Man Institute** | Academic research | Newsletter + public papers | ML for quant finance, market microstructure |

### 5.2 Secondary Sources (checked when primary sources don't surface enough)

| Source | Type | Access | Focus |
|---|---|---|---|
| **IEEE Xplore** | Peer-reviewed journals | Abstracts free, papers often paywalled | Signal processing, neural architectures for time series |
| **Journal of Financial Data Science** | Peer-reviewed | Some open access | ML applications in finance |
| **QuantConnect community** | Forums + shared strategies | Free | Implemented strategies with backtests |
| **Freqtrade Discord / GitHub** | Community | Free | Freqtrade-specific ML strategies |

### 5.3 Search Terms for Sourcing Sweeps

Rotate and combine these across sources:

**Core:** `algorithmic trading strategy`, `crypto trading ML`, `systematic trading`

**Architecture-specific:** `state space model trading`, `temporal fusion transformer finance`, `reinforcement learning trading`, `hawkes process order flow`, `regime detection trading`, `liquidation cascade crypto`, `order flow imbalance`

**Technique-specific:** `mean reversion crypto`, `momentum strategy ML`, `volatility forecasting`, `funding rate strategy`, `market microstructure alpha`

**Meta/methodology:** `backtesting pitfalls`, `walk-forward validation trading`, `overfitting trading strategies`, `synthetic data augmentation finance`

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

## 7. Sourcing Sweep Log

*Each sweep gets an entry here. This prevents re-searching the same ground.*

### Sweep #1
- **Date:** 2026-03-20
- **Sources checked:** SSRN, arXiv (q-fin.TR, q-fin.ST, q-fin.CP — Dec 2025 through Feb 2026), Quantpedia blog (Dec 2025 – Feb 2026), Oxford-Man Institute publications, practitioner sources
- **Search terms used:** `crypto trading strategy novel 2025 2026`, `crypto market microstructure scalping`, `funding rate arbitrage perpetual futures automated`, `Quantpedia crypto trading strategy new`, `arXiv quantitative finance crypto`
- **Papers/sources reviewed:** ~25 papers and articles scanned, ~8 read in detail
- **Candidates surfaced:** 4 (A through D, see Section 4.3)
- **Top recommendation from Claude:** Candidate A (Order Book Microstructure) stands out — it's from Jan 2026, uses our exact exchange (Binance Futures), has published code, portable cross-asset features, and represents a genuinely different alpha source from LiqCascade. Candidate B (Funding Rate Arb) is interesting but may not meet the high-ROI objective and requires non-Freqtrade infrastructure.
- **Notable papers reviewed but not promoted:**
  - *Catching Crypto Trends* (Zarattini et al., SSRN 2025) — Donchian channel ensemble on crypto. Solid but conventional trend-following; unlikely to significantly outperform simpler momentum approaches we could build ourselves.
  - *Risk-Aware Deep RL for Crypto Trading* (Bandarupalli, SSRN 2025) — PPO-based RL. Underperformed buy-and-hold (Sharpe 1.23 vs 1.46). RL for trading remains promising in theory but this specific paper is a cautionary example.
  - *CGA-Agent: Genetic Algorithm for Crypto Trading* (arXiv 2025) — Multi-agent genetic algo for parameter optimization. Interesting meta-approach to tuning, but the underlying strategies being optimized are standard TA. Could revisit as an optimization technique rather than a strategy.
  - *BTC Seasonality / 2-hour hold strategy* (Quantpedia/SSRN) — Holding BTC only 2 hours per day based on NYSE open/close timing. Intriguing anomaly but very low frequency, fragile edge, and unclear if it persists post-ETF era.

---

## 8. Lessons & Principles

Hard-won insights that apply across all approaches. Add to this as projects conclude.

1. **ML accuracy ≠ trading edge.** A classifier can achieve 100% accuracy and produce zero profit if it's learning the labeling formula instead of future returns. Always test whether model output predicts forward P&L, not just label match. *(Source: RAME)*

2. **Entry quality > exit optimization.** Across 8 RAME backtest runs, changing exits shuffled where losses appeared but never changed the total. The real lever is being selective about which trades to take. *(Source: RAME)*

3. **Structural alpha > statistical alpha.** Liquidation cascades exist because of market mechanics (forced selling), not because of a statistical pattern that could be arbitraged away. Prefer approaches with a clear *why*. *(Source: RAME → LiqCascade pivot)*

4. **Short-term indicators lie in macro trends.** EMA21 generated "bullish" signals throughout the 2022 bear market. Any short-term signal needs a macro filter (EMA200 or equivalent). *(Source: RAME)*

5. **Regime labels are good context, bad signals.** The 2×2+CRISIS framework is real, but treating it as the primary entry signal doesn't work — the per-trade edge is too small. Use it as a gate/filter, not a signal generator. *(Source: RAME → LiqCascade architecture)*

6. **Test the pipeline, not just the model.** Data acquisition, signal latency, execution slippage, and fee structure can each independently kill a strategy that looks great in a Jupyter notebook. *(Source: general)*

7. **Validate fee economics before building execution infrastructure.** Run a threshold sweep on the held-out test set before committing to any non-trivial execution path. A signal with IC=0.135 and dir_acc=54% is real — but BTC 3s moves average 1.7 bps against a 10 bps round-trip taker fee. No threshold filter can bridge a 6× gap between mean move magnitude and fee floor. The sweep takes 30 minutes; building sub-minute execution infrastructure takes weeks. Do the sweep first. *(Source: LOB Microstructure)*

8. **Institutional paper results do not transfer to retail fee tiers.** A paper demonstrating taker-execution profitability may implicitly assume VIP fee tiers (0.02–0.04% per side) rather than standard retail (0.05% per side = 10 bps round-trip). Always compute expected P&L at your actual fee tier before accepting a paper's profitability claim. This is especially critical for high-frequency microstructure strategies where the fee-to-move-magnitude ratio is the dominant P&L driver. *(Source: LOB Microstructure)*

---

## 9. Version History

| Date | Change |
|---|---|
| 2026-03-20 | v1.5 — Candidate A (LOB Microstructure) archived. Moved from Candidates to Archived (Section 4.1). Two new lessons added (Section 8, items 7–8). Related files list updated. |
| 2026-03-20 | v1.4 — Candidate A promoted to ACTIVE. LOB_Microstructure_Deep_Dive.md created. Dev plan superseded by Deep Dive. |
| 2026-03-20 | v1.3 — Candidate A fully evaluated (PASS with conditions). LOB_Microstructure_Dev_Plan.md created. Preamble rewritten to be fully self-contained across sessions. Related files list added. |
| 2026-03-20 | v1.2 — First sourcing sweep completed. 4 candidates added (A–D). Sweep #1 logged. |
| 2026-03-20 | v1.1 — Added Roles (Section 1) and Objectives (Section 2). Renumbered all sections. |
| 2026-03-20 | v1.0 — Initial creation. Populated from RAME archive, LiqCascade deep dive, and RAME project summary. Evaluation filter and sourcing config established. |
