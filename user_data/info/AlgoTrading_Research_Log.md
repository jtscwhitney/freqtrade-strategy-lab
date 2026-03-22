# AlgoTrading Research Log
## Maintained by: [Developer] + Claude (any model)
## Last Updated: 2026-03-22
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
- `user_data/info/CrossSectionalMomentum_Dev_Plan.md` — Candidate G development plan (NEW)
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

### 4.2 ACTIVE

#### Liquidation Cascade Strategy (v1.0)
- **Status:** ACTIVE — Phase 3 (Live Dry-Run), deployed 2026-03-18
- **Core idea:** Detect forced liquidation cascades via Binance WebSocket data as primary alpha signal. Regime framework demoted to context filter only (CRISIS gate + EMA200 macro trend)
- **Architecture:** Sidecar process (WebSocket liquidation stream) → signal file → Freqtrade 5m strategy reads signal → enter with-trend cascade, exit via 2×ATR target / 1×ATR stop / 30min time stop. 4x leverage
- **Why this is different from RAME:** Alpha source is a mechanical market event (forced liquidations), not indicator prediction. Signal is directionally unambiguous while occurring. Not lagged — detected in real time
- **Current deployment:** DigitalOcean droplet, Docker, 5 pairs dry-run: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT. max_open_trades=5.
- **Phase plan:** Phase 3 (dry-run, 4+ weeks) → Phase 3.5 (LOB-OFI+OI filter validation) → Phase 4 (hyperopt) → Phase 5 (additional pairs if needed) → Phase 6 (live capital)
- **Go/no-go for Phase 4:** 20+ trades, profit factor > 1.0, win rate > 40%, sidecar uptime > 99%
- **Phase 3.5 (ACTIVE — 2026-03-21):** OI change rate instrumentation deployed to sidecar. `oi_contracts` and `oi_change_pct_1m` now logged per symbol per minute in `signal_history.jsonl`. Enables retrospective validation of LOB-OFI+OI entry filter once 20+ trades accumulated. Strategy V04 unchanged. See Deep Dive Phase 3.5 for full details.
- **Phase 3 preliminary results (2026-03-22 — 5 days, 129 trades):**
  - Win rate: 39.5% | Avg profit: -0.207% | Profit factor: 0.659 — **below Phase 4 thresholds**
  - Exit breakdown: `time_stop` 76 trades (59%, avg -1.031%, 0% win) · `roi` 49 trades (38%, avg +0.738%, 96% win) · `trailing_stop_loss` 4 trades (3%, avg +3.859%, 100% win)
  - **Root cause: 59% time-stop rate.** Signal is real (roi/trailing exits are excellent) but VOL_SPIKE_MULT/CANDLE_BODY_MULT thresholds are too loose — generating ~26 entries/day across 5 pairs vs expected 1–2 genuine cascades/pair/day. False-positive entries have no cascade momentum and exit at -1% via time stop.
  - By pair: ETH -0.044%, SOL +0.068% (near break-even) · BTC -0.437%, BNB -0.413% (worst) · XRP -0.185%
  - **Action:** Do not change parameters yet — 5 days is a single regime snapshot. Revisit at **2026-04-05** with 2+ weeks of data. If time-stop rate remains >50%, tighten thresholds before Phase 4 hyperopt.
  - **Phase 3.5 OI retrospective:** Run at 2026-04-05 once ~100+ trades have OI data attached (instrumentation live since 2026-03-21). Key question: do roi/trailing exits have higher OI change rate at entry than time_stop exits?
  - **Analysis script:** `user_data/scripts/ft_analyze.py` — run via `docker cp ft_analyze.py freqtrade_liqcascade:/tmp/ && docker exec freqtrade_liqcascade python /tmp/ft_analyze.py`
