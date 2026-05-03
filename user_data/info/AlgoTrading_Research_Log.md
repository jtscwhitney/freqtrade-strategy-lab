# AlgoTrading Research Log
## Maintained by: [Developer] + Claude (any model)
## Version: v5.1 (2026-05-03 — Sourcing protocol restructure; structural-alpha / gate-shaped bias)
## Stack: Cursor / Freqtrade / FreqAI / Claude Opus 4.7
## Prior versions: `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md` (v1.0–v4.3)
## Companion: `Research_Audit_2026-04-17_Findings_and_Path_Forward.md` — read this first if you have not seen the audit

---

## READ THIS FIRST — What This File Is and How to Use It

**This file is the shared memory and operating agreement between the developer and Claude across all sessions.** Claude has no persistent memory between conversations. Every new session — claude.ai or Cursor — starts from zero. This file bridges that gap.

**v5.0 changes (2026-04-17):** A process audit found that the prior 7-point evaluation filter had a 0/4 hit rate among PASS / STRONG PASS candidates that reached Phase 0. The filter was scoring buildability and literature fit, not edge. v5.0 rebuilds the workflow around a multi-stage gate (buildability → edge deflation → paper replication → Phase 0 economics → Phase 1 forward), introduces filter-precision tracking and a workflow kill criterion, refocuses effort on the only two strategies with real-time validation feedback (LiqCascade, OracleSurfer), and frames a synthesis initiative (GatedExecution) that combines lessons from archived candidates rather than repeatedly drawing fresh papers.

**v5.1 changes (2026-05-03):** Sourcing protocol restructure. The v5.0 multi-stage gate is working as designed (Candidate O was correctly rejected at §6.1 for 4/7; Candidate N investigation correctly archived at step 3) — but the *upstream* candidate flow is still drawing from broad academic / practitioner sources with novelty bias, which has produced 0/7 wins. v5.1 narrows sourcing along three structural axes derived from the project's own evidence (Lesson #3, Lesson #17): structural-alpha sources, gate-shaped signals for §4.5 GatedExecution, and capital-efficiency / portfolio-construction overlays. §5, §5.5, §5.6 restructured around these axes. §4.6 sequencing expanded to 8 numbered steps reflecting the May–June 2026 plan (4 sessions of active work between now and LiqCascade Phase 4 resolution, then 2 trigger-based steps post-resolution). Sweep #6 trigger language tightened: the sweep produces queued candidates only — no implementation work begins until LiqCascade resolves. Lesson #18 added.

**What it contains:**
- **Roles & Objectives (§1–§2):** Who we are to each other and what we're trying to achieve. Claude is an equal partner, not an assistant.
- **Stack & Constraints (§3):** The fixed technical realities every approach must fit within.
- **Approach Registry (§4):** Active, archived, parked, candidate strategies. Project memory — check before suggesting anything to avoid re-treading.
- **Synthesis Initiative — GatedExecution (§4.5):** The new primary architectural thesis. Combine validated signals from archived/parked candidates instead of always drawing fresh papers.
- **Sourcing Configuration (§5):** Where we look for new strategy ideas. v5.1 narrows along three structural axes: structural-alpha sources, gate-shaped signals for §4.5, and capital-efficiency overlays.
- **Evaluation Process (§6):** The new multi-stage gate. Buildability filter → edge deflation pass → paper replication checklist → Phase 0 economics → Phase 1 forward. Plus filter-precision tracking and the workflow kill criterion.
- **Techniques Library (§7):** Reusable techniques, tools, methods that strengthen candidates during evaluation, development, or operation.
- **Sourcing Sweep Log (§8):** Record of each research sweep — sources, terms, papers reviewed, outcomes.
- **Lessons & Principles (§9):** Hard-won insights from past projects that apply across all future work.
- **Version History (§10):** Change log for this file.

**How to use it:**
- **Developer:** Upload at the start of every session. When changes are made, download the updated version and replace your local copy. Keep in version control.
- **Claude:** Read this entire file before doing anything else. Understand the roles, objectives, what's been tried, what's active, what's next, and **the empirical track record of your own evaluation methods**. Do not suggest approaches already in the registry. Do not confirm ideas uncritically — §1 requires you to push back, propose alternatives, check the developer's reasoning. **Periodically (every 2–3 sessions or after major updates), do a global consistency check:** verify cross-references, candidate statuses, sweep recommendations vs current statuses, and flag stale or contradictory information.

**Workflow at a glance (Cursor + claude.ai):**

*Track 1 — Research (claude.ai web sessions):*
1. **Sourcing Sweeps:** Reduced cadence (no more than one sweep per ~6 weeks of calendar time, OR after a Phase 1 outcome on an active candidate, whichever is later). v5.1: each sweep covers all three structural axes (§5) and produces queued candidates only — no implementation work begins until ACTIVE strategies resolve their go/no-go gates. Quality > quantity. See §5 for sources, §5.5 for axis-organized search terms, §5.6 for sweep protocol.
2. **Candidate Evaluation:** Two-stage gating. (a) The 7-point Buildability Filter (§6.1) — necessary but not sufficient. (b) The Edge Deflation Pass (§6.2) — mandatory. Only candidates clearing both proceed to a Paper Replication Checklist (§6.3) and Dev Plan.
3. **Priority Ranking:** §4.6 reflects effort allocation, not just candidate ordering. The 70/30 rule (§4.6) is the operating principle until further notice.
4. **Dev Plan Creation:** For the top-ranked candidate that has cleared §6.2, Claude creates a Dev Plan a Cursor session can execute from without conversation history.

*Track 2 — Implementation (Cursor sessions):*
1. Read this Research Log for context, then the relevant Dev Plan for implementation details.
2. Implementation follows the Dev Plan's phase structure with explicit go/no-go gates.
3. **Phase 0 fee economics sweep is mandatory** — Phase 0 also runs the regime-split test (each calendar year of test data must be reported separately) before any Phase 1 work begins.
4. When a candidate fails: write a full post-mortem in §4.2 Archived, extract reusable infrastructure, add new lessons to §9, update the Priority Ranking, **and update the Filter Precision Tracking table in §6.5**.
5. When a candidate succeeds: promote to Active (§4.1), create/update a Deep Dive document.

*Syncing between tracks:*
- At the end of any session, Claude produces an updated Research Log for the developer to download.
- At the start of any session, the developer uploads the latest version.

**Related files:**
- `user_data/info/Research_Audit_2026-04-17_Findings_and_Path_Forward.md` — the audit that prompted v5.0
- `user_data/info/AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md` — frozen prior version
- `user_data/info/LiquidationCascade_Deep_Dive.md` — LiqCascade (ACTIVE)
- `user_data/info/CointPairsTrading_Deep_Dive.md` — Candidate F (ARCHIVED)
- `user_data/info/PathSignatureLeadLag_Deep_Dive.md` — Candidate E (ARCHIVED)
- `user_data/info/CrossSectionalMomentum_Dev_Plan.md` — Candidate G (PARKED — referenced for GatedExecution synthesis)
- `user_data/info/CrossSectionalMomentum_Deep_Dive.md` — Candidate G (PARKED)
- `user_data/info/CrossSectionalMomentum_Phase0_Summary.md` / `Phase1_Summary.md` — G results
- `user_data/info/LOB_Microstructure_Dev_Plan.md` / `Deep_Dive.md` — Candidate A (ARCHIVED)
- `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` / `Deep_Dive.md` — Candidate J (PARKED)
- `user_data/info/EnhancedCointPairs_Dev_Plan.md` / `Deep_Dive.md` — Candidate L (PARKED; forward experiment concluded 2026-05-02)
- `user_data/info/AdaptiveTrend_Dev_Plan.md` / `Deep_Dive.md` — Candidate M (ARCHIVED)
- `deploy/digitalocean.md` — DigitalOcean deployment reference
- OracleSurfer — in `Freqtrade` repo (separate): `user_data/strategies/OracleSurfer_v14_PROD.py` (ACTIVE dry-run)

---

## 1. Roles

Claude and the developer are **equal partners** — Co-Investigators, Co-Strategists, Co-Developers. Claude does not default to confirming the developer's ideas. Both parties brainstorm, challenge assumptions, propose alternatives, check each other's reasoning. The goal is the best possible system, not agreement.

**In practice this means Claude should:**
- Push back when an approach has flaws, even if the developer is enthusiastic
- Proactively suggest alternatives the developer hasn't considered
- Flag when a line of investigation is unlikely to meet objectives, rather than silently building what's asked
- Bring its own research and ideas to sourcing sweeps, not just process what the developer provides
- **Track the empirical accuracy of its own methods.** Acknowledge when an evaluation framework is failing and recommend revising it. The 0/4 hit rate of the prior 7-point filter is the precedent — ongoing tracking is in §6.5.

---

## 2. Objectives

**Primary goal:** Investigate, develop, and deploy crypto algorithmic trading systems — novel, adapted, or assembled from known techniques — that significantly outperform conventional investment strategies (i.e., justify their complexity with materially higher risk-adjusted returns).

**Risk tolerance:** High. Willing to accept elevated risk for elevated returns.

**Trade frequency objective (revised v5.0):**
- The prior phrasing ("must be active traders — high trade counts per unit time, comparable to scalping") was selecting against likely winners. Multiple academic literatures (cross-asset trend-following, carry, term-structure) consistently show the highest replicable Sharpes at daily-to-weekly horizons. Forcing strategies into intraday windows pushed candidates into fee-sensitive or noise-driven designs.
- **New phrasing:** the *portfolio* must be active. The minimum acceptable activity floor is **≥ 30 closed trades / month at the portfolio (sum of strategies) level**, evaluated as a 90-day rolling average. Any individual strategy may run as slowly as daily rebalancing if the portfolio meets the floor.
- Concretely, this unlocks: dual-leg pairs trading at daily granularity across many spreads, daily/weekly trend-following, basis/funding sleeves — all previously rejected for being too slow as standalones.

**Forward-testing realism:**
- Some approaches will only be testable via dry-run or live forward testing.
- Forward-test windows should be sized by **expected trade count to statistical confidence**, not by calendar time. Minimum 50 closed trades for a binary go/no-go read; minimum 150 for a Sharpe estimate with usable confidence intervals. Strategies that cannot generate this within 60 calendar days at expected frequency must be tested with a longer commitment up front, or rejected at evaluation.

**Capital horizon:** Solo developer. AI-assisted. Limited capital. The systems must be operationally simple enough that one person + AI can maintain, monitor, and iterate on them indefinitely.

---

## 3. Stack & Constraints

These are the fixed realities every approach must fit within.

| Constraint | Detail |
|---|---|
| **Framework** | Freqtrade (Python, Docker) with FreqAI for ML models |
| **IDE / AI** | Cursor with Claude as co-developer |
| **Compute** | Cloud VPS (DigitalOcean) for live/dry-run; local for backtesting. Non-GPU preferred. |
| **Markets** | Crypto futures primarily (Binance Perpetuals as default). Other Freqtrade-supported exchanges considered. See §3.1. |
| **Data budget** | Free or low-cost preferred. CCXT, Binance API, CoinGecko, public APIs. Paid sources considered if ROI is compelling or proven. |
| **Leverage** | 2–4x typical |
| **Execution** | Freqtrade standard (not HFT, not co-located) |
| **Fee tier** | Binance retail: 5 bps/side = **10 bps round-trip taker**. Always cost backtests at this rate or worse. |
| **Developer** | Solo. AI-assisted. |
| **Libraries** | Python: scikit-learn, XGBoost, LightGBM, PyTorch (inference), TA-Lib, pandas, numpy. Lightweight others OK. |