- **Open questions:**
  1. Counter-trend cascade quality (short squeezes in bear markets)
  2. Optimal proxy thresholds (VOL_SPIKE_MULT, CANDLE_BODY_MULT) — **flagged by Phase 3 preliminary: likely too loose**
  3. ATR-relative vs fixed ROI targets
  4. Funding rate as entry pre-condition
  5. Cascade failure mode characterization
  6. LOB-OFI + OI filter utility — does OI change rate at cascade detection predict 15–35 min trade outcomes? (Phase 3.5 retrospective — run 2026-04-05)
- **Deep dive:** `LiquidationCascade_Deep_Dive.md` (in `freqtrade-scalper` repo)

---

### 4.3 CANDIDATES

*Approaches identified as potentially promising but not yet evaluated or attempted. Items here should be run through the Evaluation Filter (Section 6) before committing development time.*

#### CANDIDATE B: Funding Rate Arbitrage (Cross-Exchange or Spot-Perp)
- **Source:** Multiple — ScienceDirect (2025), practitioner guides, open-source implementations on GitHub
- **Core idea:** Exploit the funding rate mechanism on perpetual futures by holding delta-neutral positions (long spot + short perp, or long perp on one exchange + short perp on another). Profit comes from funding payments every 4–8 hours, not price direction.
- **Why it's interesting for us:** Structural alpha — exists because of how perpetual contracts are designed, not statistical pattern. Market-neutral by construction. High trade frequency (funding payments every 4–8h across many pairs = many "collection events" per day). Published research shows up to 115.9% over six months with losses capped at 1.92%. Average annual return estimated at ~19% in 2025. Can be automated. Scales across many pairs simultaneously.
- **Potential concerns:** Not a pure Freqtrade strategy — requires simultaneous positions on spot + futures (or two exchanges), which Freqtrade doesn't natively support. Would need custom execution logic. Capital-intensive for meaningful returns (funding payments are tiny per cycle). Funding rates can flip direction unpredictably. Execution risk on position entry/exit (slippage can eat the spread). May not meet the "high ROI" objective — this is more of a steady income strategy than a home-run approach.
- **Evaluation filter score:** Not scored — parked. Requires non-Freqtrade infrastructure; lower ROI potential vs E and F.
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
- **Status:** CANDIDATE — validated for crypto in Sweep #2
- **Source:** Rough path theory literature (SSRN, arXiv); libraries: `iisignatures`, `esig`. Key references: Gyurkó et al. (2013) "Extracting information from the signature of a financial data stream" (arXiv:1307.7244); Futter et al. (2023) "Signature Trading" (arXiv:2308.15135); Rahimi (2024) GitHub: lead-lag-portfolios using Lévy-area on crypto.
- **Core idea:** Use path signatures (from rough path theory) to summarize the "shape" of recent multi-asset price paths into a compact mathematical representation, then feed that into a simple model (even linear regression) to detect lead-lag relationships — e.g., when ETH is about to follow BTC's move based on the geometric structure of their recent paths.
- **Why it's interesting for us:** Theoretically grounded in serious mathematics (not data-mining). Replaces dozens of hand-crafted indicators with a single principled representation. Works on standard OHLCV data — no sidecar needed, no special data source. Libraries are lightweight and CPU-friendly. Simple downstream models (linear/logistic regression) reduce overfitting risk vs deep learning. Lead-lag detection between correlated crypto pairs could generate frequent trades across multiple pairs simultaneously (addresses trade frequency objective). Different alpha source from everything else in our registry.
- **Crypto-specific validation (found in Sweep #2):**
  - Rahimi (GitHub: lead-lag-portfolios) directly implements Lévy-area lead-lag detection on a universe of cryptocurrencies, constructs market-neutral portfolios from leader/follower rankings, and backtests them. Full Python code available with notebooks.
  - Futter et al. (2023) "Signature Trading" derives a closed-form mean-variance optimal trading strategy using signatures — trading strategy as a linear functional on signature terms. Bypasses explicit price prediction entirely.
  - A May 2025 arXiv paper on "Segmented Signatures" for pair trading proposes a decomposition method that reduces computational complexity while preserving cross-asset interaction information — directly applicable to our multi-pair setup.
  - QuantStart has a multi-part tutorial series on rough path theory and signatures applied to quantitative finance, including Python code for lead-lag and time-joined transformations.
- **Potential concerns:** BTC-ETH lead-lag may be partially arbitraged at our execution timeframes. The "shape" features may be sensitive to the lookback window chosen. Need to run fee economics validation (Technique 7.3) early — if the lead-lag edge is small per trade, we hit the same fee problem as LOB Microstructure. A newer paper (DeltaLag, ICAIF 2025) suggests adaptive learned lags outperform static signature-based approaches — worth monitoring but adds complexity.
- **Combination potential (→ Candidate I):** E and G (Cross-Sectional Momentum) exploit the same underlying phenomenon — information diffusion across assets at different speeds. Signatures capture the *shape* of diffusion; momentum captures the *ranking*. A combined approach could use signature-derived lead-lag scores to improve the momentum ranking (e.g., weight leaders higher, detect when lead-lag structure is strengthening/weakening). **Candidate I is reserved for this combination — contingent on independent validation of both E and G.** Do not build I until at least one of E/G is validated in our stack.
- **Evaluation filter score:** Scored 2026-03-22 — see below
- **Complementarity to existing:** HIGH — entirely different alpha source (cross-asset geometric patterns vs microstructure events). Could run on standard Freqtrade candles with no infrastructure changes.

**CANDIDATE E — EVALUATION FILTER:**

| # | Criterion | Assessment | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Standard OHLCV data only. No special data source needed. Binance API / CCXT / freqtrade download-data. This is a major advantage over Candidate A (LOB). | **PASS** |
| 2 | **Compute fit** | `iisignature` is CPU-only, numpy-based, pip-installable. Signature computation on truncated paths (level 3–5) is fast — O(d^n) per path but d is small (2–5 dimensions) and n is small (3–5 levels). Linear regression downstream model has trivial compute. No GPU needed for training or inference. | **PASS** |
| 3 | **Freqtrade compatibility** | Excellent. Signature features are computed from OHLCV data in `populate_indicators()`. Lead-lag scores become standard dataframe columns. Entry/exit signals generated in `populate_entry_trend()` / `populate_exit_trend()`. No sidecar needed. Multi-pair via `informative_pairs()` — load BTC data as informative when trading ETH, compute lead-lag between them. This is native Freqtrade. | **PASS** |
| 4 | **Out-of-sample evidence** | Mixed. Rahimi's GitHub has backtested crypto portfolios using Lévy-area lead-lag. Futter et al. (2023) derive mean-variance optimal strategies with signatures. The foundational paper (Gyurkó et al., 2013) tests on FTSE 100 futures with walk-forward validation. However, no single paper shows a fully backtested, fee-inclusive, out-of-sample profitable trading strategy on crypto using signatures for short-term trading at our timeframes. The evidence is more "the features are predictive" than "here's a profitable system." | **CONDITIONAL PASS** — signal validity demonstrated, profitability at our timeframes not yet proven |
| 5 | **Clear mechanism** | Yes. The Lévy area between two assets' price paths mathematically captures lead-lag relationships — if asset A's moves consistently precede asset B's, the signed area is nonzero. This is grounded in rough path theory (Terry Lyons, Oxford). The economic mechanism is information diffusion: some assets react to news faster than others due to liquidity differences, attention asymmetries, or market microstructure. Well-theorized and well-understood. | **PASS** |
| 6 | **Complementarity** | HIGH. LiqCascade is event-driven momentum on single assets. This is cross-asset relational and directionally agnostic (it trades the *relationship*, not a price direction). Completely different alpha source. | **PASS** |
| 7 | **Implementation scope** | 1 week is feasible for an MVP. Day 1: download multi-pair OHLCV data, implement lead-lag transformation and Lévy-area computation using `iisignatures`. Day 2: compute pairwise lead-lag scores across a universe of 5–10 crypto pairs, validate that scores are nonzero and time-varying. Day 3: build a simple strategy — when lead-lag score crosses threshold, enter the lagging asset in the direction of the leader's move. Day 4: backtest in Freqtrade. Day 5: fee economics threshold sweep (Technique 7.3). All on standard OHLCV data, no infrastructure to build. | **PASS** |

**Filter score: 6/7 PASS, 1/7 CONDITIONAL PASS → Overall: PASS**

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
- **Status:** CANDIDATE — surfaced in Sweep #3, ready for formal evaluation
- **Source:** Drogen, Hoffstein & Otte (SSRN 2023) "Cross-sectional Momentum in Cryptocurrency Markets"; Han, Kang & Ryu (SSRN 2023) "Time-Series and Cross-Sectional Momentum: Comprehensive Analysis under Realistic Assumptions"; ScienceDirect (2025) "Cryptocurrency market risk-managed momentum strategies"; Rohrbach et al. (2017) high-frequency momentum on crypto.
- **Core idea:** Rank a universe of 10–30 crypto assets by recent returns (formation period: 1h to 30 days). Go long the top-ranked winners and short the bottom-ranked losers. Rebalance at the holding period frequency. The cross-sectional variant exploits relative performance differences across assets rather than absolute price direction.
- **Why it's interesting for us:** Directly addresses our two biggest recent failure modes. (1) **High frequency by design:** with hourly formation periods across 20+ pairs, this generates many trades per day — the opposite of CointPairs' 0.05 trades/day problem. (2) **Per-trade moves well above fee floor:** hourly crypto momentum moves are typically 50–300+ bps, far above our 10 bps round-trip fee. Works on standard OHLCV data, no sidecar needed. Established strategy class with strong academic evidence. Multiple enhancement paths: risk-managed variants (volatility-scaling), winner-only variants (losers rebound — documented by Han et al.), combination with path signatures (Candidate E) for smarter ranking. The literature specifically finds that cross-sectional momentum works *better* for crypto than for traditional currencies (Rohrbach et al.).
- **Potential concerns:** Momentum crashes are documented in crypto (Grobys 2025) — can experience severe tail losses. Han et al. (2023) find that under realistic assumptions (fees, daily price fluctuations, liquidation risk), many momentum portfolios are actually liquidated and statistically significant returns become insignificant. The momentum effect is concentrated among winners — losers often rebound and inflict losses. Risk-managed variants partially address crashes but add complexity. Need to validate that the effect persists at our specific formation/holding periods on Binance Futures perpetuals.
- **Combination potential (→ Candidate I):** G and E (Path Signatures) could be combined — signatures provide a richer feature set for ranking assets than simple past returns. Instead of ranking by raw return over the formation period, rank by a signature-derived score that captures the *shape* and *lead-lag structure* of recent price paths. **Candidate I is reserved for this combination — contingent on independent validation of both E and G.** Build G standalone first.
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

#### CANDIDATE H: On-Chain / Whale Flow Signals (reclassified as Technique)
- **Status:** RECLASSIFIED — better suited as a Technique/filter than a standalone strategy
- **Source:** Practitioner ecosystem — Nansen, Glassnode, Whale Alert, Arkham, CryptoQuant, Santiment, Dune Analytics
- **Core idea:** Use exchange inflow/outflow data, whale wallet accumulation/distribution patterns, and stablecoin supply changes as leading indicators for directional trades.
- **Why it didn't become a full candidate:** (1) Data frequency is typically daily or at best hourly — incompatible with our active-trading frequency objective for a standalone strategy. (2) Most tools are designed for discretionary analysis, not automated trading. (3) Signal-to-noise ratio for fully automated execution is unproven. (4) Would require a sidecar to ingest API data, adding infrastructure.
- **Where it fits:** Added to Techniques Library (Section 7) as a potential macro filter — e.g., only take LiqCascade or momentum entries when whale accumulation trend score is favorable. Similar role to the CRISIS gate but using on-chain data instead of ATR.

#### CANDIDATE I: Path Signature-Enhanced Cross-Sectional Momentum (RESERVED)
- **Status:** RESERVED — contingent on independent validation of both Candidate E (Path Signatures) and Candidate G (Cross-Sectional Momentum)
- **Core idea:** Replace or augment the simple return-based ranking in cross-sectional momentum with signature-derived features that capture the *shape* and *lead-lag structure* of recent multi-asset price paths. Instead of ranking by "which asset had the highest return over the last N hours," rank by "which asset's path signature indicates it is currently a leader in the information diffusion process." This could improve ranking accuracy, reduce momentum crash exposure (signatures may detect when lead-lag structure is breaking down), and provide a richer signal than raw returns.
- **Prerequisites:** At least one of E or G must be validated independently in our stack before building I. If G works standalone, E's contribution would be tested as an enhancement layer. If E works but G doesn't, I is moot (the ranking framework is G's contribution).
- **Do not evaluate, plan, or build until prerequisites are met.**

### 4.4 Current Priority Ranking (as of Sweep #3 — 2026-03-22)

1. **Candidate G (Cross-Sectional Momentum)** — **STRONG PASS (7/7). Recommended next build.** First candidate to achieve a clean pass on all criteria. Directly addresses both failure modes that killed our last two candidates (trade frequency + fee economics). No sidecar, no paired-trade coordination, no special data. Implementation is straightforward — ranking logic in `populate_indicators()` via `DataProvider`, entry signals for top/bottom-ranked pairs. Risk-managed and winner-only variants documented in the literature for further enhancement.

2. **Candidate E (Path Signatures)** — Still strong. **Parallel implementation underway by co-developer** — check for merge-pending results before starting. If E validates independently, it becomes an enhancement layer for G (→ Candidate I).

3. **Candidate I (Signature-Enhanced Momentum)** — RESERVED. Contingent on E + G independent validation. Do not build prematurely.

4. **Candidates B (Funding Rate Arb), C (Vol Commonality), D (CNN Preprocessing)** — Parked. B requires non-Freqtrade infrastructure. C and D are techniques, not standalone strategies (already captured in Techniques Library).

*This ranking reflects the state of knowledge as of the date above. Update after any new sweep, evaluation, or project outcome.*

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
- **Relevant candidates:** Any future ML-based strategy; potentially Candidate E (Path Signatures) if a regression model is used.

### 7.2 Feature Engineering / Preprocessing

#### Fractional Differentiation
- **Status:** AVAILABLE
- **What it does:** Makes time series stationary while preserving long-range memory. Standard differencing (percent change) removes all price-level information; fractional differentiation removes just enough trend to achieve stationarity while retaining predictive memory of historical levels.
- **Libraries:** `fracdiff` (Python, pip-installable)
- **Source:** Marcos López de Prado, "Advances in Financial Machine Learning" (2018), Ch. 5. Resurgence in 2025–2026 IEEE papers on memory-augmented networks.
- **How we'd use it:** Apply as a standard preprocessing step to any ML model that takes price data as input. Replace simple returns or percent changes with fractionally differenced series. Gives the model access to both stationarity (required for ML) and price-level memory (required for detecting support/resistance, trend structure, etc.).
- **When to apply:** During feature engineering for any ML-based candidate. Low effort — one function call per feature column.
- **Relevant candidates:** Candidate E (Path Signatures — could fractionally differentiate the input paths), any future FreqAI model.

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
  - *Catching Crypto Trends* (Zarattini et al., SSRN 2025) — Donchian channel ensemble on crypto. Solid but conventional trend-following; unlikely to significantly outperform simpler momentum approaches we could build ourselves.
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

---

## 10. Version History

| Date | Change |
|---|---|
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