### 3.1 Cross-Asset Proxy Pairs

All execution via Freqtrade — that constraint is fixed. Primary exchange Binance, but Freqtrade supports Bybit, OKX, Kraken, Gate.io, etc. Cross-asset candidates (gold, equities, forex) are eligible if a liquid proxy pair (24h volume > $10M) exists on a Freqtrade-supported exchange and tracks the underlying reliably. Tokenized assets can decouple under stress — verify before committing.

| Asset Class | Underlying | Binance Proxy Pair | Notes |
|---|---|---|---|
| Gold | XAU/USD | PAXG/USDT (spot) | No perpetual futures — spot only |
| Forex-like | USD strength | Stablecoin pairs | Very limited liquidity |
| Equity-correlated | Tech/risk-on | BTC/ETH (correlate with NASDAQ in macro regimes) | Indirect |
| Oil/Energy | Crude oil | No direct proxy | — |
| DeFi index | DeFi sector | Various tokens (UNI, AAVE) | Loosely correlated |

---

## 4. Approach Registry

Status key: `ACTIVE` = currently deployed or under iteration · `ARCHIVED` = tried, abandoned, post-mortem written · `PARKED` = shelved with reusable artifacts; reopen only on stated trigger · `CANDIDATE` = identified but not yet built · `INVESTIGATION` = pre-candidate; needs targeted analysis before becoming a candidate

### 4.1 ACTIVE — primary effort allocation per §4.6

#### Liquidation Cascade Strategy (LiqCascade) — v1.0
- **Status:** ACTIVE — Phase 3.6 (Counter-Trend Fade V06 + Sidecar Stall Detection), since 2026-05-02
- **Core idea:** Detect forced liquidation cascades via Binance WebSocket data as primary alpha signal. Regime framework demoted to context filter only (CRISIS gate + EMA200 macro trend).
- **Architecture:** Sidecar (WebSocket liquidation stream + OI polling) → signal file → Freqtrade 5m strategy reads signal → **V05 rides cascade (with-trend)** · **V06 fades cascade (counter-trend)**. ETH+SOL only for V06. 4x/2x leverage.
- **Current deployment:** DigitalOcean droplet, Docker. V05 on port 8082 (5 pairs: BTC/ETH/SOL/BNB/XRP), V06 on port 8083 (2 pairs: ETH/SOL only). Separate DBs. Shared sidecar.
- **Phase plan:** Phase 3 (dry-run) ✓ → Phase 3.5 (OI filter) ✓ → **Phase 3.6 (counter-trend V06)** ACTIVE → Phase 4 (hyperopt, if V06 PF > 1.0) → Phase 6 (live capital, if any variant proves profitable).
- **Phase 3.5 final results (2026-05-02, 752 trades, Mar 17–Apr 19):**
  - Overall: PF 0.488 · WR 39.0% · −$4,789 · Time-stop rate 56.4% (unchanged from Phase 3's 60.7%)
  - Shorts (342): **PF 0.672** · WR 42.7% · −$1,342. Longs (410): PF 0.345 · WR 35.9% · −$3,447
  - Short exits: time_stop 56.4% (0% WR) · roi 40.6% (97.8% WR) · trailing 2.9% (100% WR)
  - **OI filter verdict:** Did not improve results. Week 15 (post-deploy) had worst short PF (0.272) and WR (30.5%)
  - **WebSocket stall:** Binance forceOrder stream silently died Apr 19. Root cause: Binance migrated WebSocket URLs on Apr 23 — `!forceOrder@arr` moved from `/ws` to `/market/ws/`. Sidecar was connecting to legacy URL which no longer serves market data. **Fixed 2026-05-02** (URL updated). Stall detection added (120s watchdog with auto-reconnect).
  - **All 5 pairs negative, all PFs < 1.0.** Do NOT advance to Phase 4.
- **Phase 3.6 (V06 Counter-Trend Fade):** V06 inverts V05's direction: CASCADE_LONG → SHORT, CASCADE_SHORT → LONG. Thesis: cascade overshoots are common; the snap-back is more reliable than the initial direction. Shorter time stop (15 min vs 35). Tighter ROI. Flipped leverage (counter-trend gets 4x). **ETH+SOL only** (best V05 short PF: 0.925, 0.863). No OI filter.
- **Kill criterion:** 50 closed trades with short PF < 1.0 → archive LiqCascade permanently, fold into GatedExecution as gate signal.
- **Repo:** `freqtrade-scalper` (separate) — `strategies/LiqCascadeStrategy_V05.py`, `V06.py`, `sidecar/liquidation_monitor.py`
- **Deep dive:** `LiquidationCascade_Deep_Dive.md` (in `freqtrade-scalper`)

#### OracleSurfer Strategy (v14 PROD)
- **Status:** ACTIVE — v14 deployed 2026-04-06 (dry-run). Pre-dates this Research Log; added retroactively 2026-04-07.
- **Core idea:** FreqAI XGBoost classifier on 4h features predicts 3-class regime (BEAR / NEUTRAL / BULL) using triple-barrier labeling. Entry on Oracle signal + EMA200 trend alignment + RSI momentum + ADX strength gate. Exits via ROI ladder, trailing stop, hard stop. Single pair: BTC/USDT:USDT futures, 1h execution.
- **Architecture:** FreqAI (XGBoost) → `&s_regime_class` → entry filter (EMA200 + RSI + ADX) → Freqtrade execution. 3-year training window, 4h feature timeframe, retrain every 6h live. Features: Choppiness Index, KAMA distance, SMA200 valuation distance, VIX-Fix synthetic fear gauge, OBV oscillator, 5-period ROC.
- **Current deployment:** DigitalOcean droplet (same box as LiqCascade), Docker, BTC/USDT:USDT only, `dry_run: true`. Strategy `OracleSurfer_v14_PROD`. Config `config_sniper_BTC_DryRun.json`. FreqAI identifier `Oracle_Surfer_v12_v2_DryRun`. API port 8080.
- **v12 dry-run results (Feb 22 – Apr 6, 2026, 8 trades):** Win rate 50% · PF 0.31 · Net P&L −8.2%. Exits: 4× trailing SL (+2.98% avg) · 4× hard SL (−10.27% avg). Root cause: asymmetric stop/reward — 50% WR insufficient to break even at this geometry.
- **v12 → v14 structural overhaul (deployed 2026-04-06):** Stop −10% → −5%; ROI ladder added (+10% any time / +7% at 8h / +5% at 16h / +3% at 24h); break-even moved from +3% → +2%; entry tightened (EMA200 + RSI 50± + ADX > 20; MACD removed); Oracle label horizon 96h → 48h with bear priority; DCA disabled; training expanded 1yr → 3yr with regularization; retrain 1h → 6h. Breakeven now at ~40% WR (was ~77%).
- **Go/no-go for v14 continuation:** PF > 1.0, WR > 45% — reassess after **15 closed trades or 2026-07-07**, whichever comes first.
- **Open questions:**
  1. v14 dry-run results — assess WR and PF after structural overhaul
  2. BTC-only vs multi-pair expansion — only after v14 proves profitable
  3. Oracle signal quality at 48h horizon
  4. Should CRISIS gate from LiqCascade be adopted?
- **v5.0 priority:** **#2 effort allocation.** Strategy is pre-existing infrastructure on a slow timer; primary action is monitoring and a single mid-window adjustment if WR < 30% at 8 trades.
- **Repo:** `Freqtrade` (separate) — `user_data/strategies/OracleSurfer_v14_PROD.py`, `user_data/config_sniper_BTC_DryRun.json`

### 4.2 ARCHIVED

#### RAME — Regime-Adaptive Multi-Strategy Ensemble
- **Status:** ARCHIVED (2026-03-17) — needs total rethink if revisited
- **Duration:** ~2 weeks, 17 backtest runs
- **Core idea:** Classify market into 5 regimes (ACTIVE_BULL, ACTIVE_BEAR, QUIET_BULL, QUIET_BEAR, CRISIS) using ATR/ADX/EMA, then route trades to regime-specific sub-strategies.
- **What worked:** 2×2+CRISIS regime framework empirically valid (HMM best_n=5). ACTIVE regime labels have statistically significant 4h directional edge (ETH ACTIVE_BULL p=0.006, BTC QUIET_BEAR p=0.025).
- **Why it failed:** (1) edge too small (+0.087% per 4h, barely above breakeven); (2) consistent late entry; (3) regime indicators oscillate at short TFs; (4) FreqAI classifier was tautological (memorized labels); (5) every exit strategy was destructive (2–24% WR across 9 configs); (6) 2022 bear exposed fatal flaw — short-term "bullish" signals during macro downtrend caused 70–87% of all losses.
- **Salvageable:** regime framework as context filter (not signal generator); EMA200 macro filter (adopted by LiqCascade); CRISIS gate using ATR p90 (adopted by LiqCascade).
- **Deep dive:** `Regime_Adaptive_Ensemble_Deep_Dive.md`

#### LOB Microstructure — CatBoost on Order Flow Features
- **Status:** ARCHIVED (2026-03-20) — signal real, fee structure incompatible at retail rates
- **Source:** arXiv 2602.00776 (Bieganowski & Ślepaczuk, Jan 2026)
- **What worked:** Signal real and paper-replicable. 3s dir_acc 54.2% unconditional, 59.3% top-20% filtered. Spearman IC 0.135 at 3s, decaying to 0.024 at 60s. Feature importance matched paper.
- **Why it failed:** BTC 3s move std = 1.68 bps; Binance retail taker fee = 10 bps round-trip. **6× structural gap.** Threshold sweep across top-50% to top-0.5% × all horizons (3s/5s/15s/60s/300s) → zero profitable operating points. Best case (top-0.5%, 3s): mean |move| = 5.74 bps, net P&L = −8.97 bps/trade.
- **Salvageable:** OFI signal as confirmation filter for LiqCascade entries (Technique 7.3). Reusable infrastructure: 109 days BTC+ETH historical aggTrades.
- **Deep dive:** `LOB_Microstructure_Deep_Dive.md`

#### Cointegration Pairs Trading (CointPairs) — Candidate F
- **Status:** ARCHIVED (2026-03-22) — Phase 1 FAIL
- **Core idea:** Trade mean reversion of log-price spread between major pairs. Single-leg V02 on BNB/ETH @ 4h.
- **What worked:** Hurst H≈0.25 (real mean reversion). Phase 0 fee sweep at 4h showed solid economics. BNB/ETH stable rolling β.
- **Why it failed:** (1) single-leg directional exposure — persistent BNB/ETH directional moves bled the strategy; no fixed stop calibration avoided negative expectancy. (2) 67 trades over 1,400 days = 0.05 trades/day — incompatible with prior frequency objective. **v5.0 NOTE: failure mode #1 (single-leg) is real; failure mode #2 (frequency) would no longer be a kill criterion under the revised §2 frequency objective if multiple spreads were run concurrently. Reconsider as part of GatedExecution synthesis or a portfolio-of-spreads design.**
- **Reusable infrastructure:** `user_data/scripts/cointpairs_phase0_validation.py` (v4) — full diagnostic suite (ADF → EG → Johansen → Hurst → OU half-life → rolling β → fee sweep with time-stop check). Reusable for any mean-reversion candidate.
- **Deep dive:** `CointPairsTrading_Deep_Dive.md`
- **Files:** `user_data/strategies/CointPairsStrategy_V02.py`, `config/config_cointpairs_V02.json`

#### Path Signatures / Lead-Lag (Candidate E)
- **Status:** ARCHIVED (2026-03-23) — Backtest FAIL
- **Core idea:** Level-2 path cross-terms (Chen / Lévy antisymmetry) between leader (BTC) and follower log prices as lead-lag score; enter ETH/SOL long/short with BTC momentum confirmation.
- **Why it failed:** (1) PF ~0.89, ~99% drawdown on long backtest; 315 stop-loss exits ≈ −12% each swamped winners. (2) MVP was directional/unhedged on followers; literature emphasizes market-neutral or portfolio constructions. (3) OOS profitability not demonstrated.
- **Reusable infrastructure:** `Dockerfile.freqtrade`, `config/config_pathsignatures_V01.json`, `docker-compose.pathsignatures.yml`.
- **Deep dive:** `PathSignatureLeadLag_Deep_Dive.md`

#### Candidate M: AdaptiveTrend — Systematic Multi-Pair Momentum
- **Status:** ARCHIVED (2026-04-09) — Phase 0 NO-GO; long-only signal unprofitable across all three iterations
- **Source:** Bui & Nguyen (arXiv 2602.11708) — ROC momentum on 150+ pairs with ATR trailing stop and monthly Sharpe-based pair selection
- **Phase 0 results:**

  | Version | Pairs | Changes | PF | Return | WR | Trades |
  |---|---|---|---|---|---|---|
  | V01 | 15 large-caps | ATR_MULT=3.5 baseline | 0.81 | −42.2% | 31% | ~900 |
  | V02 | 61 pairs | +46 mid-caps | 0.63 | −74.4% | 27.2% | 2,411 |
  | V03 | 57 pairs | EMA(100) + MOM_LOOKBACK 24→72 + ATR-norm + mom exit | 0.69 | −62.2% | 28.0% | 2,639 |

- **Why it failed:** (1) test period bias — 2022–2025 included worst crypto bear; mid/small caps in secular downtrend; (2) universe degraded with expansion; (3) momentum exit signal increased churn; (4) paper's SR 2.41 depends on 150+ pair universe + monthly Sharpe rotation (+1.07 SR ablation contribution).
- **Salvageable:** Short leg V01 produced +26.6% (270 trades). **v5.0 NOTE: this is now treated as INVESTIGATION (§4.4 Candidate N), not a promoted candidate. The +26.6% on 6 pairs over a window dominated by a single −70% bear is consistent with naive short-beta capture, not signal. Regime split required before any further work.**
- **Reusable infrastructure:** `AdaptiveTrendStrategy_V01/V02/V03.py` — ATR trailing stop, concurrent slot management, `_row_at()` pattern.
- **Dev plan:** `AdaptiveTrend_Dev_Plan.md` (ARCHIVED) | **Deep dive:** `AdaptiveTrend_Deep_Dive.md` (ARCHIVED)

### 4.3 PARKED

#### Candidate G: Cross-Sectional Crypto Momentum
- **Status:** PARKED (2026-03-29) — empirically weak after Phase 1 baseline; 7/7 STRONG PASS on prior filter, FAILED in execution
- **Phase 1 result:** V01_1d ~+17% full-sample 2022–2025 but unstable by year (+71% / +14% / −40% calendar slices); 4h grid and long-only NO-GO.
- **Reopen triggers (preserved):** named add-on addressing a documented weakness (regime breakdown, funding-aware simulation, narrower universe, vol-targeted risk layer, external filter, validated new ranking signal); OR new data/constraints change the test (different venue, fee tier, mandate). Do NOT reopen for unfocused hyperopt.
- **v5.0 NOTE:** infrastructure (cross-pair ranking via `DataProvider` + `custom_info`) is the most reusable piece for the GatedExecution synthesis (§4.5).
- **Files retained:** `XSMomentumStrategy_V01.py`, `config_xsmom.json`, `CrossSectionalMomentum_*.md`

#### Candidate J: Ensemble Donchian Trend-Following
- **Status:** PARKED (2026-04-06) — Phase 0 NO-GO on fee-inclusive Freqtrade backtests; 7/7 STRONG PASS on prior filter, FAILED in execution
- **Phase 0 outcome:** Regime splits and full-sample strongly negative under realistic per-side fees (`--fee 0.0005`); ATR trailing worse than Donchian-lower; higher entry thresholds did not clear PF / go-forward bars. See `user_data/results/donchian_phase0_sweep_20260406_105346.md`.
- **Reopen triggers:** new hypothesis with different universe, filters, or execution assumptions; fresh Phase 0 charter.
- **v5.0 NOTE:** the failure pattern (fee-inclusive multi-pair trend-following at hourly TF gets crushed by transaction costs) is data — incorporated into §6.2 deflation pass.
- **Files retained:** `EnsembleDonchianStrategy_V01/V02`, `config_donchian.json`, `user_data/scripts/donchian_phase0_sweep.py`, sweep artifacts.

#### Candidate L: Enhanced Cointegration Pairs Trading (with adaptive trailing stop + vol filter)
- **Status:** PARKED (2026-05-02) — **§6.2 Edge Deflation Pass completed 2026-05-03; verdict reached.** Spread/z-score signal is real but does not clear §6.2.6 standalone thresholds. **Verdict: option (a) — fold spread/z-score signal into §4.5 GatedExecution as a sub-signal.** Dev Plan FROZEN; Deep Dive Part 8 is the canonical worksheet.
- **Source:** Palazzi (Journal of Futures Markets, Aug 2025) — adaptive trailing stop + vol filter on cointegrated crypto pairs (peer-reviewed). Also Tadi & Witzany (Financial Innovation, 2025) — copula-based pairs on Binance Futures.
- **§6.2 deflation outcome (2026-05-03):**
  - **Palazzi 2025:** Input portfolio Sharpe 0.89 (per §6.2.5 explicit instruction; 13/37 OOS-positive). After 0.5 decay + fee tier downgrade + slippage + regime weighting → deflated return **~3–5%/yr**, deflated Sharpe **~0.20–0.30**. **FAIL §6.2.6** (need >25% return, Sharpe >1.0).
  - **Tadi & Witzany 2025:** Inferred input Sharpe ~1.1. After deflations + softer (1/N)^0.3 selection penalty for weekly re-selection → deflated return **~3–5%/yr**, Sharpe **~0.30–0.40**. **FAIL §6.2.6.**
  - Both papers **FAIL §6.2 standalone**. Both refer to GatedExecution per §6.2.6 last bullet ("discrete signal that could plug into GatedExecution").
- **Empirical cross-check (forward droplet 2026-05-02):** 35% of paper's pairs OOS-positive (13/37); our forward replicas were 33% positive (1/3 spreads × 2 versions = BTC/ETH only) — within sampling noise. Direct confirmation that pair selection within the universe dominates strategy variant, and that deflation is correctly calibrated. Aggregate PnL **~+0.01%** vs sum of stakes; **17** closed trade rows (below §2 50-trade bar). BTC/ETH replicas ~+4.2% each; BNB/SOL and BTC/SOL replicas negative.
- **Lab vs forward split (preserved):** Lab walk-forward on **BTC/ETH @ 4h** retained positive headline economics for **V01/V02 defaults** (see `user_data/results/cointpairs_comparison_tables.md`). Forward 6-process test did **not** validate standalone capital deployment.
- **Reopen trigger (post-verdict):** This candidate reopens **only** if (i) GatedExecution Dev Plan v0.1 explicitly rejects the spread/z-score gate (then revisit option b portfolio-of-spreads with held-out pairs), OR (ii) a §6.2 deflation pass on a *new* paper materially changes the deflated economics. Open-ended hyperopt or "one more droplet month" remain **invalid** triggers.
- **What carries forward into §4.5 GatedExecution:** Spread/z-score signal source `{direction, confidence, freshness}` per pair per candle, computable from `EnhancedCointPairsStrategy_V01.py` logic in a sidecar (no per-pair Freqtrade processes needed). Per-pair calibration is mandatory (naive multi-pair Phase 0 GO inheritance failed forward). Adaptive trailing stop + vol filter (Palazzi options) are **not** carried forward — lab demonstrated they reduce P&L; superseded by GatedExecution unified exit.
- **Deploy / ops:** Droplet forward tests **stopped by policy 2026-05-02**; repo **`freqtrade-coint-pairs-trading`** retained for reproducibility and historical logs. Strategy files retained as reference implementation for spread/z-score signal computation only.
- **Historical checkpoints:** 2026-04-18 combined snapshot ≈ −1.72%, 12 closed / 8 open legs — `freqtrade-coint-pairs-trading/TESTING.md`. Final 2026-05-02 combined snapshot **12** open legs, **17** closed trade rows. **2026-05-03:** §6.2 deflation completed; verdict (a) GatedExecution sub-signal; Dev Plan FROZEN. See `EnhancedCointPairs_Deep_Dive.md` Part 8.

### 4.4 CANDIDATES & INVESTIGATIONS

*Candidates and investigations below have NOT yet cleared the full v5.0 multi-stage gate (§6) for promotion to ACTIVE. All require §6.1 + §6.2 + §6.3 before new capitalized build effort.*

#### Candidate N: ShortBias Momentum — ARCHIVED (2026-05-02)
- **Status:** ARCHIVED — failed step 3 of the §4.4 investigation procedure. Signal confirmed as short-beta capture.
- **Origin:** AdaptiveTrend (M) Phase 0 — short leg of V01 produced +26.6% over 2022–2025 across 6 large-cap pairs.
- **Investigation results (AdaptiveTrendStrategy_V01_ShortOnly, ATR_MULT=3.5, 6h, 0.05% fee, 6 pairs):**

  | Year | Trades | PF | Return | Sharpe | WR | MDD | Market Δ | Short BnH | Spread |
  |------|--------|-----|--------|--------|-----|------|-----------|-----------|--------|
  | 2022 | 125 | 1.65 | +77.55% | 1.28 | 48.8% | 25.88% | −74.52% | +74.52% | **+3.03pp** |
  | 2023 | 111 | 0.57 | −28.78% | −1.28 | 36.9% | 30.44% | +255.96% | −100% | +71.22pp |
  | 2024 | 112 | 0.94 | −3.70% | −0.13 | 40.2% | 20.09% | +91.73% | −91.73% | +88.03pp |

- **Why it failed:** 2022 spread = +3.03pp — below the +5pp threshold. The headline +77.55% return in the one year shorting worked was 96% beta capture. The momentum filter (ROC < −3%) provides real edge in bull years by preventing suicidal shorts, but that is a basic trend filter, not a novel signal. In bear markets — the regime where short alpha must prove itself — the strategy barely beat passive short.
- **Lesson reinforced:** §9 #16 — backtest sub-leg artifacts are not new candidates. The v5.0 audit's prediction was exactly correct.
- **Reusable:** `AdaptiveTrendStrategy_V01_ShortOnly.py` (strategy), `config_adaptivetrend_shortonly.json` (config). Both retained for reproducibility.

#### Candidate O: EMA50 × YTD Anchored VWAP Crossover — REJECTED (2026-05-02)
- **Status:** REJECTED — failed §6.1 Buildability Filter (4/7) + Phase 0 empirical NO-GO.
- **Source:** YouTube video (not academic). Prompts Claude to generate Pine Script for EMA(50) × YTD Anchored VWAP crossover with swing-level stops.
- **§6.1 score:** 4/7 — FAIL (no OOS evidence, no structural mechanism, no complementarity).
- **Phase 0 quick-test (V01, 4h, 0.05% fee, 5 pairs: BTC/ETH/BNB/SOL/XRP):**

  | Period | Trades | PF | Return | Sharpe | WR |
  |--------|--------|-----|--------|--------|-----|
  | 2022 | 20 | 0.50 | −1.16% | −0.24 | 55.0% |
  | 2023 | 38 | 0.71 | −0.84% | −0.15 | 42.1% |
  | 2024 | 42 | 0.57 | −2.27% | −0.38 | 45.2% |
  | Full | 140 | 0.75 | −3.10% | −0.14 | 47.1% |

- **Why it failed:** Negative every year, no favorable regime. Short side −7.18% vs long +4.08% — YTD VWAP drifts upward in crypto's secular uptrend, making downside crossovers false signals. 140 trades / 4 years across 5 pairs = ~0.1/day — frequency rounding error. Market did +27.77%, strategy lost −3.1%.
- **Lesson:** "Institutional breakeven" anchored VWAP narrative is retail folklore, not alpha. The signal is functionally a slow MA crossover — a well-studied class with poor standalone profitability at retail fees.
- **Reusable:** `EMAVWAPStrategy_V01.py`, `config_emavwap.json`. Retained as reference/anti-pattern.

#### Candidates B, C, D, H, I, K — preserved status
- **B (Funding Rate Arbitrage):** PARKED — non-Freqtrade infrastructure; lower ROI than active candidates. Status unchanged; reconsider as a carry sleeve under GatedExecution if a 2-leg sidecar is built.
- **C (Volatility Commonality Forecasting):** Reclassified as Technique (§7) — vol-timing layer.
- **D (CNN Trend / Stationarity Preprocessing):** Reclassified as Technique (§7.2 — fractional differentiation already covers most of this).
- **H (On-Chain Whale Flow):** Reclassified as Technique (§7.4) — macro filter.
- **I (Path Signature-Enhanced Momentum):** RESERVED — prerequisites unchanged; unlikely under v5.0 unless surfaces as a discrete signal layer in GatedExecution.
- **K (Multi-Timeframe Trend Confirmation):** Filter/enhancement — not standalone. Eligible as a gate signal in GatedExecution.

### 4.5 SYNTHESIS INITIATIVE — GatedExecution

**Thesis (v5.0):** The pattern of repeatedly drawing standalone candidates from the literature has produced 0 wins in 7 attempts. Several of those failed candidates produced *partial* validated signals or reusable infrastructure that, individually, do not meet the bar for a deployed strategy but, **combined**, may form a robust edge. The next significant build effort should be a synthesis layer, not the next standalone paper.

**Concept:** A single Freqtrade execution layer that consumes signals from multiple gated sources, takes a trade only when ≥ N gates agree, and uses a unified risk/exit framework.

**Candidate signal sources (drawn from validated/partially-validated work in the registry):**

| Source | Signal | Status | Origin |
|---|---|---|---|
| **Cascade detection** | LiqCascade sidecar event stream | VALIDATED (real signal, refining selectivity) | LiqCascade Phase 3.5 |
| **Cross-sectional rank gate** | Top-N momentum / bottom-N anti-momentum from XSMomentum infrastructure | PARTIAL (signal weak standalone, real as a gate) | Candidate G code retained |
| **Funding extreme gate** | Block longs / favor shorts when funding >90th percentile rolling 30d | RESEARCH | Technique 7.4 (Inan SSRN 5576424) |
| **Macro EMA200 gate** | Block long entries below daily EMA200; block shorts above | VALIDATED | RAME → LiqCascade |
| **CRISIS gate (ATR p90)** | Block all entries when realized vol > 90th percentile | VALIDATED | RAME → LiqCascade |
| **OI confirmation** | OI change rate > threshold (per-pair calibrated) | VALIDATED on shorts (XRP/BNB/ETH/SOL) | LiqCascade Phase 3.5 |
| **OFI confirmation (optional)** | LOB order flow imbalance agrees with entry direction | RESEARCH (real signal, fee-incompatible standalone) | Candidate A salvage |
| **Conformal prediction wrapper** | Tighten entries when prediction interval is narrow and one-sided | RESEARCH | Technique 7.1 |
| **Pairs spread / z-score (mean reversion)** | Per-pair signal: `{direction, confidence ∝ \|z\| above entry, freshness}`. Per-pair calibration mandatory (forward 1/3 positive replicas). | **CONFIRMED gate (2026-05-03)** — §6.2 deflation FAIL standalone (~3–5%/yr post-deflation), 35% OOS-positive across paper universe matches our 33% forward survival; refer per §6.2.6 | Candidate L §4.3, Deep Dive Part 8 |

**Architecture sketch:**
- Each signal source produces a normalized output: {direction, confidence, freshness}.
- A `GatedExecutionStrategy` Freqtrade strategy reads the union of signal files / DataFrames per pair per candle.
- Configurable gate combination: `min_agreeing_gates`, per-gate `weight`, per-gate `mandatory` flag (e.g., CRISIS gate is always mandatory).
- Unified exit: ATR-based trailing stop + ROI ladder + time stop (already proven in LiqCascade and OracleSurfer).
- Single risk model: position sizing inverse to realized vol; per-pair max concurrent trades; portfolio max heat.

**Why this is structurally different from RAME:**
- RAME used regime *labels* as the primary signal generator. GatedExecution treats every input as a *gate*, never a primary signal. Trades only fire when the *intersection* of independent gates agrees. This is a fundamentally different statistical assumption — gates kill false positives multiplicatively; signal generators add noise additively.
- RAME tried to learn a regime classifier. GatedExecution uses no learned classifier; every gate is a transparent rule with explicit thresholds.

**Why this is not the next thing to build:**
- Premature. Until LiqCascade clears Phase 4 (PF > 1.0), its cascade detection is not yet a validated signal — it is a *promising* signal under refinement.
- Sequencing: LiqCascade Phase 4 GO/NO-GO → if GO, GatedExecution becomes the natural extension and incorporates the cascade signal as the primary gate. If NO-GO, GatedExecution's primary gate must come from another validated source, which materially changes the design.
- Read at next decision: see §4.6 priority sequencing.

**First Dev Plan trigger:** When LiqCascade Phase 4 returns either a clean GO or a clean NO-GO with a clear successor signal candidate. Estimated calendar: late April to mid-May 2026.

### 4.6 Effort Allocation & Priority Ranking (v5.1)

**The 70/30 rule:** Until at least one ACTIVE strategy clears its go/no-go gate (LiqCascade Phase 4 OR OracleSurfer 15-trade gate), allocate effort as:
- **70%** to iterating on ACTIVE strategies (LiqCascade > OracleSurfer)
- **30%** to candidate evaluation, deflation passes, and the GatedExecution design

**Sequenced priorities (do in order, do not parallelize):**

> **Next actionable session work: step 5 (GatedExecution Dev Plan v0.1).** Steps 1–2 are passive monitoring; step 3 complete (v5.1, 2026-05-03); step 4 complete (2026-05-03 — verdict reached). Step 6 (Sweep #6) is queueing-gated behind step 5 per §5.6.

1. **LiqCascade Phase 3.6** (passive, 2–3 week soak). V06 counter-trend deployed 2026-05-02 alongside V05 on droplet. Reassess at 50 closed trades or ~2026-05-16. Kill criterion: short PF < 1.0 → archive permanently.

2. **OracleSurfer v14 monitoring** (passive, ongoing). At 8 closed v14 trades, mid-window check: if WR < 30%, pause and diagnose. Otherwise continue to 15-trade gate.

3. **✓ DONE (v5.1, 2026-05-03) — §6.5 filter precision touch-up.** Acknowledged that v5.0 gates correctly rejected O (§6.1, 4/7) and correctly archived N investigation (§4.4 step 3) at low cost. See §6.5 v5.1 note.

4. **✓ DONE (2026-05-03) — Deflation pass on Candidate L (PARKED).** Forward droplet experiment concluded 2026-05-02. §6.2 worksheets on Palazzi 2025 and Tadi & Witzany 2025 completed in `EnhancedCointPairs_Deep_Dive.md` Part 8. Both papers **FAIL §6.2.6 standalone** (~3–5%/yr post-deflation). **Verdict: option (a) — fold spread/z-score into §4.5 GatedExecution as sub-signal.** Dev Plan FROZEN; §4.5 table updated; §6.5 filter-precision row to be added below.

5. **← NEXT — GatedExecution Dev Plan v0.1 — skeleton draft** (1–2 sessions). Draft the structural design now: signal interface contract, gate combination logic (`min_agreeing_gates`, weights, mandatory flags), unified risk/exit framework, position sizing model. **Now includes spread/z-score gate explicitly** per step 4 verdict. Leave the *primary-signal* slot as a placeholder (resolves on LiqCascade Phase 4 outcome). Independent of which specific signal becomes primary — slots in cleanly when LiqCascade resolves.

6. **Sourcing Sweep #6** (1 session, eligible 2026-05-19 per original §4.6 trigger; may run earlier under v5.1 protocol if steps 3–5 complete). Run under the revised §5 / §5.6 v5.1 protocol — three narrow targeted gaps (structural alpha, gate-shaped signals, capital-efficiency overlays). **Hard constraint:** any candidate produced is queued for §6.2 deflation only; no implementation work begins until step 1 (LiqCascade Phase 4) resolves. This breaks the historical pattern where each sweep produced an immediate new #1 priority (J → M → L), all of which subsequently failed.

7. **LiqCascade Phase 4 resolves** (passive trigger). Outcome determines step 8.

8. **GatedExecution Dev Plan finalized + highest-priority §6.2-passing candidate from Sweep #6 enters deflation.** If LiqCascade GO: cascade detection becomes primary signal in GatedExecution. If LiqCascade NO-GO: the highest-conviction Sweep #6 candidate (likely a structural-alpha source per §5.6) is evaluated for the primary-signal slot.

*This ranking reflects the state of knowledge as of **2026-05-03** (v5.1 sourcing protocol restructure). Update after every checkpoint outcome.*

---

## 5. Sourcing Configuration

**v5.0 cadence change (retained):** Prior pattern was ~1 sweep every 1–2 weeks producing many candidates (28+ total in 4 sweeps), with low conversion to live edge. Cadence now: at most one sweep per 6 weeks of calendar time, OR triggered by an active-strategy phase outcome. Each sweep targets a specific gap, not a broad scan.

**v5.1 sourcing-bias change (new):** The v5.0 multi-stage gate is correctly *rejecting* weak candidates (Candidate O at §6.1, Candidate N at investigation step 3 — both low-cost rejections). The remaining problem is **upstream**: every candidate F through M came from broad academic / practitioner sweeps with novelty bias, and the resulting archetypes (paper-replicated single-strategy directional or quasi-directional models, hourly-to-daily TF, liquid crypto, retail fees) have a 0/7 win rate. Lesson #17 is now data: continuing to draw from the same distribution under the same novelty bias has poor base-rate conversion at our fee tier.

**v5.1 narrows sourcing along three structural axes derived from the project's own evidence:**

1. **Structural-alpha sources.** Lesson #3 (structural alpha > statistical alpha) is the highest-conviction empirical principle in this log. The only candidate in our registry built on a *why* before a *how* — LiqCascade, on forced liquidations — is also the only one currently producing real-time validation data, even if PF < 1.0. v5.1 explicitly biases sourcing toward terrain with a structural reason for the edge to exist that does not depend on competing on latency or being smarter than other quants. Examples: forced flows (ETF rebalances, perp funding payments, options expiry / dealer hedging), information-asymmetry events (token unlocks, exchange listings, scheduled airdrops, governance votes), carry / basis (perp-spot basis, calendar spreads), and microstructure dislocations that aren't latency-bound.

2. **Gate-shaped signals for §4.5 GatedExecution.** Given that GatedExecution is the highest-leverage architectural bet on the board, signals that *reduce false positives* in an existing primary signal (LiqCascade or its successor) are higher-value to this project than the next standalone candidate. v5.1 explicitly admits "gate-shaped" signals as a sourcing target: directional-bias filters, regime confirmation, false-positive reduction methods, and extreme-value contrarian indicators.

3. **Capital-efficiency / portfolio-construction overlays.** The registry has zero candidates built around portfolio construction, vol-targeting, dynamic hedging, or correlation-aware risk allocation. These have a structurally different failure surface than signal-discovery candidates because they don't depend on being right about direction — they multiply whatever edge a base strategy produces. Vol-targeting alone is well-documented as roughly doubling risk-adjusted returns of any base strategy. This is unexplored terrain in our project.

**What v5.1 does NOT change:**
- The source venues themselves (SSRN, arXiv, Quantpedia, practitioners) are correct. The problem was search terms and per-paper rigor, not where to look.
- The novelty bias is preserved *in principle*, but redefined: novel **to our stack and fee tier** rather than novel to academic literature. A 10-year-old vol-targeting overlay never tried in our configuration is more novel-to-us than the next path-signatures paper.
- §6 multi-stage gate is unchanged. v5.1 only changes what flows into §6.1.

### 5.1 Primary Sources

| Source | Type | Access | Focus |
|---|---|---|---|
| **SSRN** | Academic preprints | Free | Novel quantitative strategies, financial ML |
| **arXiv (q-fin)** | Academic preprints | Free | ML/DL applied to markets |
| **Quantpedia blog** | Strategy database | Free tier (~70 strategies). Premium $599/yr unlocks 900+ with OOS backtests + Python code. Recommend subscribing before Sweep #6 if not already. | Academic strategies → trading rules |
| **Oxford-Man Institute** | Academic research | Newsletter + public papers | ML for quant finance, microstructure |

### 5.2 Applied / Practitioner Sources

| Source | Type | Access | Focus |
|---|---|---|---|
| **QuantStart** | Blog + courses | Free blog | Practical implementation, Python, backtesting |
| **Robot Wealth** | Blog + community | Free blog | Practical retail quant, fee-aware analysis, crypto |
| **The Quant's Playbook** (Substack) | Newsletter | Free + paid | Accessible strategy breakdowns, code |
| **r/algotrading, r/quant** | Forums | Free | Practitioner reality checks |
| **QuantConnect community** | Forums + shared strategies | Free | Implemented strategies with backtests |
| **Freqtrade Discord / GitHub** | Community | Free | Freqtrade-specific strategies |
| **QuantInsti / Quantra** | Blog + courses | Free blog | End-to-end walkthroughs |

### 5.3 Secondary Academic Sources

| Source | Type | Access | Focus |
|---|---|---|---|
| **IEEE Xplore** | Peer-reviewed journals | Abstracts free | Signal processing, neural architectures |
| **Journal of Financial Data Science** | Peer-reviewed | Some open access | ML in finance |
| **Quantocracy** | Aggregator | Free | Curates quant blog posts |

### 5.4 Reference Literature

| Book | Author | Relevance |
|---|---|---|
| Advances in Financial Machine Learning | López de Prado | Foundational. Fractional diff, meta-labeling, triple barrier, purged CV |
| Machine Learning for Algorithmic Trading | Stefan Jansen | Practical companion to de Prado |
| Algorithmic Trading: Winning Strategies | Ernest P. Chan | Mean reversion, momentum, Kalman, regime |
| Python for Finance | Yves Hilpisch | Python coding reference |
| Trading and Exchanges | Larry Harris | Market microstructure |

### 5.5 Search Terms (v5.1 — reorganized around three structural axes)

**Legacy generic terms (retained for reference / non-targeted exploration):** `algorithmic trading strategy`, `crypto trading ML`, `systematic trading`. These are now low-priority — they produced our archived archetype.

**Axis A — Structural-Alpha Sources (priority for Sweep #6):**
- Forced flows: `ETF rebalance crypto`, `liquidation cascade`, `forced selling crypto`, `perpetual funding payment flow`, `options expiry hedging crypto`, `dealer gamma hedging crypto`
- Information-asymmetry events: `token unlock trading`, `exchange listing alpha`, `scheduled airdrop trading`, `governance vote trading`, `vesting cliff crypto`
- Carry / basis: `perpetual basis arbitrage`, `funding rate carry crypto`, `calendar spread crypto futures`, `cash-and-carry crypto`, `term structure crypto`
- Microstructure dislocations (non-latency): `cross-venue stablecoin spread`, `funding rate overshoot`, `perp-spot dislocation crypto`

**Axis B — Gate-Shaped Signals for GatedExecution:**
- `false positive reduction trading signal`
- `directional bias filter crypto`
- `regime confirmation gate`
- `funding rate predictive signal`
- `liquidation prediction model`
- `whale flow directional filter`
- `volatility regime classifier`
- `crisis detection crypto`
- `extreme value contrarian indicator`

**Axis C — Capital-Efficiency / Portfolio Overlays:**
- `vol targeting crypto`
- `dynamic hedging perpetual futures`
- `correlation-aware position sizing`
- `risk parity crypto portfolio`
- `Kelly criterion crypto sizing`
- `drawdown control overlay`
- `meta-strategy portfolio construction`
- `regime-conditional sizing`

**Architecture-specific (retained from v5.0, now lower priority):** `state space model trading`, `temporal fusion transformer finance`, `reinforcement learning trading`, `hawkes process order flow`, `path signatures trading`, `rough path finance`. These are technique terms that produced E (archived), J (parked), among others. Use only if a paper combines them with structural-alpha framing per Axis A.

**Technique-specific (retained):** `mean reversion crypto`, `momentum strategy ML`, `volatility forecasting`, `funding rate strategy`, `market microstructure alpha`, `conformal prediction trading`, `fractional differentiation trading`. Treat as confirmation terms only — do not source new candidates from these as primary terms (this terrain is the archetype with 0/7 win rate).

**Meta/methodology (retained, always relevant):** `backtesting pitfalls`, `walk-forward validation trading`, `overfitting trading strategies`, `synthetic data augmentation finance`, `transaction cost analysis crypto`, `deflated sharpe ratio`, `multiple testing corrections trading`

### 5.6 Sourcing Sweep Protocol (v5.1)

Each sweep MUST:

1. **Cover all three v5.1 axes** (§5 introduction): Axis A (structural alpha), Axis B (gate-shaped signals), Axis C (capital-efficiency overlays). Allocate ~5 papers per axis. Total ≤ 15 papers reviewed in detail. A sweep that produces zero candidates from one or more axes is acceptable (rejection is a valid outcome) but the *search effort* must cover all three.

2. **State the specific gap being targeted within each axis** (one paragraph per axis; what kind of strategy or signal, why now, what would clear §6.2).

3. **Per-axis hit-rate calibration.** State expected hit rate per axis: of the candidates surfaced, how many will likely pass §6.2 Edge Deflation Pass? If the honest answer is "all of them," recalibrate — that's the sycophancy failure mode (§1).

4. **For every promoted candidate, populate §6.3 Paper Replication Checklist at sweep time, not later.** Without this, the candidate does not count as "surfaced" — only "noted."

5. **Hard queueing constraint (v5.1):** Any candidate produced by a sweep is queued for §6.2 deflation only — **no implementation work begins until current ACTIVE strategies have resolved their go/no-go gate**. This breaks the historical pattern where each sweep produced an immediate new #1 priority (J → M → L), all of which subsequently failed. The sweep's deliverable is *queued, deflation-ready candidates*, not "what to build next."

6. **End with a single co-investigator recommendation per axis** (which one — or none — to advance from each axis), plus a cross-axis ranking if multiple advance. Recommendations must be honest about expected post-deflation survival.

**v5.1 sweep template (use for Sweep #6 and beyond):**

| Axis | Target gap | Search terms (from §5.5) | Papers cap | Expected §6.2 survivors |
|---|---|---|---|---|
| A — Structural alpha | [specific gap, e.g., "options expiry / dealer hedging flow on BTC"] | [3–5 terms from Axis A list] | 5 | [honest estimate] |
| B — Gate-shaped signals | [specific gap, e.g., "directional bias filters complementary to LiqCascade"] | [3–5 terms from Axis B list] | 5 | [honest estimate] |
| C — Capital efficiency | [specific gap, e.g., "vol-targeting overlay implementable in Freqtrade"] | [3–5 terms from Axis C list] | 5 | [honest estimate] |

**§6.5 feedback loop (v5.1):** After each sweep concludes and its candidates have been through §6.2, update the filter precision table per-axis. If one axis is producing all the survivors and another is producing none across two sweeps, adjust axis weighting in the next sweep. If all three axes produce zero §6.2-passing candidates across two sweeps, escalate to §6.6 workflow kill criterion.

---

## 6. Evaluation Process (v5.0 — multi-stage gate)

**Why this exists in this form:** Under v4.x, the 7-point filter alone gated implementation. Empirically (4 evaluated candidates: G STRONG PASS → fail, J STRONG PASS → fail, M PASS → fail, L PASS → not yet attempted) it has 0 confirmed wins. The filter scored buildability and literature plausibility; it did not score replicable edge at our fee tier in our forward conditions. v5.0 splits the gate into stages, each scoring something different, all required to pass.

**Order of gates:**
1. §6.1 Buildability Filter — necessary; rejects infeasible candidates cheaply
2. §6.2 Edge Deflation Pass — necessary; rejects optimistic literature claims at our actual conditions
3. §6.3 Paper Replication Checklist — diagnostic; surfaces hidden assumptions
4. §6.4 Phase 0 fee-economics + regime-split backtest — empirical
5. §6.5 Filter Precision Tracking — meta-process; track our own gate accuracy and update gates accordingly
6. §6.6 Workflow Kill Criterion — when to revise the process itself

### 6.1 Stage 1 — Buildability Filter (7 points)

*Necessary, NOT sufficient. A candidate that fails this stage is rejected. A candidate that passes proceeds to §6.2; passing here does NOT mean "approved to build."*

| # | Criterion | Question | Pass/Fail |
|---|---|---|---|
| 1 | **Data availability** | Can I get the required data free or cheaply via Binance / CCXT / public sources? | |
| 2 | **Compute fit** | Can it run inference on a standard VPS (no GPU)? Training in < 24h on a local machine? | |
| 3 | **Freqtrade compatibility** | Implementable as a Freqtrade strategy (with or without FreqAI)? | |
| 4 | **Out-of-sample evidence** | Has someone shown OOS or walk-forward results — not just in-sample? | |
| 5 | **Clear mechanism** | Is there a plausible structural / behavioural / informational reason this edge exists? | |
| 6 | **Complementarity** | Different market condition or alpha source than what's already Active / Paused? | |
| 7 | **Implementation scope** | Working backtest in ≤ 1 week of Cursor + Claude development time? | |

**Threshold:** ≥ 5/7 to advance to §6.2.

**Red flags (auto-reject or investigate further):**
- In-sample only with no holdout
- Requires tick / Level 2 data not in standard Binance API
- Core alpha depends on sub-second latency
- Equities-only with no crypto evidence
- Accuracy metrics without P&L connection (RAME lesson)
- Continuous GPU inference

### 6.2 Stage 2 — Edge Deflation Pass (mandatory, v5.0)

*Apply the following deflations to the paper's headline results before the candidate is allowed to proceed to a Dev Plan. If after deflation the candidate still meets the bar in §6.2.5, advance. Otherwise reject or refer to §4.5 GatedExecution as a sub-signal.*

#### 6.2.1 Sharpe / return decay
- **Default decay factor: 0.5** (Falck & Rej 2022 — average post-publication Sharpe halves; the Palazzi 2025 paper itself cites this).
- Apply: `deflated_sharpe = paper_sharpe × 0.5`, `deflated_return = paper_return × 0.5`.
- Override only with documented reason (e.g., paper uses out-of-sample period that ends ≥ 12 months before publication AND covers a full bull/bear cycle).

#### 6.2.2 Fee tier downgrade
- If paper uses fees < 8 bps round-trip, recompute with our 10 bps. For high-frequency strategies (avg hold < 1h) where fees dominate, this typically multiplies losses 2-3×.
- Specifically: estimate paper's fee assumption, compute `fee_delta = our_fee - paper_fee`, then `our_net_return ≈ paper_net_return - fee_delta × turnover_bps_per_year / 10000`.

#### 6.2.3 Slippage layer
- Add **2 bps round-trip slippage** for liquid pairs (BTC, ETH); **5 bps** for liquid alts (SOL, BNB, XRP, ADA, AVAX, LINK); **15 bps** for mid-caps; **30+ bps** for small-caps. If paper trades small-caps, the slippage adjustment alone often inverts the sign of the result.

#### 6.2.4 Regime weighting
- Paper test windows often end pre-2022 or use favorable selections. Re-weight returns by an expected forward-regime mix:
  - 33% bear-similar conditions (analogous to 2022)
  - 34% sideways-with-chop (analogous to 2023)
  - 33% bull-with-corrections (analogous to 2024–2025)
- Compute `weighted_return = Σ regime_weight_i × paper_return_in_regime_i`. If the paper does not report regime splits, mark this as ⚠️ and require a Phase 0 regime-split backtest before any Dev Plan effort.

#### 6.2.5 Selection bias adjustment
- If paper reports best-of-N across pairs / parameter sets, multiply the headline metric by `(1/N)^0.3` as a rough penalty (this approximates a multiple-testing correction without requiring a formal deflated-Sharpe calculation).
- If the paper uses parameter optimization on the test window without out-of-sample validation, treat as in-sample-only and reject.
- For Palazzi 2025 specifically: 37 pairs evaluated, 35% (13 pairs) OOS-positive — the headline Sharpe is the single best survivor. Use the **portfolio average Sharpe (0.89) not the single-pair Sharpe (2.12)** as the input to deflation.

#### 6.2.6 Pass threshold
- After all deflations: if **deflated annual return > 25% AND deflated Sharpe > 1.0 AND deflated MDD < 30%**, advance.
- These thresholds are deliberately above what most papers can clear post-deflation. That is the point. We have already proven we can build candidates that fail; the bar must select for survivors.
- If a candidate fails this stage but has a discrete signal that could plug into GatedExecution (e.g., a directional bias gate, a vol filter), refer it there rather than archiving.

### 6.3 Stage 3 — Paper Replication Checklist (mandatory)

*Populate this for every candidate clearing §6.2. Surfaces hidden assumptions before any code is written. Many failures (LOB fee tier, M selection bias, J ensemble fee assumption) would have been caught here.*

| # | Question | Source / Note |
|---|---|---|
| 1 | What exact fee tier does the paper assume? Per-side or round-trip? | Quote the paper's number |
| 2 | What exact data window? Does it include 2022 bear? 2024–2025 bull? | Cite dates |
| 3 | Is the universe survivorship-biased? (e.g., "top 20 by current market cap" includes only survivors) | Verify |
| 4 | Are entry/exit times daily-close-to-daily-close, or accounting for slippage and execution latency? | Critical for HF |
| 5 | What's the parameter optimization protocol? In-sample, walk-forward, or test-window? | Reject test-window-fitted |
| 6 | What's the reported MDD definition? Peak-to-trough on returns or on equity? | Standardize before comparison |
| 7 | Does the paper report regime splits (bull / bear / sideways)? If not, demand a Phase 0 regime-split test | Mandatory if missing |
| 8 | Is there a single "best" parameter set or "best" pair selection? If yes, what's the dispersion across the universe? | Selection bias check |
| 9 | What's the live / forward-test track record (post-publication)? | If none, deflate further |
| 10 | What infrastructure does the paper assume (low-latency, prime broker, custom matching)? | Reject if non-Freqtrade-compatible |

**Output:** a 1-page summary per candidate, attached to the Dev Plan.

### 6.4 Stage 4 — Phase 0 Empirical Gate

*Phase 0 is empirical, not just literature. Standard structure:*

1. **Fee-economics sweep** (Technique 7.3) — already mandatory; v5.0 unchanged.
2. **Regime-split backtest** — mandatory under v5.0. Each calendar year (or each 6-month window if data permits) reported separately. Strategy must clear PF > 1.0 in ≥ 2 of 3 years to advance to Phase 1. Ensemble averages over the full window can mask collapsed years (RAME bull-only failure mode; M long-side; G calendar instability).
3. **Per-pair PF distribution** — if multi-pair, report PF per pair. If < 50% of pairs exceed PF 1.0, the strategy is selection-biased to the best subset (M lesson).
4. **Buy-and-hold benchmark** — strategy net return must exceed buy-and-hold of the relevant universe over the same window by ≥ 5% absolute. If not, the "edge" is beta capture (Candidate N investigation).

### 6.5 Stage 5 — Filter Precision Tracking

*Track the empirical accuracy of our own gates. Update the gates when precision is poor.*

**Definitions:**
- A candidate is a **filter PASS** if it cleared the prior 7-point evaluation filter (v4.x) OR the v5.0 multi-stage gate (§6.1 + §6.2 + §6.3).
- A candidate is a **live WIN** if it reached ACTIVE status with a documented forward-test PF > 1.0 over ≥ 50 closed trades.

| Candidate | Filter version | Filter score | Phase 0 outcome | §6.2 deflation | Live status | Win? |
|---|---|---|---|---|---|---|
| F (CointPairs) | v4.0 | 6/7 + 1 cond | Phase 1 FAIL | (pre-§6.2) | ARCHIVED | NO |
| E (Path Sigs) | v4.0 | 6/7 + 1 cond | Phase 1 FAIL | (pre-§6.2) | ARCHIVED | NO |
| G (XSMomentum) | v4.0 | 7/7 STRONG | Phase 1 FAIL | (pre-§6.2) | PARKED | NO |
| J (Donchian) | v4.0 | 7/7 STRONG | Phase 0 NO-GO | (pre-§6.2) | PARKED | NO |
| M (AdaptiveTrend) | v4.0 | 6/7 + 1 cond | Phase 0 NO-GO | (pre-§6.2) | ARCHIVED | NO |
| L (Enhanced CP) | v4.0 | 5/7 + 1 cond | lab WF positive; forward 1/3 replicas positive | **FAIL §6.2.6** (2026-05-03) — ~3–5%/yr deflated; refer to §4.5 | PARKED → §4.5 sub-signal | NO (standalone); confirmed gate signal |
| **Filter v4.x precision so far** | | | | | | **0 / 6** |
| | | | | | | (L: standalone NO; §6.2 correctly rejected; signal absorbed into §4.5) |

**v5.1 note (2026-05-03):** Two candidates evaluated under v5.0 gates since v5.0 release have been correctly rejected at low cost without reaching the precision-tracking table:
- **Candidate O (EMA50 × YTD Anchored VWAP):** Rejected at §6.1 (4/7 — below threshold). One Phase 0 quick-test confirmed (PF 0.75, −3.1%). No further effort spent. The §6.1 buildability filter functioned as a cheap reject at the right stage.
- **Candidate N (ShortBias Momentum):** Archived at §4.4 step 3 (regime-split + benchmark-spread test). 2022 spread vs short-BnH = +3.03pp, below +5pp threshold. Confirmed as 96% short-beta capture. No Phase 0 build effort spent. The investigation procedure introduced in v5.0 (Lesson #16) functioned as designed.

These do not enter the precision-tracking table per current definitions (which require §6.2 PASS to count as a "filter PASS"). They are noted here because they are evidence the v5.0 gates work *for what they screen* — the remaining problem is upstream candidate flow (addressed by v5.1 §5 sourcing restructure).

**Candidate L deflation outcome (2026-05-03):** L is the **first candidate to receive a full §6.2 Edge Deflation Pass** under v5.0. Outcome: **FAIL §6.2.6 standalone** (deflated return ~3–5%/yr, deflated Sharpe ~0.20–0.40 — both papers Palazzi 2025 and Tadi & Witzany 2025). Critically, the §6.2 prediction was empirically corroborated by the forward droplet result: paper's 35% OOS-positive (13/37 pairs) ≈ our 33% positive forward replicas (1/3 spreads). This is the first data point we have on §6.2 *predictive accuracy*: the deflation correctly anticipated standalone failure, and the §6.2.6 last-bullet escape hatch ("refer to §4.5 GatedExecution") absorbed the real-but-sub-threshold signal as an explicit gate. Process worked as designed. See `EnhancedCointPairs_Deep_Dive.md` Part 8 for the worksheet and the verdict (option a).

*Update this table after every Phase 0 outcome. If v5.0 gates produce ≥ 2/3 wins in their first 3 fully-evaluated candidates, the gates are effective. If 0/3 pass to live, escalate to §6.6.*

### 6.6 Stage 6 — Workflow Kill Criterion

*When to revise the process itself, not just individual candidates.*

**Trigger:** If 0 of the next 3 §6.2-passing candidates reach ACTIVE with confirmed PF > 1.0, halt new candidate evaluation entirely and run a process retrospective.

**Process retrospective contents:**
1. Re-examine the §6.2 deflation factors. Are they too lenient?
2. Examine whether the failed candidates share a structural feature (e.g., all multi-pair, all daily TF, all from same publication source).
3. Consider abandoning the candidate-discovery pipeline in favor of pure iteration on Active strategies + GatedExecution development.
4. Document outcome in §10 Version History as a vN+1 release.

**Auxiliary trigger:** If 6 calendar months elapse with no candidate reaching ACTIVE status, run the same retrospective regardless of count.

---

## 7. Techniques Library

*Techniques, tools, methods that are not standalone strategies but can strengthen candidates during evaluation, development, or live operation. Mine when evaluating new candidates and when diagnosing deficiencies in active strategies. **Under v5.0, several archived candidates (B funding sleeve, C vol forecasting, D stationarity preprocessing, H whale flow) are explicitly catalogued as gate signals for §4.5 GatedExecution synthesis.***

*Status key:* `AVAILABLE` = ready, libraries identified · `RESEARCH` = needs investigation · `PROVEN` = used successfully

### 7.1 Uncertainty Quantification / Risk Management

#### Conformal Prediction
- **Status:** AVAILABLE
- **What:** Wraps any point-prediction model to produce intervals with mathematical coverage guarantee. Distribution-free.
- **Libraries:** `MAPIE` (sklearn-compatible), `nonconformist`
- **Use:** Confidence-gate ML signals — only enter when interval is tight and entirely on one side of entry price. Plugs directly into GatedExecution as a confidence wrapper.
- **Apply:** Phase 2+ of any ML-based candidate or signal source.

### 7.2 Feature Engineering / Preprocessing

#### Fractional Differentiation
- **Status:** AVAILABLE
- **What:** Makes time series stationary while preserving long-range memory. Better than percent change for ML feature inputs that need both stationarity and price-level memory.
- **Libraries:** `fracdiff` (pip)
- **Source:** López de Prado, "Advances in Financial Machine Learning" Ch. 5
- **Use:** Standard preprocessing for any ML model on price data. Replaces simple returns.

#### Stationarity-Preserving Preprocessing (CNN-style)
- **Status:** RESEARCH (lower priority than fracdiff)
- **Source:** Asareh Nejad et al., SSRN 2024 (was Candidate D)
- **Use:** Multi-feature joint preprocessing if fracdiff is insufficient. Rarely needed.

### 7.3 Signal Quality / Entry Filtering

#### Fee Economics Threshold Sweep
- **Status:** PROVEN (LOB Microstructure, 2026-03-20)
- **What:** Before building execution infrastructure, sweep signal-strength thresholds × time horizons at our actual fee tier (10 bps round-trip). Identify if any profitable operating point exists.
- **Use:** Mandatory pre-implementation check for any signal-driven candidate. ~30 min runtime. See Lesson #7.

#### LOB OFI as Confirmation Filter
- **Status:** RESEARCH (real signal IC=0.135 at 3s, fee-incompatible standalone)
- **Use:** Confirmation gate for an entry signal generated elsewhere (LiqCascade, GatedExecution). No standalone execution → no fee problem.
- **Apply:** When LiqCascade or GatedExecution shows high false-positive entry rate.

### 7.4 Macro / Context Filters

#### Funding Rate Extreme as Contrarian Entry Filter
- **Status:** RESEARCH (Sweep #5)
- **What:** Extreme positive funding (>0.1%/8h sustained for 3+ periods) = crowded longs = elevated unwind risk → favor shorts or block longs. Vice versa for extreme negative. Funding paid every 8h on Binance.
- **Evidence:** Inan SSRN 5576424 (DAR models confirm OOS predictability). Coinbase Institutional / GSR research. Robot Wealth practitioner tests. Effect non-linear (top/bottom decile only). Best-documented configuration is **funding + OI joint** — directly validates LiqCascade Phase 3.5 OI filter.
- **Asset scope:** Works better on altcoins than BTC/ETH. BTC/ETH funding can stay elevated weeks during strong trends. Apply percentile-based threshold on BTC.
- **Data:** Binance REST API (`GET /fapi/v1/fundingRate`, `GET /fapi/v1/openInterest`), free, poll every 8h via sidecar.
- **Use:** Gate on top of existing entry conditions. **Primary GatedExecution gate candidate.** Apply to LiqCascade Phase 4 first.

#### On-Chain Whale Flow as Macro Filter
- **Status:** RESEARCH (was Candidate H)
- **Data:** Whale Alert API (free), CryptoQuant (free tier), Glassnode (free tier), Santiment.
- **Use:** Daily-granularity macro context gate. Directional bias filter when on-chain accumulation/distribution diverges from price.
- **Apply:** Lower priority — sidecar required, signal-to-noise unproven for fully-automated use.

### 7.5 Model Optimization / Meta-Techniques

#### Genetic Algorithm for Strategy Parameter Optimization (CGA-Agent)
- **Status:** RESEARCH (arXiv 2510.07943, 2025)
- **What:** Multi-agent GA with real-time microstructure feedback for parameter optimization. Rolling 30-day reoptimization.
- **Use:** Alternative to Hyperopt. Rolling reopt addresses regime change better than static.
- **Apply:** After base strategy validated; lower priority than getting the base right.

---

## 8. Sourcing Sweep Log

*Each sweep gets an entry. Prevents re-searching the same ground. Under v5.0, new sweeps follow the §5.6 protocol (≤ 15 papers, target a specific gap, populate §6.3 checklist at sweep time).*

### Sweep #1 — 2026-03-20
- Sources: SSRN, arXiv (q-fin), Quantpedia, Oxford-Man, practitioners
- Search terms: `crypto trading strategy novel 2025 2026`, `crypto market microstructure scalping`, `funding rate arbitrage perpetual futures automated`, `Quantpedia crypto trading strategy new`, `arXiv quantitative finance crypto`
- Reviewed: ~25 papers, 8 in detail
- Surfaced: 4 (A through D)
- Recommendation: Candidate A (LOB Microstructure) — *built, archived after fee-incompatibility confirmed*
- Notable not promoted: Catching Crypto Trends (Zarattini) — later promoted as J in Sweep #4, then PARKED; Risk-Aware Deep RL (Bandarupalli) — RL underperformed BnH; CGA-Agent — moved to Techniques 7.5; BTC seasonality — fragile, unclear post-ETF.

### Sweep #2 — 2026-03-22
- Focus: crypto-specific path signature validation, OHLCV-native strategies without sidecars
- Reviewed: ~20 sources, 10 in detail
- Surfaced: Candidate E (Path Signatures, validated for crypto via Rahimi GitHub) and Candidate F (CointPairs, Amberdata + Frontiers + IEEE)
- Recommendation: Both E and F promoted — both subsequently archived after Phase 1 fail
- Notable not promoted: Robot Wealth strategy index (paid); DeltaLag (equities, deep learning); Hawkes LOB (LOB data constraint)

### Sweep #3 — 2026-03-22
- Focus: high-frequency OHLCV-native, per-trade > 10 bps, complementary to LiqCascade
- Reviewed: ~30 sources, 12 in detail
- Surfaced: Candidate G (XSMomentum), Candidate H (Whale Flow → reclassified as Technique)
- Recommendation: G promoted — subsequently PARKED after Phase 1 calendar instability
- Notable not promoted: CryptoPulse (daily, LLM); CTBench (methodology only); Volatility-Adaptive Trend (Karassavidis — abstract only, retrieved later)

### Sweep #4 — 2026-03-31
- Focus: established strategy classes with modern enhancements, biased toward high frequency
- Reviewed: ~40 scanned, 15 in detail
- Surfaced: Candidate J (Ensemble Donchian — Zarattini, re-evaluated from Sweep #1), Candidate K (MTF MACD — filter), Candidate L (Enhanced CointPairs — Palazzi)
- Recommendation: J promoted to #1 — subsequently PARKED at Phase 0
- Notable not promoted: Dynamic Grid Trading (ranging-only); Beluška & Vojtko (BTC trend confirmation, supports J/K but not new); Hawkes LOB (LOB constraint); Probabilistic Vol Forecasting (sizing technique); Tadi & Witzany copula (folded into L's evidence base)

### Sweep #5 — 2026-04-07
- Focus: applied-history-first bias, classical strategies + modern enhancements
- Reviewed: ~35 sources, 10 in detail
- Surfaced: Candidate M (AdaptiveTrend — Bui & Nguyen)
- Recommendation: M promoted to #1 — subsequently ARCHIVED after V01/V02/V03 long-side failures
- Notable not promoted: Bollinger Bands regime study (Arda) — flagged as Phase 0 fallback if M failed; Inan funding paper → Technique 7.4; Volume-Weighted TSMOM (Huang) → potential Phase 1 enhancement; LSTM TA on Bitcoin (single asset, black box); VWAP execution (not alpha generation); RSI on BTC (mean reversion fails — confirms architectural choices)

### Sweep #6 — *not yet run; eligible 2026-05-19 per §4.6 step 6 (may run earlier if §4.6 steps 3–5 complete)*
- Trigger: §4.6 step 6 — eligible after deflation pass on L (step 4) and GatedExecution skeleton (step 5) are drafted, OR original 6-week trigger date 2026-05-19, whichever earlier. Hard constraint: candidates produced are queued for §6.2 deflation only; no implementation work begins until LiqCascade Phase 4 resolves.
- **Target gaps (v5.1 three-axis structure per §5.6):**
  - **Axis A — Structural alpha:** specific gap TBD at sweep time. Candidate areas: options expiry / dealer hedging flow on BTC and ETH (deepest derivatives terrain in crypto); perp-spot basis dislocations; scheduled token unlock event flow; funding-payment-driven flow at the 8h cadence.
  - **Axis B — Gate-shaped signals for GatedExecution:** specific gap TBD at sweep time. Candidate areas: directional bias filters complementary to LiqCascade cascade signal; funding-rate predictive gates (Inan SSRN 5576424 already in §7.4 — find newer / complementary work); whale flow directional filter (Technique 7.4 currently RESEARCH).
  - **Axis C — Capital efficiency:** specific gap TBD at sweep time. Candidate areas: vol-targeting overlay implementable as a Freqtrade `custom_stake_amount`; correlation-aware sizing for multi-pair strategies; drawdown-control overlay applicable to LiqCascade and OracleSurfer simultaneously.
- **Expected post-§6.2 survivors:** honest estimate to be filled in at sweep time. v5.1 baseline expectation: 0–2 across all three axes combined. If estimate exceeds 2, recalibrate (sycophancy failure mode per §1).

---

## 9. Lessons & Principles

Hard-won insights that apply across all approaches. Add as projects conclude.

1. **ML accuracy ≠ trading edge.** A classifier can be 100% accurate and produce zero profit if it learns the labeling formula. Test whether output predicts forward P&L, not label match. *(RAME)*

2. **Entry quality > exit optimization.** Across 8 RAME backtests, changing exits shuffled losses but never reduced totals. The lever is selectivity at entry. *(RAME)*

3. **Structural alpha > statistical alpha.** Liquidation cascades exist because of market mechanics (forced selling), not statistical patterns that arbitrage away. Prefer approaches with a clear *why*. *(RAME → LiqCascade)*

4. **Short-term indicators lie in macro trends.** EMA21 generated bullish signals throughout 2022 bear. Any short-term signal needs a macro filter (EMA200 or equivalent). *(RAME)*

5. **Regime labels are good context, bad signals.** The 2×2+CRISIS framework is real but per-trade edge as a primary signal is too small. Use as a gate. *(RAME → LiqCascade)*

6. **Test the pipeline, not just the model.** Data acquisition, signal latency, execution slippage, fee structure can each independently kill a notebook-perfect strategy. *(general)*

7. **Validate fee economics before building execution.** Run a threshold sweep on held-out test set before any non-trivial execution path. Sweep takes 30 min; building infrastructure takes weeks. *(LOB Microstructure)*

8. **Institutional paper results don't transfer to retail fee tiers.** Always recompute at your actual tier (10 bps round-trip for us). Critical for high-frequency microstructure. *(LOB Microstructure)*

9. **Mean-reversion half-life must match trading-frequency objective.** Real mean-reverting structure (Hurst H ≈ 0.26) is untradeable if reversion is months not hours. Compute OU half-life before building; if P(reversion within time stop) < 20%, it's a directional hold. *(CointPairs)*

10. **Val-period bull markets manufacture false fee-sweep signals.** If validation is sustained bull, long-only entries with fixed time stop show excellent P&L at any threshold — not signal, just buying-and-holding-a-rising-asset. Always check long vs short symmetry. *(CointPairs)*

11. **Time-stop rate > 50% is the primary diagnostic for entry over-sensitivity in event-driven strategies.** When > 50% of entries time-stop with 0% WR, the entry thresholds generate false positives. The fix is upstream at entry, not at the stop. *(LiqCascade Phase 3)*

12. **Lead-lag features ≠ directional edge on followers.** A meaningful nonstationary cross-path score can lose money when traded as naked long/short on a high-beta alt with a wide fixed stop — tail risk dominates even when many exits are small winners. *(Path Signatures E)*

13. **Expanding the universe to more pairs does not improve long-side momentum when the additional pairs are in secular downtrends.** Mid-cap altcoins from the 2021 cycle spent 2022–2024 in persistent downtrends. More altcoins = more falling knives. Verify per-pair PF distribution before scaling up. *(AdaptiveTrend M V02)*

14. **Isolate and test each directional leg of a bidirectional strategy before expanding or improving.** If long+short composite shows marginal positive PF but long destroys capital and short profits, you have a short-bias strategy with a capital-destroying attachment. The diagnostic: run can_short=True full-period, extract leg P&L, decide architecturally before any parameter optimization. *(AdaptiveTrend M)*

15. **(v5.0) The buildability filter is necessary but not sufficient.** A 7/7 STRONG PASS measures literature plausibility and stack fit. It does not predict edge at our fee tier in our forward conditions. v4.x ran 0/4 wins among PASS / STRONG PASS candidates. Always pair the buildability filter with an edge-deflation pass (§6.2) before committing implementation time. *(Process audit 2026-04-17)*

16. **(v5.0) Backtest sub-leg artifacts are not new candidates.** A profitable short leg of a failed bidirectional strategy is a hypothesis, not a strategy. The +26.6% short-leg result of M was promoted directly to #1 priority in v4.3 — that is the same trap as best-of-N pair selection in published papers. Require a regime-split + benchmark-spread test (§4.4 N investigation steps) before any sub-leg can become a candidate. *(Process audit 2026-04-17)*

17. **(v5.0) Repeated failure across the same archetype is data about the archetype, not about specific implementations.** LOB, CointPairs, XSMomentum, Donchian, AdaptiveTrend — all five archived/parked candidates were "draw a paper, build it, hope it works." Three of five had >5/7 filter scores and still failed. The lesson is not "the next paper will be different" — it is "the paper-to-Phase-0 pipeline has poor base-rate conversion at our fee tier and forward conditions." Synthesis (GatedExecution) of validated sub-signals is a structurally different bet with potentially better base-rate. *(Process audit 2026-04-17)*

18. **(v5.1) Sourcing bias matters as much as evaluation rigor.** The v5.0 multi-stage gate is correctly rejecting weak candidates (O at §6.1, N at investigation step 3). But if every candidate flowing into the gate is drawn from the same archetype that has 0/7 wins, even a perfect gate cannot manufacture a winner. The fix is upstream: bias sourcing toward terrain with structurally different base rates. v5.1 narrows along three axes — structural-alpha sources (where there's a *why* before a *how*, per Lesson #3), gate-shaped signals for §4.5 GatedExecution, and capital-efficiency overlays. The first axis is the highest-conviction; the second is the highest-leverage given current architecture; the third addresses unexplored terrain. *(Sourcing protocol restructure 2026-05-03)*

---

## 10. Version History

| Date | Change |
|---|---|
| 2026-05-03 | **Candidate L verdict reached — §6.2 Edge Deflation Pass complete.** Both source papers (Palazzi 2025, Tadi & Witzany 2025) **FAIL §6.2.6 standalone** (deflated return ~3–5%/yr, Sharpe ~0.20–0.40). **Verdict: option (a) — fold spread/z-score signal into §4.5 GatedExecution as sub-signal.** §4.3 L block updated with deflation outcome and reopen trigger; §4.5 GatedExecution table row for spread/z-score upgraded from "PARKED codebase" to "CONFIRMED gate"; §4.6 step 4 marked complete; step 5 (GatedExecution Dev Plan v0.1) is now next-actionable; §6.5 filter-precision table gains L row (first candidate with full §6.2 result); §6.5 v5.1 note expanded with corroboration that deflation correctly predicted standalone failure (paper's 35% OOS-positive ≈ our 33% forward replicas). `EnhancedCointPairs_Deep_Dive.md` Part 8 added (worksheet, checklist, post-mortem, verdict); `EnhancedCointPairs_Dev_Plan.md` FROZEN with status header. First full §6.2 worksheet in project history — process worked as designed. |
| 2026-05-03 | **v5.1 — Sourcing protocol restructure; structural-alpha / gate-shaped bias.** §5 reframed around three structural axes (A: structural-alpha sources, B: gate-shaped signals for §4.5, C: capital-efficiency overlays). §5.5 search terms reorganized along these axes; legacy generic and architecture-specific terms demoted. §5.6 sweep protocol now requires per-axis allocation (~5 papers each, ≤15 total), per-axis hit-rate calibration, and a hard queueing constraint (sweep candidates queue for §6.2 only — no implementation work begins until ACTIVE strategies resolve their go/no-go gates). §4.6 sequencing expanded to 8 numbered steps (4 sessions of active work between now and LiqCascade Phase 4 resolution, then 2 trigger-based steps post-resolution); Sweep #6 trigger language tightened. Internal date inconsistency in original v5.0 (§4.6 said 2026-05-19; §8 Sweep #6 said 2026-05-29) resolved in favor of 2026-05-19 (6 weeks since Sweep #5 on 2026-04-07). §6.5 updated with note acknowledging v5.0 gates correctly rejected O (§6.1) and archived N investigation (§4.4 step 3) at low cost — gates work; problem was upstream candidate flow. §8 Sweep #6 entry rewritten with v5.1 three-axis structure. Lesson #18 added. No changes to §6 multi-stage gate, §7 techniques, or active strategy work (LiqCascade Phase 3.6, OracleSurfer v14 monitoring continue per §4.6 priority sequence). |
| 2026-05-02 | **LiqCascade Phase 3.5 complete; Phase 3.6 (V06 counter-trend) deployed.** Reassessment (752 trades): PF 0.488, short PF 0.672, time-stop rate unchanged at 56.4%. OI filter did not improve results. Binance WebSocket URL migrated Apr 23 — sidecar fixed (stall detection added, URL updated to `/market/ws/!forceOrder@arr`). V06 deployed: counter-trend fade, ETH+SOL only, 15-min time stop, flipped leverage. Kill criterion: 50 trades PF < 1.0. |
| 2026-05-02 | **Candidate N — ARCHIVED (investigation failed step 3).** Short-only regime splits (2022/2023/2024): 6 pairs, ATR_MULT=3.5, 6h. 2022 spread strategy vs short-BnH = +3.03pp — below +5pp threshold; signal confirmed as 96% short-beta capture. Lesson #16 validated. **Candidate O (EMA50 × YTD Anchored VWAP) — REJECTED** at §6.1 (4/7) + Phase 0 NO-GO (PF 0.75, −3.1%, negative every calendar year). Short side −7.18% vs market +27.77%. Reference code retained. Priority ranking updated — LiqCascade reassessment now #1. |
| 2026-05-02 | **Candidate L — forward deploy discontinued; PARKED.** Six-container **`freqtrade-coint-pairs-trading`** run ended by policy after ~**4 weeks**; final combined snapshot (**2026-05-02**): **12** open legs, **17** closed trade rows across DBs, aggregate **≈ +0.01%** vs sum of stakes (closed + open MTM). Per-spread: **BTC/ETH** replicas **~+4.25%** each (**V01/V02**), **BNB/SOL** and **BTC/SOL** replicas **negative**. **Recommendation: keep (not ARCHIVED)** — retain strategies + Phase 0 pipeline for **§4.5** optional spread gate or narrowed §6 revival; reopen only per §4.3 triggers. §4.6 step 4 updated. GatedExecution table gains pairs-spread row. Mirrors updated in **`user_data/info/EnhancedCointPairs_*.md`** (both repos). |
| 2026-04-18 | **Candidate L forward checkpoint** — Six-container deploy (`freqtrade-coint-pairs-trading`): 12 closed / 8 open legs, aggregate total PnL ≈ −1.72% vs stakes; **CONTINUE** (below §2 ~50 closed-trade read; §6 unchanged). Details in deploy repo **`TESTING.md`**. |
| 2026-04-17 | **v5.0 — Major restructure after Process Audit.** Rebuilt evaluation as multi-stage gate (§6.1 buildability + §6.2 edge deflation + §6.3 paper replication checklist + §6.4 phase 0 + §6.5 filter precision tracking + §6.6 workflow kill criterion). Refined frequency objective to portfolio-level (≥30 trades/month) instead of per-strategy. Demoted Candidate N from #1 priority to INVESTIGATION pending regime-split test. Reframed Candidate L from #2 priority to deferred pending GatedExecution design step. Added §4.5 GatedExecution synthesis initiative. Established 70/30 effort allocation rule (active iteration vs new candidates). Reduced sourcing sweep cadence from ~biweekly to ~6-weekly with target-gap protocol (§5.6). Added 3 lessons (#15, #16, #17). Prior v4.3 archived to `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md`. Companion audit doc: `Research_Audit_2026-04-17_Findings_and_Path_Forward.md`. |
| 2026-04-09 | v4.3 — Candidate M ARCHIVED (Phase 0 NO-GO). N added. Lessons #13, #14. (See archive.) |
| 2026-04-08 | v4.2 — M Phase 0 V01 results. (See archive.) |
| 2026-04-07 | v4.1 — Candidate L full-paper analysis. (See archive.) |
| 2026-04-07 | v4.0 — Sweep #5; Candidate M promoted. Funding Rate technique added. (See archive.) |
| 2026-04-07 | v3.9 — OracleSurfer added retroactively to ACTIVE. (See archive.) |
| 2026-04-06 | v3.7–v3.8 — Candidate J PARKED (Phase 0 NO-GO). (See archive.) |
| 2026-03-31 | v3.6 — Sweep #4. J promoted (later parked). (See archive.) |
| 2026-03-29 | v3.4–v3.5 — Candidate G PARKED. (See archive.) |
| 2026-03-23 | v3.2 — Candidate E ARCHIVED. Lesson #12. (See archive.) |
| 2026-03-22 | v2.0–v3.1 — Sweep #2/3, Candidates E/F/G/H, F PARKED then ARCHIVED, Lessons #9–#11. (See archive.) |
| 2026-03-20 | v1.0–v1.5 — Initial creation. Sweep #1. Candidate A ARCHIVED. Lessons #7–#8. (See archive.) |

*For full v1.0–v4.3 changelog with per-version details, see `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md`.*
