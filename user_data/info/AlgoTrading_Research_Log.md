# AlgoTrading Research Log
## Maintained by: [Developer] + Claude (any model)
## Version: v5.3.2 (2026-05-22 — S1 NO-GO; T1 blocked on Tokenomist data decision; session ends here)
> ⛔ **FROZEN / ARCHIVAL (2026-06-07).** This manual Research Log is being merged into the algo-bros
> agent framework. The living successors are in `C:\Users\jtscw\algo-bros\docs\`:
> `RESEARCH_LOG.md` (registry/research), `EVALUATION.md` (the §6 gates + §7 techniques),
> `LESSONS.md` (§9 principles), `ARCHITECTURE.md` (system). Plan + migration status:
> `algo-bros\docs\dev-plans\integration.md`. **Do not add new entries here** — this file is retained
> as the source of record for the pre-integration history (still being mined section-by-section).

## Stack: Cursor / Freqtrade / FreqAI / Claude Opus 4.7
## Prior versions: `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md` (v1.0–v4.3)
## Companion: `Research_Audit_2026-04-17_Findings_and_Path_Forward.md` — read this first if you have not seen the audit

---

## READ THIS FIRST — What This File Is and How to Use It

**This file is the shared memory and operating agreement between the developer and Claude across all sessions.** Claude has no persistent memory between conversations. Every new session — claude.ai or Cursor — starts from zero. This file bridges that gap.

**v5.0 changes (2026-04-17):** A process audit found that the prior 7-point evaluation filter had a 0/4 hit rate among PASS / STRONG PASS candidates that reached Phase 0. The filter was scoring buildability and literature fit, not edge. v5.0 rebuilds the workflow around a multi-stage gate (buildability → edge deflation → paper replication → Phase 0 economics → Phase 1 forward), introduces filter-precision tracking and a workflow kill criterion, refocuses effort on the only two strategies with real-time validation feedback (LiqCascade, OracleSurfer), and frames a synthesis initiative (GatedExecution) that combines lessons from archived candidates rather than repeatedly drawing fresh papers.

**v5.1 changes (2026-05-03):** Sourcing protocol restructure. The v5.0 multi-stage gate is working as designed (Candidate O was correctly rejected at §6.1 for 4/7; Candidate N investigation correctly archived at step 3) — but the *upstream* candidate flow is still drawing from broad academic / practitioner sources with novelty bias, which has produced 0/7 wins. v5.1 narrows sourcing along three structural axes derived from the project's own evidence (Lesson #3, Lesson #17): structural-alpha sources, gate-shaped signals for §4.5 GatedExecution, and capital-efficiency / portfolio-construction overlays. §5, §5.5, §5.6 restructured around these axes. §4.6 sequencing expanded to 8 numbered steps reflecting the May–June 2026 plan (4 sessions of active work between now and LiqCascade Phase 4 resolution, then 2 trigger-based steps post-resolution). Sweep #6 trigger language tightened: the sweep produces queued candidates; evaluation (§6.1–§6.3) can begin immediately; Phase 0+ build work is gated behind §6.2 clearance. Lesson #18 added.

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
1. **Sourcing Sweeps:** Reduced cadence (no more than one sweep per ~6 weeks of calendar time, OR after a Phase 1 outcome on an active candidate, whichever is later). v5.1: each sweep covers all three structural axes (§5) and produces queued candidates; evaluation (§6.1–§6.3) can begin immediately; Phase 0+ build work gated behind §6.2 clearance. Quality > quantity. See §5 for sources, §5.5 for axis-organized search terms, §5.6 for sweep protocol.
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
- `user_data/info/LiquidationCascade_Deep_Dive.md` — LiqCascade (ARCHIVED 2026-05-21)
- `user_data/info/CointPairsTrading_Deep_Dive.md` — Candidate F (ARCHIVED)
- `user_data/info/PathSignatureLeadLag_Deep_Dive.md` — Candidate E (ARCHIVED)
- `user_data/info/CrossSectionalMomentum_Dev_Plan.md` — Candidate G (PARKED — referenced for GatedExecution synthesis)
- `user_data/info/CrossSectionalMomentum_Deep_Dive.md` — Candidate G (PARKED)
- `user_data/info/CrossSectionalMomentum_Phase0_Summary.md` / `Phase1_Summary.md` — G results
- `user_data/info/LOB_Microstructure_Dev_Plan.md` / `Deep_Dive.md` — Candidate A (ARCHIVED)
- `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` / `Deep_Dive.md` — Candidate J (PARKED)
- `user_data/info/EnhancedCointPairs_Dev_Plan.md` / `Deep_Dive.md` — Candidate L (PARKED; forward experiment concluded 2026-05-02)
- `user_data/info/AdaptiveTrend_Dev_Plan.md` / `Deep_Dive.md` — Candidate M (ARCHIVED)
- `user_data/info/GatedExecution_Dev_Plan.md` — GatedExecution synthesis initiative (v0.1 skeleton, 2026-05-03)
- `deploy/digitalocean.md` — DigitalOcean deployment reference
- OracleSurfer — in `Freqtrade` repo (separate): `user_data/strategies/OracleSurfer_v14_PROD.py` (ACTIVE dry-run)

**Document scope rules — what lives here vs. in companion files:**

- **This file is the single source of truth.** A future session reading only this file should have every actionable fact needed to resume work. External documents should either be Dev Plans / Deep Dives (which *implement* decisions made here, not *inform* them) or reference appendices that this file already summarizes.
- **Ephemeral handoff briefs** (`Cursor_Next_Steps_*.md`, web session → Cursor handoffs) are deleted after their items are completed and absorbed into this file (§4.6, §8, §10). They are not cumulative.
- **Dev Plans** are implementation documents for a specific candidate or initiative. They contain commands, phase gates, file paths, and integration details. They should not contain new research decisions or evaluation outcomes that aren't reflected here.
- **Deep Dives** are narrative companions to Dev Plans — results, analysis, post-mortems. The verdict and key numbers from any Deep Dive must appear in §4 (Approach Registry) or §8 (Sweeps) as a summary. The Deep Dive is the appendix; this file is the primary record.
- **Templates** (`Templates/`) are reusable scaffolding — not session-specific. Referenced from the relevant process section (§6.2 in the case of the deflation worksheet).
- **One-off reports** (like `HS_Empirical_Test_*.md`) should have their key findings in §8 and a pointer to the report for methodology details. The Research Log alone must be sufficient for decision-making.
- **No new document types without justification.** If a session produces a `.md` that isn't a Dev Plan, Deep Dive, Template, or handoff brief, it's either inlined here or it shouldn't exist.

**File length note (2026-05-03):** This file is ~940 lines / ~28k tokens. It remains readable in a single pass. If it exceeds ~1,500 lines / ~45k tokens, consider: (1) condensing version history entries to one-line summaries, (2) moving detailed sweep records to a separate Sweep Log and keeping only the current-sweep summary here, (3) archiving completed lessons to a Lessons Log and keeping only the past 2 years' lessons here. Not urgent — flag if observed.

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

#### Liquidation Cascade Strategy (LiqCascade) — v1.0 — **ARCHIVED 2026-05-21 (NO GO)**
- **Status:** ARCHIVED — Final evaluation 2026-05-21. Both V05 and V06 failed Phase 3 go/no-go criteria. Kill criterion met.
- **Core idea:** Detect forced liquidation cascades via Binance WebSocket data as primary alpha signal. Regime framework demoted to context filter only (CRISIS gate + EMA200 macro trend).
- **Architecture:** Sidecar (WebSocket liquidation stream + OI polling) → signal file → Freqtrade 5m strategy reads signal → V05 rode cascade (with-trend) · V06 faded cascade (counter-trend). 4x/2x leverage.
- **Final deployment:** DigitalOcean droplet, Docker. V05 on port 8082 (5 pairs: BTC/ETH/SOL/BNB/XRP). V06 on port 8083 (ETH/SOL only — container stopped due to build issue).
- **Phase plan completed:** Phase 1 (proxy backtest) → Phase 2 (skipped) → Phase 3 (dry-run) → Phase 3.5 (OI filter) → Phase 3.6 (V06 counter-trend). All phases complete. No Phase 4.
- **Phase 3 final results (2026-05-21, 1,186 V05 trades, Mar 17–May 21, 65 days):**
  - Overall: PF 0.493 · WR 40.1% · −$5,630 · Time-stop rate 59.2% (0.1% WR)
  - Exits: time_stop 702 (59.2%, 0.1% WR) · roi 470 (39.6%, 98.1% WR) · trailing 14 (1.2%, 100% WR)
  - Post-V05 deploy (May 2+, 434 trades): PF unchanged, time_stop 57.1% — OI filter did not reduce false positives
  - All 5 pairs negative. Every pair PF < 1.0.
  - **Signal alpha IS real:** ROI exits have 98% WR at +0.71% avg. Trailing exits 100% WR at +3.85% avg. False positives (59% time_stop at 0% WR) overwhelm genuine cascades.
- **V06 final results (2026-05-21, 294 trades, May 2–May 21, 19 days):**
  - PF < 0.5 · WR 34.0% · −$2,696 · Time-stop rate 99.3% (33.6% WR)
  - Only 2 ROI exits in 294 trades (100% WR, +3.28% avg)
  - Fade concept shows directional merit (33.6% time_stop WR vs V05's 0.1%) but 15-min window far too short
  - **Kill criterion MET:** >50 trades, PF < 1.0, WR < 40%
- **Sidecar:** 11,574 WebSocket stalls in 65 days (~181/day). Binance `!forceOrder@arr` stream too unstable for sole-signal-source use. Estimated uptime ~96.5% — below 99% threshold.
- **Root cause (unchanged from Mar 22 preliminary):** Cascade detection generates too many false positives relative to genuine events. Neither threshold tuning, OI confirmation, nor counter-trend fade solved the selectivity problem. The cascade signal is a **gate (confirming filter), not a standalone entry signal.**
- **Disposition:** Archived. Sidecar infrastructure preserved (liquidation event stream, OI polling, signal_history.jsonl). Cascade detection folded into GatedExecution (§4.5) as gate signal — confirms/blocks entries from another primary signal. Do NOT re-open LiqCascade as a standalone strategy.
- **Repo:** `freqtrade-scalper` (separate) — `strategies/LiqCascadeStrategy_V01–V06.py`, `sidecar/liquidation_monitor.py`
- **Deep dive:** `LiquidationCascade_Deep_Dive.md` (in `freqtrade-scalper`, frozen at final evaluation)

#### OracleSurfer Strategy (v14 PROD)
- **Status:** ACTIVE — v14 deployed 2026-04-06 (dry-run). Evaluated 2026-05-21: post-v14 PF 2.09, WR 83.3% (6 trades). Structural overhaul working. **Frequency disqualifies as primary scalping signal** (~1 trade/week BTC-only; multi-pair at 5 pairs → ~5/week still swing territory). Continue monitoring as diversifying swing sleeve candidate.
- **Core idea:** FreqAI XGBoost classifier on 4h features predicts 3-class regime (BEAR / NEUTRAL / BULL) using triple-barrier labeling. Entry on Oracle signal + EMA200 trend alignment + RSI momentum + ADX strength gate. Exits via ROI ladder, trailing stop, hard stop. Single pair: BTC/USDT:USDT futures, 1h execution.
- **Architecture:** FreqAI (XGBoost) → `&s_regime_class` → entry filter (EMA200 + RSI + ADX) → Freqtrade execution. 3-year training window, 4h feature timeframe, retrain every 6h live. Features: Choppiness Index, KAMA distance, SMA200 valuation distance, VIX-Fix synthetic fear gauge, OBV oscillator, 5-period ROC.
- **Current deployment:** DigitalOcean droplet (104.248.17.129), Docker, BTC/USDT:USDT only, `dry_run: true`. Strategy `OracleSurfer_v14_PROD`. Config `config_sniper_BTC_DryRun.json`. FreqAI identifier `Oracle_Surfer_v14_DryRun`. API port 8080. Container uptime: 5 weeks.
- **v12 dry-run results (Feb 25 – Apr 6, 2026, 8 trades):** Win rate 50% · PF 0.31 · Net P&L −$81.20. Exits: 4× trailing SL (+2.96% avg) · 4× hard SL (−10.27% avg). Root cause: asymmetric stop/reward — 50% WR insufficient to break even at this geometry.
- **v12 → v14 structural overhaul (deployed 2026-04-06):** Stop −10% → −5%; ROI ladder added (+10% any time / +7% at 8h / +5% at 16h / +3% at 24h); break-even moved from +3% → +2%; entry tightened (EMA200 + RSI 50± + ADX > 20; MACD removed); Oracle label horizon 96h → 48h with bear priority; DCA disabled; training expanded 1yr → 3yr with regularization; retrain 1h → 6h. Breakeven now at ~40% WR (was ~77%).
- **v14 post-overhaul results (2026-05-21, 6 closed trades, Apr 11 – May 17):**

  | Metric | Value | Threshold | Pass? |
  |---|---|---|---|
  | Closed trades | 6 (14 total, 1 active) | ≥ 15 | BELOW |
  | Win rate | 83.3% (5W / 1L) | > 45% | **YES** |
  | Profit factor | 2.09 | > 1.0 | **YES** |
  | Net P&L | +$14.41 | — | — |
  | Gross win / loss | +$27.67 / −$13.25 | — | — |
  | **Trade frequency** | **~1.0/week (BTC-only)** | **scalping target: ≥30/month portfolio** | **FAIL — swing, not scalping** |

  **Trade log (post-v14):** [unchanged — 6 trades + active #15]

  **Key findings:**
  - Structural overhaul succeeded: PF 0.31 → 2.09. Halved stop distance is the primary P&L driver.
  - Trailing stops capturing +1.8–2.3% consistently on winners (median hold: 2 days).
  - Trade #15 (active short) is first post-v14 short — critical data point. All 6 closed post-v14 trades were longs.
  - **Frequency is the limiting factor.** 1h candles, 4h Oracle features, 48h label horizon → inherently a swing strategy. Even at 5 pairs, ~5 trades/week ≈ 20/month — below the ≥30/month portfolio target. Multi-pair expansion would help but the signal generation rate at 1h execution is the binding constraint.

- **Go/no-go for v14 continuation:** Continue dry-run as passive monitoring. Reassess at 15 post-v14 closed trades or 2026-07-07. Mid-window check (8 post-v14 trades): if WR < 50%, pause. **V14 is profitable but is a swing strategy, not a scalping strategy — it cannot fill the primary-signal slot in GatedExecution, which requires scalping-frequency signal generation.** It remains valuable as a potential diversifying sleeve in a multi-strategy portfolio.
- **Open questions:**
  1. ~~v14 dry-run results~~ → ANSWERED: PF 2.09, WR 83.3% (n=6)
  2. Multi-pair expansion — would improve frequency but signal generation rate at 1h is the binding constraint; unlikely to reach scalping frequency
  3. Oracle signal quality at 48h horizon — appears effective directionally
  4. Should CRISIS gate from LiqCascade be adopted? — deferred
  5. Short performance under v14 parameters — no data yet; Trade #15 is first test
- **v5.2.1 priority:** **#2 — passive monitoring.** Profitable but wrong frequency profile. Do not build implementation plans around OracleSurfer as primary signal. Retain as swing diversifier.
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
- **Reopen trigger (post-verdict):** This candidate reopens **only** if (i) GatedExecution Dev Plan v0.1 explicitly rejects the spread/z-score gate (then revisit option b portfolio-of-spreads with held-out pairs), OR (ii) a §6.2 deflation pass on a *new* paper materially changes the deflated economics. Open-ended hyperopt or "one more droplet month" remain **invalid** triggers. **Dev Plan v0.1 (2026-05-03): spread/z-score gate is CONFIRMED — option (i) closed.**
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

#### Candidate C1: Conditional Volatility Targeting — §6.2 COMPLETE (2026-05-04)
- **Status:** **§6.2 deflation complete; verdict reached.** C1-Sharpe (vol scaling for Sharpe improvement) **REJECTED**. C1-Risk (vol scaling for drawdown reduction) **CONFIRMED as risk overlay candidate for §4.5 GatedExecution §5.2** (unified risk/exit framework). Standalone Dev Plan path is closed; integration path is open.
- **Source papers:** Hoyle & Shephard 2018 (SSRN 3279787, theoretical framework); Yuyama et al. 2023 (SSRN 4548964, crypto-specific empirical replication on portfolios containing BTC, 2016–2022).
- **Pre-deflation diagnostic (run 2026-05-03):** H&S empirical test on 771 LiqCascade V04+V05 closed dry-run trades produced ξ₀ = 0.992 (EWMA), confirming convexity mechanism for Sharpe improvement is structurally absent in our PnL — trades cluster in high-vol periods. Full report: `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md`.
- **§6.2 deflation outcome (2026-05-04):**
  - **C1-Sharpe — FAIL.** H&S diagnostic on actual LiqCascade PnL shows ξ₀ < 1 under EWMA (0.99 combined, 0.88 shorts, 1.21 longs but on negative-S so γ₁>1 *worsens* Sσ). Yuyama 2023 confirms this is a class-level phenomenon: BTC violates the asymmetry precondition that makes vol scaling improve Sharpe. Yuyama's tables show Sharpe improvement is mixed and *not* statistically significant across any VC strategy. Both the system-specific and class-level evidence point to no Sharpe improvement. **Standalone return/Sharpe deflation moot — C1-Sharpe never produced return on its own to deflate.**
  - **C1-Risk — CONDITIONAL PASS as risk overlay (not as standalone).** Yuyama 2023 reports statistically significant (1% level) reductions in standard deviation, VaR, CVaR, and Max Drawdown across all four allocation methods (1/N, BL, MK, RP) and all five VC strategies, robust through 2018 and 2022 crypto crashes. The mechanism — reducing exposure during high-vol periods — *transfers cleanly* to LiqCascade because ξ₀ < 1 means high-vol periods are exactly the periods of worst returns. However, four substantive deflations apply (worksheet: see below).
- **Why §6.2.6 standalone thresholds don't apply.** §6.2.6 requires deflated annual return >25%, Sharpe >1.0, MDD <30%. **These are designed for return-generating strategies, not risk overlays.** A vol-scaling overlay does not generate return — it modifies the risk profile of an underlying strategy's PnL. Applying §6.2.6 standalone thresholds to a risk overlay produces an automatic FAIL by construction, which is meaningless. **C1-Risk is structurally analogous to Candidate L's spread/z-score outcome:** the §6.2.6 last bullet ("if a candidate fails standalone but has a discrete signal that could plug into GatedExecution, refer it there rather than archiving") applies. C1-Risk is referred to §4.5 GatedExecution as a candidate risk overlay for §5.2.
- **Substantive deflations applied to C1-Risk transfer claim:**
  1. **Unit-of-analysis correction.** Yuyama scales whole-portfolio vol; bitcoin is 12.5% under 1/N (much higher under MK/BL). Risk reduction comes partly from cash substitution when bitcoin volatility rises. C1-Risk applied to LiqCascade alone has no substitution mechanism — vol scaling only reduces the position size, leaving signal exposure shape unchanged. **Effective benefit on a single-strategy application is materially smaller than Yuyama's portfolio-level result.** Estimated ~50% magnitude relative to Yuyama's reported MDD reduction.
  2. **Operationalization gap.** Yuyama uses 30-day vol measurement, 10-day rebalance on a daily-priced portfolio. LiqCascade is trade-driven (~16 trades/day). The mapping requires defining: (a) per-trade vs per-calendar-day vol measurement; (b) per-entry vs rolling position scaling; (c) rebalance trigger semantics. **§6.1 buildability path is concrete but not yet specified — Phase 0 spec work required before Cursor build.**
  3. **PnL distribution conditional on Phase 4 — NOW RESOLVED.** H&S diagnostic ran on V04+V05 dry-run; V06 (counter-trend, OI-filtered) was the production variant in active forward testing. V06 kill criterion met 2026-05-21 (294 trades, PF < 0.5). ξ₀ re-verify on V06 PnL is moot — no production V06 deployment remains. The original V04+V05 diagnostic (ξ₀ = 0.992 under EWMA) stands as the best available estimate for cascade-detection-based PnL.
  4. **Underlying-return precondition.** Yuyama's Calmar improvements come from MDD reduction *outpacing* return reduction. On a long-bitcoin portfolio with positive expected return, this works. **On a strategy with negative expected return, vol scaling reduces magnitude of losses but does not improve Calmar in any meaningful sense.** LiqCascade dry-run showed negative expectancy (S = −0.259, PF < 1.0 across all variants). The C1-Risk transfer claim **depends on another GatedExecution primary signal being established with positive expected return** — LiqCascade did not clear its own gate.
- **Verdict.** C1-Risk is referred to §4.5 GatedExecution §5.2 as a **candidate risk overlay** with the following integration constraints: (a) applies only when the underlying strategy has cleared its own go/no-go (positive expected return) — LiqCascade did NOT clear (2026-05-21); (b) operationalization spec required as a Phase 0 pre-build artifact; (c) magnitude expectation calibrated to ~50% of Yuyama's portfolio-level MDD reduction (not 100%). V06 ξ₀ re-verify moot after LiqCascade NO GO. **No Phase 0+ build authorized until a GatedExecution primary signal with positive expected return is established.**
- **§6.2 worksheet:** `Templates/Edge_Deflation_Worksheet_C1Risk_2026-05-04.md` (full worksheet — populates the standard template with C1-Risk-specific reasoning including the §6.2.6 standalone-vs-overlay distinction).
- **§6.3 Paper Replication Checklist:** populated below in §6.3 (since C1-Risk clears §6.2 conditionally).
- **Reopen trigger (post-verdict, updated 2026-05-21):** LiqCascade Phase 4 returned NO GO (both V05 and V06 failed). C1-Risk reopens for Phase 0 build only if (i) another GatedExecution primary signal is established with positive expected return, AND (ii) operationalization spec is drafted and reviewed. V06 ξ₀ re-verify is now moot (V06 kill criterion met — no production PnL to target). Open-ended hyperopt or speculative implementation remain **invalid** triggers.

#### Candidates B, C, D, H, I, K — preserved status
- **B (Funding Rate Arbitrage):** PARKED — non-Freqtrade infrastructure; lower ROI than active candidates. Status unchanged; reconsider as a carry sleeve under GatedExecution if a 2-leg sidecar is built.
- **C (Volatility Commonality Forecasting):** Reclassified as Technique (§7) — vol-timing layer.
- **D (CNN Trend / Stationarity Preprocessing):** Reclassified as Technique (§7.2 — fractional differentiation already covers most of this).
- **H (On-Chain Whale Flow):** Reclassified as Technique (§7.4) — macro filter.
- **I (Path Signature-Enhanced Momentum):** RESERVED — prerequisites unchanged; unlikely under v5.0 unless surfaces as a discrete signal layer in GatedExecution.
- **K (Multi-Timeframe Trend Confirmation):** Filter/enhancement — not standalone. Eligible as a gate signal in GatedExecution.

#### Candidate A1-R: OFI/CVD at Candle Level — §6.1 COMPLETE (2026-05-21)

- **Status:** **ARCHIVED — Phase 0 NO-GO (2026-05-21).** Both signal formulations failed initial backtest screening. 3s→5m OFI transfer hypothesis not supported by data.
- **Source:** Sweep #8 (2026-05-21). Resurrected from Candidate A (LOB Microstructure, archived 2026-03-20).
- **Core idea:** Compute trade imbalance from Freqtrade's native public trade data at 5m candles. Trade when imbalances are extreme.
- **Phase 0 backtest results (2026-01-01 to 2026-01-15, BTC+ETH, 2× leverage, 0.1% fee):**

  | Variant | Signal | Pairs | Trades | WR | PF | Net | Time-stop % |
  |---|---|---|---|---|---|---|---|
  | V01 | Per-candle OFI z-score (z > 2.0) | BTC+ETH | 73 | 17.8% | 0.21 | −$107 | 98.6% |
  | V02 | Cumulative delta divergence | BTC+ETH | 312 | 10.6% | 0.11 | −$457 | 98.7% |

  **Parameter sweep:** z=2.0 → 73 trades, PF 0.21. z=3.0 → 1 trade, PF 0.00. No intermediate threshold produced both adequate frequency and positive PF. ETH's thinner order books made results worse, not better (WR 15.4% vs BTC 20.6%). The informed-trader footprint visible in tick-level data (dir_acc=54.2% at 3s) washes out completely at 5m candles — trade classification noise (~15-20% tick rule error) and temporal aggregation destroy the remaining edge.

- **Root cause:** The OFI edge at 3s was barely above noise (dir_acc=54.2%). At 5m, the aggregation window is 100× longer (300s vs 3s), averaging thousands of trades into a single delta value. Whatever informed-trader signal exists at the tick level is diluted beyond recovery by the time it reaches a 5m candle. Tick rule misclassification compounds this — the ~15-20% of trades misclassified as buy vs sell injects enough noise to mask any remaining signal.
- **Disposition:** Archived. Strategy files retained for reference (`A1_ROFI_V01.py`, `A1_ROFI_V02.py`, `config_a1_rofi_V01.json`). Freqtrade orderflow pipeline validated and reusable for future microstructure work. Lesson: tick-level signals do not aggregate to candle-level signals — the temporal aggregation destroys edge that depends on sequencing within the candle.
- **Repo:** `freqtrade-strategy-lab` — `user_data/strategies/A1_ROFI_V01.py`, `V02.py`, `config/config_a1_rofi_V01.json`

#### Candidate S1: Funding Rate Timing — ARCHIVED Phase 0 NO-GO (2026-05-22)

- **Status:** **ARCHIVED — Phase 0 NO-GO.** Both directional hypotheses failed. Pre-funding move too small for retail fees.
- **Core idea:** Enter 5-15 min before Binance 8h funding payments when funding rate is in extreme decile. Multi-pair, 5m candles.
- **Phase 0 backtest results (2026-04-20 to 2026-05-10, BTC+ETH, 2× leverage, 0.1% fee, expanding percentile rank):**

  | Variant | Direction | Trades | WR | PF | Net | Time-stop |
  |---|---|---|---|---|---|---|
  | V01 fade | Against funding (contrarian) | 13 | 0% | 0.00 | −$17 | 85% |
  | V02 momentum | With funding (continuation) | 13 | 7.7% | 0.11 | −$16 | 92% |

  **Unfiltered reference (all in-window candles, no funding filter):** 118 trades, PF 0.04, WR 6.8%, time_stop 84%.

- **Root cause:** The pre-funding price move is 5-15 bps on average, which is below or barely above the 10 bps round-trip taker fee. With 2× leverage, the breakeven move is ~5 bps — the average move doesn't clear it. Additionally, the direction of the pre-funding move is not systematically predictable — both fading the crowded side and riding momentum produced near-zero WR. The funding rate signal is a real economic phenomenon but the effect size at 5-15 minute pre-funding windows is too small for our fee tier.
- **Disposition:** Archived. Strategy file retained (`S1_FundingRateTiming_V01.py`, `config_s1_funding_V01.json`). Funding rate data loading pipeline validated (feather file → OHLCV format, `open` column = funding rate). Lesson: event-driven strategies need effect sizes at least 3× the round-trip fee to survive noise; funding payment timing is a real event but the pre-funding window effect is below this threshold.
- **Repo:** `freqtrade-strategy-lab` — `user_data/strategies/S1_FundingRateTiming_V01.py`, `config/config_s1_funding_V01.json`

#### Candidate T1: Token-Unlock Short Bias — NEXT (2026-05-22) — **AWAITING DATA DECISION**

- **Status:** **§6.1 blocked on data availability.** Tokenomist has unlock data but historical + recipient-type segmentation may require Pro tier. Developer must verify before next session.
- **Core idea:** Short tokens with ≥1% of circulating supply unlocking, **team-only** (Keyrock 2024: team unlocks drop up to 25%; ecosystem unlocks net +1.18% — wrong direction). Daily frequency, Binance perps.
- **Why team-only filtering is mandatory:** Animoca 2026: naive all-unlocks effect = 0.6%/2wk — below 1.5% breakeven at 10 bps RT. Without recipient-type segmentation, the strategy is dead on arrival. The filter IS the strategy.
- **§6.1 preliminary (5 of 7 scorable, 1 BLOCKED):**

  | # | Criterion | Score | Notes |
  |---|---|---|---|
  | 1 | Data availability | **BLOCKED** | Tokenomist free tier / API trial needs verification: historical unlocks + recipient types? |
  | 2 | Compute fit | PASS | Daily event study, trivial |
  | 3 | Freqtrade compatibility | PASS | Daily candles, standard OHLCV |
  | 4 | OOS evidence | PASS | Keyrock 2024 (16K events), Field & Hanka 2001 (JFE) |
  | 5 | Clear mechanism | PASS | Supply increase from team unlocks → sell pressure |
  | 6 | Complementarity | PASS | Event-driven, non-technical |
  | 7 | Implementation scope | PASS | Event study + daily strategy, <1 week |

- **PATH FORWARD — single decision gate (developer action required before next session):**

  1. **Sign up for Tokenomist free trial** at https://tokenomist.ai (Google Form for API trial). Check:
     - Does the API/CSV provide **historical** unlock data (not just upcoming)?
     - Does it include **recipient type** (team / investor / ecosystem / advisors)?
     - If both YES → T1 unblocked. Next session: complete §6.1 + build Phase 0 event study.
     - If historical YES but recipient NO → T1 is dead (naive all-unlocks below breakeven). Pivot to A1 (GEX) or Sweep #9.
     - If historical NO → T1 is dead. Pivot to A1 (GEX) or Sweep #9.

  2. **If T1 is blocked:** The queue is A1 (GEX Flow, Glassnode paywall, 15% survival) → Sweep #9 (targeted scalping-frequency primary signal). Both A1-R and S1 failed Phase 0. The GatedExecution primary-signal slot remains empty. OracleSurfer v14 continues passive monitoring (swing diversifier only — frequency-disqualified from primary).

- **Key references:** Keyrock 2024 "From Locked to Liquidity" (16,000+ events, methodology disclosed, team/ecosystem/investor segmentation); Animoca 2026 (aggregate 0.3%/week); Field & Hanka 2001 JFE (IPO lockup expiry — academic analogue, US-only jurisdictional caveat).

- **Status:** QUEUED behind S1. Promoted from Sweep #7 investigation at 20% expected §6.2 survival. Requires Keyrock 2024 recipient-type segmentation data for formal candidate status. §6.1 not yet run.

### 4.5 SYNTHESIS INITIATIVE — GatedExecution

**Thesis (v5.0):** The pattern of repeatedly drawing standalone candidates from the literature has produced 0 wins in 7 attempts. Several of those failed candidates produced *partial* validated signals or reusable infrastructure that, individually, do not meet the bar for a deployed strategy but, **combined**, may form a robust edge. The next significant build effort should be a synthesis layer, not the next standalone paper.

**Concept:** A single Freqtrade execution layer that consumes signals from multiple gated sources, takes a trade only when ≥ N gates agree, and uses a unified risk/exit framework.

**Candidate signal sources (drawn from validated/partially-validated work in the registry):**

| Source | Signal | Status | Origin |
|---|---|---|---|
| **Cascade detection** | LiqCascade sidecar event stream | VALIDATED as gate signal (failed standalone — NO GO 2026-05-21). Structure: real alpha (ROI 98% WR) but 59% false-positive rate unsolved by threshold tuning, OI filter, or counter-trend fade. Effective as a confirming gate, not a standalone entry generator. | LiqCascade Phase 3 (final) |
| **Cross-sectional rank gate** | Top-N momentum / bottom-N anti-momentum from XSMomentum infrastructure | PARTIAL (signal weak standalone, real as a gate) | Candidate G code retained |
| **Funding extreme gate** | Block longs / favor shorts when funding >90th percentile rolling 30d | RESEARCH | Technique 7.4 (Inan SSRN 5576424) |
| **Macro EMA200 gate** | Block long entries below daily EMA200; block shorts above | VALIDATED | RAME → LiqCascade |
| **CRISIS gate (ATR p90)** | Block all entries when realized vol > 90th percentile | VALIDATED | RAME → LiqCascade |
| **OI confirmation** | OI change rate > threshold (per-pair calibrated) | CALIBRATED but did not improve live selectivity. Winners had higher |oi_change| than losers (1.67× overall) but deploying the filter produced no material change in time_stop rate or PF. Retain as optional gate with per-pair calibration for future GatedExecution experiments. | LiqCascade Phase 3.5 |
| **OFI confirmation (optional)** | LOB order flow imbalance agrees with entry direction | RESEARCH (real signal, fee-incompatible standalone) | Candidate A salvage |
| **Conformal prediction wrapper** | Tighten entries when prediction interval is narrow and one-sided | RESEARCH | Technique 7.1 |
| **Pairs spread / z-score (mean reversion)** | Per-pair signal: `{direction, confidence ∝ \|z\| above entry, freshness}`. Per-pair calibration mandatory (forward 1/3 positive replicas). | **CONFIRMED gate (2026-05-03)** — §6.2 deflation FAIL standalone (~3–5%/yr post-deflation), 35% OOS-positive across paper universe matches our 33% forward survival; refer per §6.2.6 | Candidate L §4.3, Deep Dive Part 8 |
| **Conditional vol targeting (risk overlay, §5.2 — NOT a gate)** | Position-sizing layer: scale per-entry size inversely with conditional vol so that exposure during high-vol periods is reduced. Operationalization spec required. | **CONFIRMED as §5.2 risk-overlay candidate (2026-05-04)** — §6.2 deflation: C1-Sharpe REJECTED (ξ₀ < 1 in our PnL, Yuyama 2023 confirms class-level); C1-Risk CONDITIONAL PASS as overlay (Yuyama documents 60–70% MDD reduction; transfer estimated at ~50% magnitude after unit-of-analysis correction; requires positive-EV underlying). Phase 0+ build gated on (a) Phase 4 GO, (b) operationalization spec, (c) V06 ξ₀ re-verify. | Candidate C1 §4.4, HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md |

**Architecture sketch:**
- Each signal source produces a normalized output: {direction, confidence, freshness}.
- A `GatedExecutionStrategy` Freqtrade strategy reads the union of signal files / DataFrames per pair per candle.
- Configurable gate combination: `min_agreeing_gates`, per-gate `weight`, per-gate `mandatory` flag (e.g., CRISIS gate is always mandatory).
- Unified exit: ATR-based trailing stop + ROI ladder + time stop (already proven in LiqCascade and OracleSurfer).
- Single risk model: position sizing inverse to realized vol; per-pair max concurrent trades; portfolio max heat.

**Why this is structurally different from RAME:**
- RAME used regime *labels* as the primary signal generator. GatedExecution treats every input as a *gate*, never a primary signal. Trades only fire when the *intersection* of independent gates agrees. This is a fundamentally different statistical assumption — gates kill false positives multiplicatively; signal generators add noise additively.
- RAME tried to learn a regime classifier. GatedExecution uses no learned classifier; every gate is a transparent rule with explicit thresholds.

**Why this is now the next thing to build (updated 2026-05-21):**
- LiqCascade Phase 4 has resolved: **NO GO.** Cascade detection failed as a standalone strategy. Cascade stream is a validated **gate** — it confirms or blocks entries from another primary signal.
- OracleSurfer v14 is profitable (PF 2.09, WR 83.3%) but is a **swing strategy** (~1 trade/week BTC-only, 1h execution, 48h Oracle horizon). It cannot fill the scalping-frequency primary-signal slot. It remains a passive monitoring candidate and potential future diversifying sleeve.
- The primary-signal slot must be filled by a **scalping-frequency** signal source. **A1-R (OFI/CVD at Candle Level)** is the current leading path — resurrects Candidate A's validated OFI signal (IC=0.135, dir_acc=54.2%) at Freqtrade-native candle level where fees don't dominate. Sweep #8 promoted at 35% expected §6.2 survival. A1 (GEX flow, 15% survival, Glassnode paywall concern) is demoted to backup. S1 (Funding Rate Timing, 25%) and T1 (Token Unlocks, 20%) queued behind A1-R.
- GatedExecution is the designated synthesis vehicle. Cascade detection, CRISIS gate, EMA200 gate, OI confirmation, and pairs-spread are all validated gates waiting for a primary signal.

**First Dev Plan trigger:** **ACTIVE.** Next action: A1-R §6.1 Buildability Filter (expected 7/7) → if pass, Phase 0 backtest of OFI/CVD signal at 5m on BTC+alts using Freqtrade orderflow + `--dl-trades`.

**Dev Plan v0.1 skeleton created 2026-05-03** (`GatedExecution_Dev_Plan.md`): signal interface contract (§2), gate catalog (§3), combination logic (§4), unified risk/exit framework (§5). Primary-signal slot: A1-R (OFI/CVD at 5m) pending §6.1 → §6.2 → Phase 0. A1 (GEX) and S1 as backups. Cascade detection confirmed as gate slot.

### 4.6 Effort Allocation & Priority Ranking (v5.1)

**The 70/30 rule (revised 2026-05-21):** LiqCascade Phase 4 resolved NO GO. OracleSurfer is profitable but frequency-disqualified from primary-signal slot (swing, not scalping). Allocate effort as:
- **50%** to GatedExecution Dev Plan v1.0 (A1 deflation as primary-signal path; cascade gate integration; scalping-frequency signal sourcing)
- **25%** to OracleSurfer v14 passive monitoring
- **25%** to remaining Sweep #6 candidate deflation (B1, B2) and infrastructure maintenance

**Sequenced priorities (do in order, do not parallelize):**

> **Current state (2026-05-21):** LiqCascade Phase 4 resolved NO GO. OracleSurfer v14 post-overhaul evaluation complete: profitable (PF 2.09) but swing frequency (~1/week) — disqualified from GatedExecution primary-signal slot. Step 8 active — NO-GO branch. A1 deflation is primary path for scalping-frequency primary signal. OracleSurfer continues as passive monitoring (swing diversifier candidate). All LiqCascade infrastructure preserved for GatedExecution gate slot.

1. **✓ DONE (2026-05-21) — LiqCascade Phase 3.6 → Phase 4 resolved NO GO.** [unchanged]

2. **OracleSurfer v14 monitoring** (passive — evaluated 2026-05-21). Post-v14 (Apr 11+): 6 closed trades, PF 2.09, WR 83.3%, +$14.41. Profitable but **~1 trade/week — swing, not scalping.** Even at 5 pairs, 1h execution + 48h Oracle horizon caps frequency at ~5/week ≈ 20/month, below the ≥30/month portfolio target. Continue passive monitoring. Reassess at 15 post-v14 closed trades. Mid-window: if WR < 50% at 8 post-v14 trades, pause. **Retain as potential swing diversifier sleeve — do NOT build GatedExecution around it.**

3. **✓ DONE (v5.1, 2026-05-03) — §6.5 filter precision touch-up.** Acknowledged that v5.0 gates correctly rejected O (§6.1, 4/7) and correctly archived N investigation (§4.4 step 3) at low cost. See §6.5 v5.1 note.

4. **✓ DONE (2026-05-03) — Deflation pass on Candidate L (PARKED).** Forward droplet experiment concluded 2026-05-02. §6.2 worksheets on Palazzi 2025 and Tadi & Witzany 2025 completed in `EnhancedCointPairs_Deep_Dive.md` Part 8. Both papers **FAIL §6.2.6 standalone** (~3–5%/yr post-deflation). **Verdict: option (a) — fold spread/z-score into §4.5 GatedExecution as sub-signal.** Dev Plan FROZEN; §4.5 table updated; §6.5 filter-precision row to be added below.

5. **✓ DONE (2026-05-03) — GatedExecution Dev Plan v0.1 skeleton.** `GatedExecution_Dev_Plan.md` created. Signal interface contract (§2: `{direction, confidence, freshness}` per pair per candle), gate catalog (§3: 4 CONFIRMED gates + 4 CANDIDATE gates + primary-signal placeholder), combinator logic (§4: `min_agreeing_gates`, weighted confidence, mandatory flags, independence requirement), unified risk/exit framework (§5: ATR trailing + ROI ladder + time stop + inverse-vol sizing). Primary-signal slot left as placeholder — design invariant confirmed under both LiqCascade Phase 4 outcomes. Advancing to v1.0 now that Phase 4 has resolved (NO GO, 2026-05-21) — per step 8.

6. **✓ DONE (2026-05-03) — Sourcing Sweep #6** (first sweep under v5.1 three-axis protocol). Four candidates queued for §6.2 deflation. **Post-sweep article reads** (Hoyle/Shephard 2018, Yuyama 2023, Glassnode GEX Dec 2025) revised total expected survivors from 1.20 to 0.90 — see §8 Sweep #6 entry for full retrospective and revised estimates. Hard queueing constraint was enforced until LiqCascade Phase 4 resolved 2026-05-21 (NO GO) — step 8 now active.

6.5. **✓ DONE (2026-05-03) — Hoyle & Shephard empirical test on existing strategy PnL + §6.2 worksheet template.** [...] Both items improve project infrastructure and inform downstream deflation passes; neither is a new candidate build.

6.6. **✓ DONE (2026-05-03, optional) — B1/B2 pre-deflation reads + full gate calibration (EMA200 + CRISIS multi-year) + Sourcing Sweep #7 + queueing constraint refined.** Four items executed as preparation work. (a) B1/B2 reads revised Sweep #6 aggregate expected survivors 0.90 → 0.71. (b) EMA200 gate CONFIRMED as directional qualifier; CRISIS gate: 0% FP on 6-week forward window, 5/7 true-positive on 2022-2025 crisis events with structural limitation (rolling p90 adapts too fast during clustered crises). (c) Sweep #7: 0 candidates promoted (1 investigation noted: token-unlock short bias). (d) §5.6 rule 5 refined: §6.1-§6.3 evaluation can begin immediately; only Phase 0+ builds gated behind §6.2 clearance. See §8 for full results.

6.7. **✓ DONE (2026-05-04) — Sweep #7 retrospective + Lesson #20 + C1-Risk §6.2 deflation pass.** Three items executed as web-session work between Sweep #6 deflation queue and Phase 4 resolution. (a) Sweep #7 retrospective added with honest scoring against Sweep #6 retro improvements; SSRN/arXiv academic search confirmed no peer-reviewed crypto-token-unlock event study but identified Keyrock 2024 + Field & Hanka 2001 as deflation-eligible references — token-unlock investigation now has §6.2 deflation surface (was from-scratch only). Lesson #20 added (methodology-disclosed empirical reference at any tier vs no such reference at any tier — refines the §6.2 routing rule). (b) C1-Risk §6.2 deflation pass complete: C1-Sharpe REJECTED (ξ₀ < 1 in our PnL, Yuyama 2023 class-level confirmation, no Sharpe improvement); C1-Risk CONDITIONAL PASS as risk overlay candidate for §4.5 GatedExecution §5.2 (not standalone) with four substantive deflations (unit-of-analysis, operationalization, Phase-4-conditional, underlying-EV precondition). §4.4 C1 entry created; §4.5 gate catalog gains vol-overlay row. Step 8 deflation order updated — C1 removed from queue. (c) §5.6 rule 5 refined-rule application validated: §6.2 deflation work proceeded during ACTIVE-strategy soak without compromising hard queueing constraint. See §4.4 Candidate C1, §8 Sweep #7 retrospective.

7. **✓ DONE (2026-05-21) — LiqCascade Phase 4 resolved.** Outcome: NO GO (V05 PF 0.493, V06 PF < 0.5, both well below 1.0 threshold). Triggers step 8 NO-GO branch. GatedExecution Dev Plan v1.0 now unblocked.

8. **GatedExecution Dev Plan v1.0 + primary-signal candidate deflation** (BLOCKED — awaiting developer data decision). A1-R and S1 both Phase 0 NO-GO → T1 blocked on Tokenomist data. See T1 entry in §4.4 for decision gate.
   - **T1** (Token-Unlock Short Bias) → **BLOCKED: verify Tokenomist historical + recipient-type data**
   - **If T1 blocked:** A1 (GEX Flow, 15%, Glassnode paywall) or Sweep #9 (scalping primary signal)
   - Cascade detection, CRISIS, EMA200, OI, pairs-spread = 5 validated gates waiting

*Session ended 2026-05-22. Next session: resolve T1 data decision, then follow the active branch.*

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

5. **Queueing constraint (v5.1, refined 2026-05-03):** A candidate produced by a sweep enters the evaluation pipeline immediately — §6.1 buildability filter, §6.2 edge deflation pass, and §6.3 paper replication checklist can all begin without waiting for ACTIVE strategies to resolve. What is gated: **no Phase 0+ build work** (empirical backtest, strategy code, config files, deploy infrastructure) on a candidate that hasn't cleared §6.2. This preserves the protection against the "sweep → immediately build → fail" pattern (J → M → L, 0/7) while allowing evaluation work to proceed during ACTIVE-strategy soak periods. The original v5.1 rule ("no implementation work until ACTIVE strategies resolve") was too blunt — it created dead time when no Phase 0 work was pending and all §4.6 items were complete. The refined rule correctly distinguishes evaluation (§6.1–§6.3) from implementation (Phase 0+).

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

**Template & worked example:** `Templates/Edge_Deflation_Worksheet_TEMPLATE.md` (blank reusable template) and `Templates/Edge_Deflation_Worksheet_CandidateL_WORKED_EXAMPLE.md` (populated from Candidate L's completed deflation in `EnhancedCointPairs_Deep_Dive.md` Part 8). Use the template for all future §6.2 passes; use the worked example as the canonical reference for how each section should be completed.

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
| C1 (Cond Vol Targeting) | v5.1 | n/a (overlay, not standalone) | n/a (overlay; pre-deflation H&S diagnostic ξ₀=0.99 EWMA) | **C1-Sharpe REJECTED + C1-Risk CONDITIONAL PASS** (2026-05-04) — referred to §4.5 §5.2 as risk overlay; not a standalone-deflation case (§6.2.6 thresholds don't apply to overlays) | §4.5 §5.2 risk overlay candidate | NO (standalone path closed); conditional overlay pending Phase 4 |
| **Filter v4.x precision so far** | | | | | | **0 / 6** |
| | | | | | | (L: standalone NO; §6.2 correctly rejected; signal absorbed into §4.5) |
| | | | | | | (C1: not a return-generating candidate; §6.2 produced overlay verdict, not standalone PASS/FAIL — does not affect 0/6 denominator) |

**v5.1 note (2026-05-03):** Two candidates evaluated under v5.0 gates since v5.0 release have been correctly rejected at low cost without reaching the precision-tracking table:
- **Candidate O (EMA50 × YTD Anchored VWAP):** Rejected at §6.1 (4/7 — below threshold). One Phase 0 quick-test confirmed (PF 0.75, −3.1%). No further effort spent. The §6.1 buildability filter functioned as a cheap reject at the right stage.
- **Candidate N (ShortBias Momentum):** Archived at §4.4 step 3 (regime-split + benchmark-spread test). 2022 spread vs short-BnH = +3.03pp, below +5pp threshold. Confirmed as 96% short-beta capture. No Phase 0 build effort spent. The investigation procedure introduced in v5.0 (Lesson #16) functioned as designed.

These do not enter the precision-tracking table per current definitions (which require §6.2 PASS to count as a "filter PASS"). They are noted here because they are evidence the v5.0 gates work *for what they screen* — the remaining problem is upstream candidate flow (addressed by v5.1 §5 sourcing restructure).

**Candidate L deflation outcome (2026-05-03):** L is the **first candidate to receive a full §6.2 Edge Deflation Pass** under v5.0. Outcome: **FAIL §6.2.6 standalone** (deflated return ~3–5%/yr, deflated Sharpe ~0.20–0.40 — both papers Palazzi 2025 and Tadi & Witzany 2025). Critically, the §6.2 prediction was empirically corroborated by the forward droplet result: paper's 35% OOS-positive (13/37 pairs) ≈ our 33% positive forward replicas (1/3 spreads). This is the first data point we have on §6.2 *predictive accuracy*: the deflation correctly anticipated standalone failure, and the §6.2.6 last-bullet escape hatch ("refer to §4.5 GatedExecution") absorbed the real-but-sub-threshold signal as an explicit gate. Process worked as designed. See `EnhancedCointPairs_Deep_Dive.md` Part 8 for the worksheet and the verdict (option a).

**Candidate C1-Risk deflation outcome (2026-05-04):** C1 is the **first overlay-class candidate to receive a §6.2 pass** — and surfaced a real protocol gap: the §6.2.6 standalone thresholds (deflated return >25%, Sharpe >1.0, MDD <30%) are designed for return-generating strategies and do not apply to risk overlays (vol-scaling, drawdown management, etc.) which by construction don't generate return — they reshape the risk profile of an underlying strategy's PnL. Applying §6.2.6 standalone thresholds to an overlay produces an automatic FAIL by construction, which is meaningless. **Resolution applied this session:** treat C1-Risk as structurally analogous to Candidate L's spread/z-score sub-signal outcome — the §6.2.6 last bullet ("if a candidate fails standalone but has a discrete signal that could plug into GatedExecution, refer it there rather than archiving") covers it, with the integration target being §4.5 §5.2 (unified risk/exit framework) rather than §4.5 gate catalog. Four substantive deflations applied to the Yuyama 2023 risk-reduction transfer claim (unit-of-analysis correction, operationalization gap, Phase-4-conditional PnL distribution, underlying-EV precondition). Verdict: CONDITIONAL PASS as risk overlay candidate. **Protocol implication for future overlays:** §6.2.6 should be amended at the next §6.2 protocol revision to distinguish "standalone candidate" (apply return/Sharpe/MDD thresholds) from "overlay candidate" (apply: does the underlying-strategy risk-profile change clear a meaningful improvement threshold, conditional on positive-EV underlying, with operationalization spec). For now, the routing pattern (refer overlays to §4.5 §5.2 rather than §6.2.6 standalone reject) is the correct workaround.

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

### Sweep #6 — 2026-05-03 (v5.1 protocol — first sweep under three-axis structure; COMPLETE)

**Output document:** See §8 entry below for full per-axis findings, rationale, and queued deflation order.

**Per-axis results:**

**Axis A — Structural alpha:**
- Gap targeted: crypto-specific structural-flow phenomena retail can access without latency competition. Searched (i) options dealer hedging / GEX flow, (ii) perp-spot basis as standalone signal.
- Surfaced: **A1 — Crypto GEX flow** (Glassnode flow-based GEX Dec 2025; supporting MenthorQ, Bookmap, GEXBoard); A2 — Perp basis (Ackerer/Hugonnier/Jermann Wharton 2024, Bocconi BSIC 2025).
- Promoted: **A1**. Rejected A2 (partially redundant with funding extreme gate already in catalog → §4.3 independence violation).

**Axis B — Gate-shaped signals for GatedExecution:**
- Gap targeted: gates using *different underlying data* than catalog (catalog covers price, liquidations, funding, OFI, momentum). Missing: on-chain flow, options surface, exogenous macro proxies.
- Surfaced: **B1 — Stablecoin Exchange Netflow gate** (Unravel Finance Apr 2025; supporting CryptoQuant, Glassnode); **B2 — IV Skew gate** (Wang et al. ScienceDirect 2024; supporting Hoang & Baur SSRN 2020, Amberdata).
- Promoted: **B1**, conditionally **B2** (only if A1 promoted — they share Deribit data infrastructure, marginal cost low).
- Critical pre-deflation finding for B2: BTC IV curve is "more symmetric" than equity IV curves (Wang et al.) — left/right slope ratio ~3:1 BTC vs ~10:1 equities at daily maturity. Skew exists but signal magnitude is structurally weaker in BTC than in S&P 500. Honest pre-§6.2 expectation: low directional information content in BTC, possibly stronger in alts.

**Axis C — Capital-efficiency / portfolio-construction overlays:**
- Gap targeted: overlays that multiply edge from existing signals without depending on directional prediction. Specifically: replacing the placeholder `inverse-vol sizing` in GatedExecution Dev Plan §5.2 with a rigorous, deflation-anchored design.
- Surfaced: **C1 — Conditional Volatility Targeting** (Bongaerts et al. Tandfonline 2020 + Hoyle & Shephard SSRN 2018 anchor + Yuyama et al. Georgetown SSRN 2023 as crypto-specific replication); C2 — Risk Parity / correlation-aware sizing (Yuyama et al.).
- Promoted: **C1** with Yuyama et al. 2023 as crypto anchor and Hoyle & Shephard as falsification lens. Held C2 for v1.0 GatedExecution (premature without single-pair baseline).

---

### Sweep #6 — Post-Sweep Article Reads (2026-05-03, same session)

After producing the initial sweep output and survival estimates, the developer obtained and supplied three full-text references for deeper reading. Reading these *before* deflation produced material updates to the survival estimates and identified specific failure modes that the formal §6.2 pass will need to address. **Pre-deflation reading shifted total expected survivors from 1.20 → 0.90 — closer to the lower end of the v5.1 baseline.** This is recorded here so future sessions see the revised numbers, not the initial sweep estimates.

**Read #1: Hoyle & Shephard 2018 (SSRN 3279787) — full paper.** The C1 falsification lens.
- The headline result: vol scaling improves Sharpe iff `γ₁ ≥ √(1 + S²·γ₂)`, where `γ₁ = ξ₀ + ξ₁`, `ξ₀ = E(σ/σₜ)` is the convexity term (always ≥ 1 by Jensen), and `ξ₁ = Cov(σ/σₜ, μₜ/μ)` is the timing/covariance term.
- Empirically across 142 futures and FX markets (1988–2017): mean γ₁ ≈ 1.33, median ≈ 1.08. Improvement is driven almost entirely by ξ₀ (convexity, mean ~1.36) — **not by clever timing** (ξ₁ ≈ 0 mean, modestly negative median across categories). The paper does not include any crypto data.
- Key implication for our project: H&S provides a clean empirical *test* runnable on our own LiqCascade and OracleSurfer realized PnL, but **does not pre-supply a crypto answer**. We need to compute ξ₀, ξ₁, γ₂ from our actual data.

**Read #2: Yuyama et al. 2023 (Georgetown SSRN 4548964) — full paper.** The crypto-specific vol-control replication.
- 4 allocation methods × 5 vol-control variants × 2017–2022 OOS, BTC + 7 traditional assets.
- Vol control reliably reduces risk: std dev, VaR, CVaR, Max DD all improve at high statistical significance. Max DD reductions of 60–70% (e.g., reference −33% → VC(4) −5%).
- **Vol control mostly *fails* to improve Sharpe over the full period.** None of the Sharpe differences are statistically significant. Authors' diagnosis (Section 5): vol control is suitable for assets where return *falls* when risk rises and *rises* when risk falls. Bitcoin in 2018 and 2022 showed the opposite — return and vol both fell. So Bitcoin violates the precondition for vol control to add Sharpe.
- One narrow exception: during the 2018 and 2022 crypto drawdown years specifically, vol-controlled portfolios produced better Sharpe than the reference in many cases. Bull-year underweighting of BTC dominates in the full-window aggregate.

**Read #3: Glassnode "Introducing: Taker-Flow-Based Gamma Exposure" (Dec 18, 2025).** The A1 methodology source.
- The article confirms the *conceptual* framing: equity-style GEX heuristic ("calls = investors short, dealers long; puts = investors long, dealers short") fails in crypto because crypto traders actively buy calls to speculate. Glassnode reconstructs GEX using Deribit's taker-vs-maker labels per trade, treating the maker as dealer and inferring net dealer positioning from cumulative taker flow strike-by-strike.
- **Methodology paper is sales-gated.** The Appendix on page 8 reads verbatim: *"To find out more about our methodology behind this metric, please reach out to your account manager."* The actual mathematical reconstruction — inventory-tracking model, decay/rebalancing rules, greek-computation choices, maker-side breakdown assumptions — is not in the public article.
- Article's empirical content is a single static snapshot of BTC GEX at one point in time. No backtest, no statistical test of GEX→returns or GEX→realized vol. Disclaimer page 9: *"limited case study with significant constraints… should not be interpreted as investment advice or definitive trading signals."*
- A1 buildability paths: (1) paid Glassnode Professional feed (~$$$$/month, 10-min resolution, BTC/ETH/SOL/XRP/PAXG, Deribit only); (2) DIY reconstruction from raw Deribit ticks with no public benchmark to validate against; (3) use the equity heuristic that the article explicitly says is broken for crypto. None are clean for §6.2.

**Revised survival estimates after deeper reading:**

| Rank | Candidate | Initial est. | Revised est. | Reason for revision |
|---|---|---|---|---|
| 1 | C1 — Conditional Vol Targeting | ~50% | **~30%** | Yuyama 2023 shows naive vol targeting *fails* Sharpe test on BTC because crypto violates the precondition (return-vol asymmetry). Risk-overlay framing (drawdown reduction) more likely path than Sharpe-enhancer framing. |
| 2 | B1 — Stablecoin Netflow Gate | ~30% | **~30%** | No new info from reads; estimate unchanged. |
| 3 | A1 — Crypto GEX Flow | ~25% | **~15%** | Glassnode methodology is sales-gated. Buildability path requires either paid feed (cost not budgeted) or DIY-without-benchmark (high effort, no validation reference). May fail §6.1 buildability filter, not §6.2. |
| 4 | B2 — IV Skew Gate | ~15% | **~15%** | No new info from reads; estimate unchanged. |
| | **Total expected survivors** | **1.20** | **0.90** | |

**Revised C1 deflation framing.** The original C1 charter was implicit: "improve Sharpe via inverse-vol sizing." Yuyama 2023 makes this unlikely to pass standalone in crypto. However, Yuyama's risk-reduction findings are real and statistically significant. The deflation pass should split C1 into two distinct charters:
- **C1-Sharpe:** does conditional vol targeting improve Sharpe of LiqCascade/OracleSurfer/GatedExecution PnL? Apply H&S empirical test on actual realized data. Likely fails per Yuyama.
- **C1-Risk:** does conditional vol targeting reduce drawdown / improve Calmar without materially hurting net return? Apply Yuyama-style asymmetric test. More likely passes.

If C1-Sharpe fails but C1-Risk passes, integrate as a *risk overlay* in Dev Plan §5.2 rather than as a *Sharpe-enhancing sizing rule*. This is a legitimate narrowing per §6.2 protocol — not lowering the bar, but recognizing that risk overlays should be deflated against drawdown/Calmar criteria, not return/Sharpe.

**Revised A1 buildability concern.** A1 may fail §6.1 buildability before reaching §6.2 unless one of: (a) project budgets the Glassnode Professional cost, (b) developer commits effort to DIY reconstruction with custom assumptions and no benchmark, or (c) the equity heuristic is used despite Glassnode's own statement that it's broken for crypto. Decision on A1 path needs to happen at §6.1 stage when the candidate is pulled from the queue — not assumed.

**B2 dependency on A1.** B2 was conditionally promoted only if A1 was built (shared Deribit infrastructure). If A1 fails §6.1 buildability and is not built, B2's marginal-cost argument disappears and B2 likely fails its own §6.1 too.

---

### Sweep #6 — Hoyle & Shephard Empirical Test on Realized PnL (2026-05-03)

Per `Cursor_Next_Steps_2026-05-03.md` Item 1: ran the Hoyle & Shephard 2018 (SSRN 3279787) empirical vol-scaling test on LiqCascade (771 forward dry-run closed trades, V04+V05, 2026-03-17 to 2026-05-03) and OracleSurfer (11 trades — insufficient sample). Full report: `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md`. Analysis script: `user_data/scripts/hs_empirical_test.py`.

**Key finding — LiqCascade combined (771 trades, μ = −0.00407, σ = 0.01570, S = −0.259):**

Under the EWMA 12-day half-life vol process (HS baseline, constant μ): ξ₀ = 0.992, ξ₁ = 0, γ₁ = 0.992, γ₂ = 0.003. HS test **FAILS** (γ₁ < 1.0001). Sσ = −0.257 vs S = −0.259 — marginal Sσ − S = +0.002.

Under the 30-day rolling std vol process (robustness, constant μ): ξ₀ = 1.047, γ₁ = 1.047. HS test **technically PASSES**, but Sσ = −0.271 — Sσ − S = −0.012. Because S < 0, γ₁ > 1 makes Sσ *more* negative (vol scaling amplifies a negative-expectancy process).

**Key finding — LiqCascade shorts only (346 trades, S = −0.165):** ξ₀ = 0.878 under EWMA — the most extreme ξ₀ < 1 in any slice. Short trades cluster most strongly in high-vol periods. γ₁ = 0.878. HS test FAILS. Sσ − S = +0.020 — vol scaling dampens losses slightly by reducing exposure in high-vol windows, but the convexity mechanism that makes vol scaling *improve* Sharpe (ξ₀ ≈ 1.36 in HS's 142-market dataset) is structurally absent.

**Key finding — LiqCascade longs only (425 trades, S = −0.336):** ξ₀ = 1.210 under EWMA — the only slice with ξ₀ > 1. But S < 0 means γ₁ > 1 makes Sσ worse: Sσ − S = −0.069. This is the worst-case interaction: vol scaling boosts convexity on a negative-Sharpe directional leg.

**OracleSurfer:** 11 closed trades — far below 50-trade minimum. Not actionable. Numbers reported in the full report for completeness.

**Implication for C1 deflation estimates:**
- The HS test on our actual PnL provides a data-driven prior that C1-Sharpe (naive vol targeting for Sharpe improvement) is **very unlikely to pass §6.2**. The convexity mechanism that makes vol scaling work in traditional futures (ξ₀ ≈ 1.36) is absent in our liquidation-cascade PnL (ξ₀ ≈ 0.99 under EWMA). Trades cluster in high-vol periods — vol scaling reduces exposure when the signal is most active, not when it's most noisy.
- C1-Risk (vol scaling for drawdown reduction) is more viable. ξ₀ < 1 means position sizes are reduced in high-vol periods, which are when the strategy is producing its worst returns. This would reduce drawdowns even if it doesn't improve Sharpe — consistent with Yuyama 2023's finding of 60–70% Max DD reduction from vol control.
- **Revised C1 survival estimate:** ~20% for C1-Sharpe (down from post-sweep 30%), ~40% for C1-Risk. Combined probability of at least one framing passing: ~40% (unchanged — the risk framing was always the more likely path).
- **C1 survival estimate in the post-sweep reads table (§8, above) remains ~30%** for the combined C1 entry — the HS test adds evidence but doesn't warrant a formal table revision until the §6.2 deflation pass runs. The post-sweep reads revision (50% → 30%) incorporated Yuyama 2023's general crypto finding; the HS test is the strategy-specific confirmation of that finding on our PnL data.

---

### Sweep #6 — B1 & B2 Pre-Deflation Reads (2026-05-03)

After the initial post-sweep reads on C1/A1 references shifted estimates materially, B1 and B2 (which did NOT get full-text reads at sweep time) were re-examined with deeper reading to prevent late-surprise estimate drift at deflation time.

**B1 — Stablecoin Exchange Netflow Gate:**
- **Source quality:** Unravel Finance blog post (April 2025) is a practitioner piece with conceptual framing, not quantitative research. MEXC blog provides similar conceptual overview. CryptoQuant provides the raw data via free-tier API.
- **Signal:** Stablecoin inflows to exchanges = buying power ("dry powder"); outflows = risk-off. Predicts only at extremes — particularly: very low inflows are bearish for medium-term forward returns. Asymmetric.
- **Evidence quality: ANECDOTAL.** The MEXC article cites exactly one data point ($1.5B USDT inflows → ~12% BTC rally "shortly after"). Unravel Finance provides no hit rates, Sharpe ratios, or backtest results. No academic paper was found for this signal.
- **Data availability:** CryptoQuant free-tier API, Unravel Finance free dashboard. Buildable.
- **Limitations:** (1) No defined threshold — what constitutes a "spike" is never quantified. (2) Signal is only predictive at one extreme, not as a continuous indicator. (3) Authors explicitly warn against using flows in isolation. (4) 2025 structural changes (non-USD stablecoins, institutional adoption, regulatory clarity) may break historical patterns. (5) No false-positive rate is available.
- **§6.2 deflation implication:** Unlike C1 (which had a clear HS falsification framework) and A1 (which had data-cost barriers), B1 has no published quantitative evidence to deflate. The §6.2 pass would require building an empirical test from scratch rather than deflating published results — a higher bar. The signal is directionally plausible (capital flows → future buying/selling pressure is a real mechanism) but untested.
- **Revised survival estimate: ~15–20%** (down from 30%). The 30% sweep-time estimate was overly generous for a signal with zero quantitative validation. Conceptual merit only.

**B2 — IV Skew Gate:**
- **Source quality:** Wang et al. (2024) "Implied volatility slopes and jumps in bitcoin options market" — ScienceDirect, behind paywall (abstract only accessible). Hoang & Baur (2020) SSRN paper not found via public search. Supporting sources (Amberdata blog, pi42.com) are introductory/educational content, not quantitative research.
- **Key finding from Research Log sweep-time flag:** BTC IV curve is "more symmetric" than equity IV curves — left/right slope ratio ~3:1 BTC vs ~10:1 equities at daily maturity. This means the signal magnitude is structurally weaker in BTC than in traditional equity options.
- **Evidence quality: UNTESTED for directional prediction.** Available public content discusses IV skew conceptually but provides zero backtests linking skew to forward returns at any horizon. The ScienceDirect paper may contain quantitative evidence behind the paywall, but without access it cannot be evaluated.
- **Data dependency:** B2 was conditionally promoted only if A1 (Crypto GEX Flow) was built — they share Deribit options data infrastructure. A1 was revised to ~15% survival due to Glassnode data costs. If A1 fails §6.1 buildability (likely), B2 loses its marginal-cost argument and likely fails §6.1 itself.
- **Revised survival estimate: ~5–10%** (down from 15%). The dependency on A1 + the structural BTC skew symmetry weakness + zero accessible quantitative evidence make this the weakest queued candidate.

**Aggregate revised estimates after all four pre-deflation reads:**

| Rank | Candidate | Sweep est. | Post-C1/A1 reads | Post-B1/B2 reads | Net change |
|---|---|---|---|---|---|
| 1 | C1 — Conditional Vol Targeting | 50% | 30% | 30% | — |
| 2 | B1 — Stablecoin Netflow Gate | 30% | 30% | **~18%** | −12pp |
| 3 | A1 — Crypto GEX Flow | 25% | 15% | 15% | — |
| 4 | B2 — IV Skew Gate | 15% | 15% | **~8%** | −7pp |
| | **Total expected survivors** | **1.20** | **0.90** | **~0.71** | −0.19 |

The net downward drift from 1.20 → 0.71 across all pre-deflation reads is honest and consistent with v5.1 baseline (0–2 survivors expected). The process of reading before deflation is working as designed — every read has reduced rather than increased survival estimates, indicating the sweep-time estimates had optimism bias.

---

### Sweep #6 — Gate Calibration on LiqCascade Realized PnL (2026-05-03)

Ran the two CONFIRMED gates that can be calibrated from OHLCV data (EMA200, CRISIS) against all 774 LiqCascade forward dry-run trades (V04+V05, 2026-03-17 to 2026-05-03, 5 pairs). Each trade was tagged with whether the gate would have allowed or blocked it based on daily data at entry. OI gate deferred — requires sidecar OI log data. Script: `user_data/scripts/gate_calibration.py`. Output: `user_data/results/gate_calibration_tagged_trades.csv`.

**EMA200 Gate (block longs below daily EMA200, block shorts above):**
- **Hit rate:** 55.2% of trades blocked (427/774). Consistent across all 5 pairs (52–60%).
- **Directional breakdown:** ALL 427 blocked trades were longs (price was below EMA200 for the entire period — bearish/ corrective regime). ALL 347 shorts were allowed (correctly: price below EMA200, shorts are with-trend).
- **P&L of blocked vs allowed:** Blocked (all longs): avg −0.53%, 64.2% losing, sum −$3,503. Allowed (all shorts): avg −0.25%, 57.6% losing, sum −$1,352. P&L delta: −0.27% (blocked trades are WORSE).
- **Calibration verdict:** The gate correctly identified that longs were the worse direction during this bearish period. It functioned as a directional qualifier ("trade with the trend") rather than an entry-quality filter within direction. This is exactly its intended role in GatedExecution — it doesn't need to predict P&L, only to block the wrong direction. **CONFIRMED effective as a directional qualifier.**

**CRISIS Gate (block all entries when ATR > 90th percentile rolling 30d):**
- **Hit rate:** 0.0% (0/774 trades blocked). 
- **Interpretation:** During this 6-week period (Mar 17 – May 3, 2026), none of the 5 pairs experienced a day where ATR exceeded its 90th percentile. This was "normal" crypto volatility — elevated relative to traditional assets, but not crisis-level for crypto. The gate correctly stayed off.
- **Calibration verdict:** Zero false positives during a period of active liquidation-cascade trading. The gate does NOT fire spuriously during "normal high vol" — it reserves blocking for genuine tail events. The true positive rate (does it correctly block during crisis events like March 2020, May 2021, Nov 2022 FTX?) cannot be evaluated from this dataset. **CONFIRMED no false-positive problem.** True-positive calibration requires a multi-year dataset that includes crisis events.

**Limitations of this calibration:**
1. **Single regime.** Mar–May 2026 was a corrective/bearish period. A full bull-bear-chop cycle calibration would reveal regime-dependent behavior.
2. **No OI gate.** The OI confirmation gate (validated on shorts in LiqCascade Phase 3.5) requires the sidecar OI log — not in the trade DB.
3. **6-week window.** Not long enough to catch crisis events for CRISIS gate true-positive calibration.

### Multi-Year CRISIS Gate True-Positive Calibration (2026-05-03)

Extended the CRISIS gate calibration to 2022-2025 daily data (1556 days, all 5 LiqCascade pairs). Measured whether the gate fired during 7 known crisis events that fall within the data range. Script: `user_data/scripts/crisis_calibration_multiyear.py`.

**Headline: the gate has meaningful crisis detection capability but is not a reliable crisis detector.**

**BTC crisis rate:** 12.6% of days (196/1556). Range across pairs: 12.6% (BTC) to 15.0% (ETH). This is higher than expected — the gate fires on roughly 1 in 8 trading days, not just during tail events.

**Known event detection (BTC):** 5/7 events detected. LUNA collapse (May 9-12, 2022), FTX collapse (Nov 8-10, 2022), Japan carry trade unwind (Aug 5, 2024), and Trump tariff shock (Feb 3, 2025) all triggered the gate. **Two events MISSED:**

- **3AC/Celsius insolvency (Jun 13, 2022):** Ratio 0.87 — ATR was below the rolling 90th percentile because LUNA had elevated vol for the preceding month. The gate adapted to the new normal.
- **Liberation Day tariffs (Apr 2, 2025):** Ratio 0.59 — similar issue. The gate measures "is today's vol unusual given the last 30 days," not "is this a crisis."

**Structural limitation identified:** When crisis events cluster (LUNA → 3AC within 5 weeks; 2025 tariff shocks), the rolling p90 adapts upward and the gate stops firing. The gate goes blind when crisis becomes the new normal. This is inherent to the rolling-percentile design.

**Per-year distribution:**

| Pair | 2022 | 2023 | 2024 | 2025 | 2026 (Q1) | Overall |
|------|------|------|------|------|-----------|---------|
| BTC | 7.9% | 13.7% | 17.2% | 11.8% | 11.6% | 12.6% |
| ETH | 7.4% | 18.1% | 21.6% | 13.4% | 13.7% | 15.0% |
| SOL | 6.3% | 18.9% | 17.8% | 8.5% | 11.6% | 12.8% |
| XRP | 10.4% | 17.5% | 19.7% | 7.4% | 8.4% | 13.4% |
| BNB | 8.2% | 16.4% | 17.8% | 13.4% | 12.6% | 13.9% |

2023-2024 had the highest crisis rates — consistent with elevated vol during the 2023 recovery chop and 2024 bull corrections. 2022 (the actual bear-market crisis year) had the lowest rate because the higher base vol raised the bar.

**Avg absolute daily returns:** Crisis days: 3.65–6.73% across pairs. Significantly higher than normal days — the gate does isolate elevated-vol regimes. But the 12-15% hit rate means ~45-55 crisis days per year per pair. At LiqCascade's trade rate (~4 trades/day across 5 pairs), this would block ~50-70 trades/year, some of which would be during genuine opportunity windows where the gate's crisis detection value is ambiguous.

**Calibration recommendation for GatedExecution v1.0:**
1. **Keep the CRISIS gate as mandatory** — it detected 5/7 major crisis events and fires on genuinely elevated-vol days (avg abs return 2-3× normal).
2. **Add per-pair calibration** — crisis rates vary by pair (SOL 12.8% vs ETH 15.0%). Different thresholds per pair would reduce the hit-rate dispersion.
3. **Consider a longer lookback (60d or 90d)** for the rolling percentile to reduce adaptation speed during clustered events. The 30d window adapts too fast — it misses the second event in a cluster.
4. **Do NOT rely on this gate alone for crisis protection** — it will miss the second event in a crisis cluster, which is exactly when a strategy bleeding from the first crisis is most vulnerable.
5. **Gate interaction:** The EMA200 gate would have also blocked long entries during most crisis events (prices tend to be below EMA200 during crises). The combined EMA200 + CRISIS gate overlap provides partial redundancy for the missed events.

---

### Sweep #6 Retrospective (2026-05-03)

Honest retrospective on the v5.1 three-axis sourcing protocol's first execution. Goal: improve Sweep #7 protocol if v5.1 is retained.

**What worked:**
1. **Per-axis allocation forced exploration of unexplored terrain.** Without the three-axis structure, the developer's instinct (and Claude's) would have searched broadly and likely re-found archetype candidates. Axis C (capital efficiency) is genuinely new ground for this project — would not have been searched in a generic sweep.
2. **Hard queueing constraint held.** No implementation work was started during or immediately after the sweep. The developer's "let's bang out a new candidate" suggestion was checked against Lesson #17 and redirected to non-candidate work. This is exactly the failure mode v5.1 §5.6 was built to prevent.
3. **Per-axis hit-rate calibration produced honest estimates that survive scrutiny.** The initial 1.20-survivor estimate was honest (within v5.1 baseline of 0–2). The post-reading revision to 0.90 is also honest. No sycophancy creep.
4. **Sweep-time §6.2-relevant facts captured.** B2's BTC-symmetry weakness, A1's data-infrastructure burden, and C1's Yuyama-applicable failure mode were all flagged at sweep time, not as discoveries during deflation. This compounds — every flag at sweep time is one less surprise during deflation.

**What didn't work / what to fix in Sweep #7:**
1. **§6.3 Paper Replication Checklists were deferred, not populated at sweep time.** v5.1 §5.6 explicitly requires populating §6.3 at sweep time. The deferral is a real protocol deviation. **Sweep #7: enforce §6.3 population at sweep time, no exceptions.** If a candidate cannot be §6.3-populated at sweep time, it is "noted" not "surfaced" and goes to a watch-list, not the deflation queue.
2. **Token-unlock event-flow systematic literature did not surface at this search depth.** Searched for "options dealer hedging" and "perp basis" as Axis A representatives, but did not separately search for "token unlock trading," "vesting cliff trading," or "scheduled airdrop." These were in the §5.5 Axis A search-term list but the sweep prioritized derivatives terrain. **Sweep #7 (or #6 follow-on if Sweep #6 produces no §6.2 survivors): targeted search on token-unlock event flow.** Possible reasons it didn't surface here: (a) literature genuinely thin, (b) wrong search terms, (c) buried in practitioner blogs we didn't reach. Axis A in Sweep #7 should explicitly start with token unlocks before moving to derivatives.
3. **ETF-rebalance flow same as above.** Was on the §5.5 list, not searched in this sweep. Sweep #7 should cover.
4. **Post-sweep article reads materially shifted estimates.** This is a process observation: sweep-time abstracts contain less failure-mode information than full-text reads. The C1 estimate fell from 50% → 30% on full-text reading of Yuyama; A1 from 25% → 15% on the Glassnode article. **Implication for protocol:** for the top 1–2 candidates per axis, full-text reading should happen *before* the sweep concludes, not after. This adds time per sweep but reduces post-sweep estimate drift. Sweep #7 should require full-text reads for any candidate with sweep-time survival estimate ≥ 25%.
5. **Practitioner-blog source quality varied wildly.** Glassnode, Amberdata, Deribit Insights, Unravel Finance produced data-rigorous content. Gate.com produced obvious marketing-content listicles ("5 critical signals," "$20 billion in options OI provides…"). **Sweep #7: maintain a source-quality whitelist/blacklist updated per sweep.** Discount Gate.com, CoinGape, similar to near-zero. Prioritize venue-published research (Deribit Insights, vendor whitepapers from data infrastructure companies).
6. **No SSRN/arXiv search for academic crypto-GEX work.** Sweep #6 found Glassnode's practitioner content for A1 but did not attempt an academic literature search for "Deribit options dealer flow" or "perpetual options gamma exposure." If A1 fails §6.1 buildability, Sweep #7 should explicitly do this academic search before A1 is retired permanently — there may be a methodologically-published version that doesn't require Glassnode's paid feed.

**Process improvements to fold into v5.1 §5.6 (or v5.2 if accumulated):**
- Sweep-time §6.3 population is mandatory, not best-effort.
- Sweep-time full-text reading is required for candidates ≥ 25% estimated survival.
- Source-quality whitelist/blacklist maintained across sweeps.
- Each sweep produces an explicit "search NOT done" list for follow-on sweeps.

These improvements do not require an immediate v5.2 release — they can be folded into the next protocol revision whenever §5.6 is next touched.

---

### Sweep #7 — 2026-05-03 (v5.1 protocol; token-unlock event flow, ETF rebalance, + residual Axis B/C gaps)

**Trigger:** Sweep #6 retrospective "search NOT done" list. Targeted token-unlock event flow and ETF-rebalance literature (Axis A), residual gate-shaped signals (Axis B), and unexplored capital-efficiency terrain (Axis C). First sweep under refined queueing constraint (§5.6 rule 5, 2026-05-03 revision) — candidates can enter §6.1 evaluation immediately regardless of ACTIVE strategy state.

**Per-axis results:**

**Axis A — Structural alpha (token unlocks + ETF flows):**
- **Gap:** Token unlock events as predictable sell-pressure events; ETF creation/redemption flow as forced buying/selling. Both are information-asymmetry / forced-flow mechanisms per Lesson #3.
- **Token unlocks — mechanism real, academic literature absent.** Practitioner data is rich: Tokenomist (schedules + amounts), Alpha Factory (risk framework), CryptoQuant (on-chain flows). The mechanism is basic economics — scheduled supply increases create predictable sell pressure when insiders/early investors gain transferability. But zero academic event studies with systematic backtests were found. No published hit rates, return distributions, or holding periods.
- **ETF flows — too young for publication.** Spot BTC ETFs launched Jan 2024 (~2 years of data). Flow data available via Farside, The Block, Bloomberg. But insufficient for a full bull-bear cycle, and academic publication cycles haven't caught up. Not promotable as a candidate until ≥3 years of data exist.
- **Result: 0 candidates promoted.** Token unlocks are noted as an **INVESTIGATION (token-unlock short bias)** — real mechanism, buildable data, but no paper to deflate. Would require constructing the empirical test from scratch. Eligible for a focused §4.4-style investigation if prioritized.

**Axis B — Gate-shaped signals:**
- **Gap:** Gate signals using data not already in the catalog (catalog already covers: price, liquidations, funding, OI, OFI, momentum, on-chain flow, options skew). Searched for on-chain flow and exchange reserve signals.
- **Result: 0 candidates promoted.** The existing gate catalog from Sweep #6 already covers the major signal types. Exchange inflow/outflow data overlaps with B1 (Stablecoin Netflow). No novel signal types surfaced.
- **Notable: Exchange reserve drawdowns** (coins leaving exchanges → supply shock → bullish) is a widely-discussed practitioner signal with some CryptoQuant analytics, but like stablecoin flows, lacks rigorous backtested evidence. Covered under B1's umbrella — not a separate candidate.

**Axis C — Capital efficiency / portfolio overlays:**
- **Gap:** Unexplored capital-efficiency terrain beyond C1 (Conditional Vol Targeting).
- **Result: 0 candidates promoted.** C1 already covers the primary capital-efficiency use case. Kelly-based sizing and risk parity are well-studied in traditional finance but require adaptation to crypto's non-stationary vol and correlation structure — more of a technique than a candidate.
- **Notable:** Yuyama et al. 2023 (already read for C1) tested 4 allocation methods — the ranking across methods (equal-weight, risk parity, min-variance, max-diversification) was inconclusive in crypto. Not worth a separate candidate.

**Sweep #7 summary:**

| Axis | Target gap | Papers reviewed | Promoted | Reason |
|------|-----------|----------------|----------|--------|
| A | Token-unlock event flow | 5+ practitioner sources (Tokenomist, Alpha Factory, CryptoQuant) | 0 | Mechanism real, academic literature absent — noted as INVESTIGATION |
| A | ETF creation/redemption flow | 3 sources (Farside, Bloomberg, The Block) | 0 | Only ~2yr of data; too young for statistical significance |
| B | Residual gate-shaped signals | 3 sources | 0 | Catalog already covers major signal types |
| C | Residual capital-efficiency | 2 sources (Yuyama re-read) | 0 | C1 already covers |
| | **Total** | **~13** | **0 promoted** | **1 investigation noted (token-unlock short bias)** |

**This is a legitimate sweep outcome per §5.6:** zero candidates promoted does not mean the sweep failed. The search effort covered all three axes. The terrain was genuinely thin for academic literature in the targeted areas. Rejection is a valid outcome.

**Token-unlock investigation charter (for consideration when prioritized — updated 2026-05-04 with deflation-eligible references):**
- Mechanism: scheduled token unlocks → supply increase when insiders/early investors can sell → predictable short-term sell pressure
- Data: Tokenomist (free: upcoming unlocks, amounts, % of supply); CryptoQuant (on-chain flows to exchanges around unlock dates)
- **Deflation-eligible references (added 2026-05-04 SSRN/arXiv pass):**
  1. **Keyrock 2024, "From Locked to Liquidity: What 16,000+ Token Unlocks Teach us"** — practitioner study, methodology disclosed, 16,000+ events. Headline claims: ~90% of unlocks followed by price decline; drawdowns build over 30 days pre-unlock, accelerate in final week, stabilize ~14 days post-unlock; team unlocks worst (avg drops up to 25%); ecosystem unlocks net positive (+1.18% avg); investor unlocks minimal due to OTC routing. Not peer-reviewed but quality-tier above the gate.com/coingabbar marketing-content blacklist. **Effect sizes are deflation candidates per §6.2.**
  2. **Animoca Brands Research 2026** — for unlocks > 1% of circulating supply, 0.3%/week pre and 0.3%/week post. Smaller magnitude than Keyrock's headline; useful as a sanity-check upper bound on what survives serious filtering.
  3. **Field & Hanka 2001, "The Expiration of IPO Share Lockups," Journal of Financial Economics** — academic analogue from equities. 3,217 IPO lockups: −1.8% CAR in expiry week, +40% permanent volume increase, stronger for VC-backed firms. Bradley et al. 2001, Brav & Gompers 2003, Ofek & Richardson 2000 corroborate in US data. **Major caveat for transfer to crypto:** Espenlaub et al. 2001 (UK), Goergen et al. 2006 (France/Germany), Boreiko & Lombardo 2013 (Italy) find *insignificant* abnormal returns. The IPO-lockup effect is jurisdictional, not universal. If the pattern is US-specific in equities, the crypto generalization claim needs explanation — this is a §6.2.6 standalone-test failure mode to anticipate.
- Test: event study — for every unlock ≥ 1% of circulating supply over 2022-2025, measure the N-day forward return distribution (N = 1, 3, 7, 14, 30 days). Compare to unconditional return distribution. Compute hit rate, mean excess return, and significance. **Per Keyrock's findings, also segment by recipient type (team / investor / ecosystem) — the headline 90% may be driven entirely by team unlocks; ecosystem unlocks may be a wrong-direction trade.**
- Fee feasibility: short bias (short before unlock, cover after) — single-leg perps on Binance. Should pass Phase 0 fee sweep if effect size ≥ 3% per event (taker fee = 10 bps RT, slippage ~5 bps per trade → requires ~1.5% to breakeven for single-event trades). **Animoca's 0.3%/week pre + 0.3%/week post = ~0.6% over a 2-week window — well below the 1.5% breakeven, suggesting that absent recipient-type segmentation the naive trade may not pass Phase 0. Keyrock's recipient-segmented numbers are needed to assess whether team-only filtering generates a tradeable edge.**
- Buildability: feasible. Tokenomist has free tier. Binance perps cover most tokens with unlock schedules. No sidecar required if run at daily granularity.
- Risk: effect may be front-run (market prices in unlock before the event — Keyrock confirms this with the 30-day pre-decline). Directional short bias in crypto's secular uptrend carries structural risk. Unlocks of large, liquid tokens (SOL, AVAX) may have minimal impact; small-cap unlocks may be illiquid. **Front-running risk is now quantified, not speculative — the bulk of the move is captured pre-unlock, which means a "short before unlock" trade entering 14 days out gets only the tail of the move.**
- **Investigation now has a §6.2 deflation surface** (was: from-scratch only). When prioritized, sequence: §6.1 buildability check on Keyrock methodology → §6.2 deflation pass on Keyrock claims using its disclosed methodology → empirical replication on Binance perps for ≥1% unlocks 2022-2025 → recipient-type segmentation if aggregate fails.
- **This is NOT a promoted candidate.** It is a scoped investigation for when capacity opens.

---

### Sweep #7 Retrospective (2026-05-04)

Honest accounting of Sweep #7's execution against the six Sweep #6 retrospective improvements, plus structural observations specific to #7. Goal: improve Sweep #8 protocol and surface protocol gaps that #6 did not reveal.

**Scoring against Sweep #6 retrospective improvements:**

1. **§6.3 Paper Replication Checklists at sweep time, no exceptions — vacuously satisfied, untested.** Sweep #7 promoted 0 candidates, so no checklists were needed. The rule was not tested by this sweep. Improvement #1 still requires Sweep #8 (or any sweep that promotes ≥1 candidate) to validate.

2. **Token-unlock event flow searched explicitly, leading Axis A — done; rule confirmed and strengthened.** Sweep #7 led Axis A with token unlocks per the retrospective directive. The procedural rule was followed. The 2026-05-04 SSRN/arXiv follow-up search (improvement #6 below) confirmed that no peer-reviewed academic event study on crypto token unlocks exists. The "academic literature absent" conclusion is now confirmed-negative, not "not yet found." However, the same follow-up identified Keyrock 2024 (16,000+ events, methodology disclosed) as a deflation-eligible practitioner reference and Field & Hanka 2001 (IPO lockup expiry, JFE) as a deflation-eligible academic analogue. The investigation charter has been updated accordingly.

3. **ETF-rebalance flow covered — done; terrain genuinely too young.** Sweep #7 covered ETF flows on Axis A. Result: ~2 years of spot BTC ETF data is insufficient for publication-grade event studies; flow data is available (Farside, Bloomberg, The Block) but no peer-reviewed work yet. This terrain is effectively gated until ≥3 years of data exist (~2027). Worth recording so future sweeps don't re-cover until then.

4. **Full-text reads required for ≥25% survival candidates pre-sweep-conclusion — vacuously satisfied, untested.** No candidate exceeded the 25% threshold (no candidate was promoted at all). Improvement #4 still requires Sweep #8 to validate.

5. **Source-quality whitelist/blacklist maintained — partially done, not formalized as artifact.** Sweep #7 cited Tokenomist, Alpha Factory, CryptoQuant, Farside, Bloomberg, The Block — all consistent with the implicit whitelist (data infrastructure vendors, venue-published research). No marketing-content listicles cited. But the whitelist/blacklist was applied tacitly, not as a maintained artifact. **Sweep #8: formalize.** A single dated list at the start of §8 (or a separate `Sources_Whitelist_Blacklist.md`) with whitelist / blacklist / under-review tiers, updated each sweep. The 2026-05-04 follow-up adds Keyrock to whitelist (methodology-disclosed market-maker research) and confirms Gate.com / coingabbar / generic crypto-news sites on the blacklist.

6. **SSRN/arXiv academic search for terrain where practitioner data dominates — done 2026-05-04.** Followed up on Sweep #7 Axis A. Searched SSRN, arXiv, ScienceDirect, RePEc, Google Scholar with multiple query angles ("token unlock event study," "vesting cliff price impact," "supply schedule cryptocurrency," "lockup expiration," "insider selling lockup"). **Result: no peer-reviewed academic event study on crypto token unlocks exists.** Adjacent crypto event-study literature exists (Polyzos & Youssef 2025 on crisis events, Zhou 2025 on six event types, FTX-collapse studies, ICO cross-listings) but none specifically on scheduled supply increases. **Findings that change the investigation's status:** (a) Keyrock 2024 (16,000+ events, methodology disclosed) is materially better than the Sweep #7-described practitioner sources — promotes from "no paper to deflate" to "practitioner reference at deflation-eligible quality tier." (b) The IPO lockup-expiry literature (Field & Hanka 2001, Bradley et al. 2001, Brav & Gompers 2003) is a strong academic analogue with one critical caveat: international studies (UK, France, Germany, Italy, Nordics) find the effect *insignificant*, suggesting it is jurisdictional rather than universal. Any deflation pass on the crypto generalization needs to address this. (c) Animoca Brands Research 2026 quantifies unlocks > 1% circulating supply at 0.3%/week pre + 0.3%/week post — meaningfully below the ~1.5% Phase 0 breakeven, suggesting recipient-type segmentation (not the aggregate) is where edge would have to come from. **The token-unlock investigation now has a §6.2 deflation surface and is no longer from-scratch-only.** Charter updated above.

**Structural observations specific to Sweep #7:**

7. **"Practitioner data rich + academic literature absent" is now a confirmed recurring pattern across three terrain types.** Token unlocks (Sweep #7, confirmed by 2026-05-04 SSRN/arXiv pass), crypto GEX (Sweep #6 A1), stablecoin netflows (Sweep #6 B1) all share this profile: the mechanism is real, practitioner sources publish on it (often with sales-gated or proprietary data), and no peer-reviewed event study with systematic backtests exists. **Important amendment from the 2026-05-04 follow-up:** practitioner studies are not all the same quality — Keyrock 2024 (methodology disclosed, sample-sized, recipient-segmented) functions as deflation-eligible at a tier most practitioner blogs cannot reach. This refines Lesson #20 (below) — the issue isn't "no peer-reviewed paper" per se, it's "no methodology-disclosed empirical reference at any tier." When such a reference exists at the practitioner tier (Keyrock for unlocks; potentially Glassnode for GEX, depending on access), the investigation gains a deflation surface; when none exists at any tier (stablecoin netflows currently), the §4.4 from-scratch route is the only path.

8. **Sweep #7 ran on residual gaps from Sweep #6, and the depletion shows.** Sweep #6 produced 4 candidates (0.90 expected survivors after full-text revision). Sweep #7 produced 0. This is partially expected: Axis A's densest material was already pulled; Axis B's catalog was already substantially populated; Axis C's primary use case (vol targeting) was already covered by C1. **Implication:** the v5.1 three-axis structure is not infinitely re-runnable on the same project state. After ~2 sweeps per axis, the marginal yield collapses and either (a) the project moves to a different axis structure, (b) candidates from previous sweeps are revisited as the project state changes (e.g., a NO-GO on LiqCascade reopens the primary-signal slot in §4.5 GatedExecution and changes what a "good" Axis A candidate looks like), or (c) the cadence stretches so terrain has time to repopulate (new papers, new data). This is too early to escalate to §6.6 (need n=3+ sweeps with 0 promotions) but worth flagging now. *No protocol change yet; reassess after Sweep #8.*

9. **Cadence question — "follow-on sweep" vs "new sweep" is undefined.** Sweep #6 and Sweep #7 ran the same day (2026-05-03). The trigger was Sweep #6's retrospective "search NOT done" list. §5 says cadence is ~6 weeks between sweeps; §5.6 does not address whether a follow-on sweep on the same day counts as a separate sweep or an extension. **Recommendation:** treat back-to-back sweeps that target gaps from the prior sweep's retro as *extensions* (numbered #6.5 or similar), and reserve a new sweep number for sweeps that are either (a) ≥6 weeks after the prior sweep, or (b) triggered by an active-strategy phase outcome per §5. Under that rule, current "Sweep #7" would be relabeled "Sweep #6.5." This is a small bookkeeping change but matters for §6.5 filter-precision tracking — depletion-driven 0-promotion sweeps shouldn't degrade the per-sweep base rate metric the same way an independent 0-promotion sweep would. *This recommendation is not adopted retroactively in v5.1.1; left for the next protocol revision to decide.*

**Process improvements to fold into §5.6 (or v5.2 if accumulated with #6's improvements):**

- Source whitelist/blacklist maintained as a dated artifact, not tacit (Sweep #6 retro #5, formalized).
- For terrain where practitioner data dominates, an explicit SSRN/arXiv search is required before concluding "academic literature absent" (Sweep #6 retro #6, generalized beyond GEX) — the 2026-05-04 token-unlock pass validates this rule and should be the canonical example.
- Practitioner references are not uniform quality — distinguish "methodology-disclosed practitioner references" (Keyrock-tier; deflation-eligible) from "marketing-content listicles" (gate.com tier; blacklist) at sweep time.
- "Follow-on sweeps" triggered by the prior sweep's retro within the same calendar week are numbered as extensions (#N.5), not new sweeps, for filter-precision accounting.
- After two consecutive sweeps with 0 promotions on a given axis, the next sweep either rotates to a different axis structure or is deferred until a state change (active-strategy resolution, ≥6 weeks elapsed) repopulates terrain.

**What worked in Sweep #7:**

- The honest 0-promotion outcome was reached without a sycophancy stretch. No marginal candidate was promoted to "make the sweep productive." This is the §1 sycophancy guardrail working.
- The token-unlock investigation charter was scoped at sweep time even though the candidate didn't pass — preserving the work for when capacity opens (per §4.4 investigation procedure). The 2026-05-04 follow-up demonstrates the value of this preservation: rather than re-doing the search from scratch, the existing charter was upgraded with new findings.
- Per-axis structure forced Axis B and Axis C to be searched even after it was clear Axis A was thin. Without the structure, the developer's instinct (and Claude's) might have collapsed the sweep early.

**Net protocol verdict on v5.1 after Sweep #7:** The three-axis structure remains sound. The hard queueing constraint (refined 2026-05-03) remains sound. The Sweep #6 retrospective improvements 2, 3, 5, 6 were exercised partially or fully and remain in force; improvements 1 and 4 are still untested and carry over to Sweep #8. The depletion observation (#8 above) is a real concern but premature to act on. The 2026-05-04 SSRN/arXiv follow-up demonstrated that improvement #6 is high-value when applied — it converted a "no path forward" investigation into a "deflation-eligible" one without expanding scope. No v5.2 release triggered; improvements continue to accumulate.

---

### Sweep #8 — Scalping-Frequency Primary Signal (2026-05-21)

**Trigger:** LiqCascade Phase 4 NO GO + OracleSurfer frequency-disqualified. Primary-signal slot in GatedExecution is empty. Sweep #6 candidates (A1/B1/B2) are all long-shots with structural problems (Glassnode paywall, no backtests, paywall). Targeted sweep for scalping-frequency (5m–15m) primary signal candidates.

**Context (why this sweep is Axis-A-heavy):** The binding constraint is the primary-signal slot. Axes B and C are well-covered: 5 validated gates (cascade detection, CRISIS, EMA200, OI, pairs-spread), plus B1/B2 still in deflation queue. C1-Risk confirmed as overlay candidate. Additional gate or overlay candidates without a primary signal are useless. Per §5.6: honest allocation means deprioritizing Axes B and C this sweep.

**Key discovery of this sweep:** Freqtrade (develop branch, available in 2026.3+) has **native orderflow support** via public trade data. Per-candle columns: `bid`, `ask`, `delta`, `cum_delta`, `total_trades`, `imbalances`, plus per-trade data in `dataframe["trades"]`. This was NOT available when Candidate A (LOB Microstructure, archived 2026-03-20) was built with a custom sidecar. It enables OFI/CVD signals at candle level (5m–15m) directly in `populate_indicators()` — no sidecar, no tick data, no L2 order book. Backtest data downloadable via `--dl-trades`.

**Axis A — Scalping-Frequency Primary Signal Candidates:**

**Target gap:** A directional signal operating at 5m–15m candles (not 3s tick-level, not 1h swing). Must produce ≥30 trades/month across a multi-pair portfolio. Must have empirical OOS evidence OR a clear path to Phase 0 empirical test with existing infrastructure. Must be Freqtrade-implementable without new sidecars (Freqtrade orderflow is allowed — it's native).

Search terms attempted: `order flow imbalance crypto futures`, `trade imbalance predictive direction 5 minute crypto`, `cumulative volume delta CVD strategy crypto`, `crypto funding rate timing pre-funding entry`

Sources reviewed: arXiv (1 paper), Freqtrade orderflow documentation, Freqtrade strategies GitHub, dev.to Freqtrade content (1 article)

**Candidates surfaced:**

| ID | Name | Signal | TF | Data | §6.1 risk | §6.2 survival est. |
|---|---|---|---|---|---|---|
| **A1-R** | **OFI/CVD at Candle Level** (resurrection of Candidate A) | Trade imbalance ratio `(bid_vol - ask_vol) / total_vol` from Freqtrade orderflow, rolling z-score normalized. Entry when |z| > threshold. Direction from sign. 5m candles, multi-pair. | 5m | Freqtrade orderflow (public trades via CCXT) — native, no sidecar | Signal already validated (IC=0.135, dir_acc=54.2% at 3s). Fee math improvement: 10 bps vs 5-10 bps 5m move = 1-2× ratio (vs 6× at 3s). Selectivity is the unknown. | **35%** |
| **S1** | **Funding Rate Timing** | Enter 5-15 min before Binance funding payments (00:00/08:00/16:00 UTC). Short if funding > 90th pctl; long if funding < 10th pctl. Exit at funding time + 5 min or trailing stop. 5m candles. | 5m (timed) | OHLCV + CCXT `fetch_funding_rate_history` — no sidecar | Well-known practitioner strategy — edge may be arbed. 3 trades/day × multi-pair = frequency guaranteed. Needs empirical test at retail fees. | **25%** |
| **T1** | **Token-Unlock Short Bias** | Short tokens ≥ 1% of supply unlocking, segmented by recipient type (team unlocks only — Keyrock 2024). Enter N days pre-unlock, cover post-unlock. Daily granularity. | Daily | Tokenomist (free tier) + OHLCV — no sidecar | Already charted as Sweep #7 investigation. Keyrock 2024 + Field & Hanka 2001 provide deflation-eligible references. Animoca 0.6%/2wk below 1.5% breakeven → MUST segment by recipient type. | **20%** |

**A1-R detail — OFI/CVD at Candle Level:**

- **What changed from Candidate A:** Candidate A used L2 order book data at 3-second horizon, required a custom C++ sidecar, and was killed by the 6× fee-to-signal ratio (10 bps taker vs 1.7 bps 3s BTC move std). A1-R uses Freqtrade's native public trade data (NOT L2 — aggTrades only, which is what Binance provides via CCXT). Signal is computed at 5m candle close, not 3s. Trade frequency is ~5–15 per day across 5 pairs, not ~200/day. Fee math: 10 bps RT vs 5–10 bps typical 5m move → 1–2× ratio. With 2× leverage and a selectivity filter, the fee hurdle is surmountable.
- **Signal computation:** `dataframe['delta']` = bid_vol - ask_vol per candle. `dataframe['trade_imbalance']` = delta / total_vol. `dataframe['imbalance_z']` = (imbalance - rolling_mean) / rolling_std over 20-period window. Entry when |imbalance_z| > 2.0, direction = sign(imbalance_z).
- **Why this could work where Candidate A failed:** (1) Freqtrade-native → no sidecar infrastructure, backtest data downloadable; (2) Candle-level → trades per day manageable, fee ratio improved; (3) Multi-pair → 5 pairs × ~2 trades/day = ~40 trades/month — clears the ≥30/month portfolio target.
- **Why it might not:** (1) The OFI edge at 3s may not persist at 5m — the signal could decay; (2) Trade classification (bid vs ask) from aggTrades uses tick rule which has ~15-20% error rate in crypto; (3) Selectivity might be too high (too few trades) or too low (time_stop problem, same as LiqCascade).
- **§6.1 buildability:** PASS expected (7/7). Freqtrade-native data, VPS-compatible, OOS evidence exists (Candidate A), clear mechanism, complementarity (different from EMA200/RSI/ADX), <1 week implementation.
- **Priority:** #1. A1-R is the highest-probability path to a scalping-frequency primary signal. Phase 0 backtest could begin immediately — download trade data for BTC + 4 alts, implement signal in a Freqtrade strategy, backtest 2022-2026.

**S1 detail — Funding Rate Timing:**

- **Mechanism:** Binance funding payments every 8h (00:00, 08:00, 16:00 UTC). When funding rate is extremely positive, the market is net-long and crowded → pre-funding unwinding creates sell pressure. When extremely negative → buy pressure. Also: after funding is paid, the pressure reverses (shorts re-enter, longs re-buy).
- **Practitioner evidence:** Widely discussed on CT, Robot Wealth, QuantConnect. No peer-reviewed paper found in web search. Empirical testing is straightforward — just need OHLCV + funding rate history.
- **§6.1 risk:** Medium. Data is available (CCXT). But edge may be too small after fees — pre-funding moves are typically 5-15 bps, of which fees consume 10 bps. Need leverage to overcome.
- **Priority:** #2. Quick to backtest but lower expected edge.

**T1 detail — Token-Unlock Short Bias:**

- Already charted as Sweep #7 investigation. Updated with Keyrock 2024 methodology.
- **Priority:** #3. Lower frequency (daily), recipient-type segmentation required, and the investigation is not yet a candidate — needs formal promotion.

**Rejected / not promoted:**
- **arXiv 2408.03594 (Hawkes OFI):** Requires tick-level LOB data + sub-second execution → Freqtrade-incompatible. REJECT per §6.1 #3.
- **Dev.to Horus orderflow article:** Marketing for paid API with undisclosed methodology. No strategy logic. REJECT.
- **Volatility breakout (Bollinger squeeze):** Classic overfished archetype. No directional prediction. REJECT per §5.5 technique-specific exclusion.
- **Session-based / opening range:** Crypto 24/7 weakens session effects vs equities. No crypto-specific evidence found. Not promoted.
- **Options expiry / dealer gamma hedging:** No crypto-specific paper found in search. Deribit options OI is ~$20B — large enough for impact. Could be a future sweep item if A1-R fails.

**Axis B — Gate-Shaped Signals:**

**Target gap:** Additional confirmation gates beyond the 5 already validated. With no primary signal, additional gates are low-value. This axis is deprioritized this sweep.

Search terms attempted: only surveyed for novel gate types not in existing catalog.

**Result: 0 candidates promoted.** Minor finding: Freqtrade orderflow enables per-trade large-trade detection (filter individual trades > 95th pctl size in last 20 candles). Could serve as a confirmation gate. Not worth a standalone candidate — note as a technique for A1-R strategy development if A1-R is promoted.

**Axis C — Capital-Efficiency / Portfolio Overlays:**

**Target gap:** Additional overlays beyond C1-Risk. C1-Risk already confirmed as §5.2 overlay candidate. No new overlay candidates needed until primary signal is established.

**Result: 0 candidates promoted.** Axis C is adequately covered for current project state.

**Sweep #8 summary:**

| Axis | Target | Sources | Promoted | Notes |
|---|---|---|---|---|
| A | Scalping primary signal | Freqtrade orderflow docs, arXiv, dev.to, project archives (Candidate A) | 3 (A1-R, S1, T1) | A1-R is highest-probability path |
| B | Gate-shaped signals | Survey only | 0 | 5 validated gates already; B1/B2 still in queue |
| C | Capital-efficiency | Not searched | 0 | C1-Risk covers current needs |
| | **Total** | **~8** | **3 promoted** | **A1-R: 35%, S1: 25%, T1: 20%** |

**Cross-axis recommendation:**

**Advance A1-R (OFI/CVD at Candle Level) to §6.1 Buildability Filter immediately.** It is the only candidate in the sweep with: (a) validated signal evidence from the project's own research (Candidate A), (b) Freqtrade-native data pipeline (no sidecar), (c) improved fee math vs the original that killed it, (d) a §6.1 score expected at 7/7, and (e) direct path to a Phase 0 backtest using existing infrastructure. S1 and T1 are lower priority — queue them behind A1-R. S1 is quick to backtest (~1 day) and worth running in parallel if time permits. T1 is daily-frequency and should be formally promoted from investigation to candidate only if the recipient-type segmentation data (Keyrock 2024) can be obtained.

**Expected survivors after §6.2 (honest):** A1-R 35% (= 0.35 expected). S1 25% (= 0.25). T1 20% (= 0.20). **Total expected: 0.80.** Within v5.1 baseline (0–2). The single-axis focus is appropriate given the binding constraint.

**§5.5 search-term addition:** Add to Axis A — `Freqtrade orderflow trade imbalance`, `cumulative volume delta crypto 5 minute`, `public trade data directional signal`. These terms surfaced A1-R from the project's own archives + Freqtrade documentation rather than external literature — a reminder that the best candidates are sometimes already in the building.

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

19. **(v5.1) Sweep-time abstracts contain less failure-mode information than full-text reads.** Sweep #6 produced initial survival estimates of 50% (C1), 30% (B1), 25% (A1), 15% (B2) — total 1.20. After full-text reading of three references the same session (Hoyle & Shephard 2018, Yuyama 2023, Glassnode GEX Dec 2025), estimates revised to 30% / 30% / 15% / 15% — total 0.90. The full-text reads surfaced specific failure modes (Yuyama: BTC violates the precondition for naive vol targeting to add Sharpe; Glassnode methodology is sales-gated requiring paid feed or DIY-without-benchmark) that the abstracts did not. **For sweeps under v5.1 and beyond: full-text reading is required for any candidate with sweep-time survival estimate ≥ 25% — performed *before* the sweep concludes, not as post-hoc revision.** This adds time per sweep but reduces post-sweep estimate drift and produces deflation-ready facts at sweep time. Fold into §5.6 at next protocol revision. *(Sweep #6 retrospective 2026-05-03)*

20. **(v5.1.1) The §6.2 deflation surface depends on a methodology-disclosed empirical reference, not specifically on a peer-reviewed paper.** Sweep #7's initial conclusion ("token unlocks: no paper to deflate, route to §4.4 from-scratch investigation") was correct on the *peer-reviewed* axis but missed a finer distinction. The 2026-05-04 SSRN/arXiv follow-up confirmed no peer-reviewed crypto-token-unlock event study exists, but identified Keyrock 2024 (16,000+ events, methodology disclosed, sample-sized, recipient-segmented) as a practitioner reference at deflation-eligible quality, plus Field & Hanka 2001 (JFE, IPO lockup expiry) as a strong academic analogue with a critical jurisdictional caveat (US-significant, EU-insignificant). **The operative distinction is "methodology-disclosed empirical reference at any tier" vs "no such reference exists at any tier."** The first routes to §6.2 deflation; the second routes to §4.4 from-scratch investigation. Practitioner sources are not uniform — Keyrock-tier (methodology + sample + segmentation) is deflation-eligible; gate.com/coingabbar-tier (marketing listicles) is blacklist. The recurring "practitioner data rich + academic literature absent" pattern (token unlocks, GEX, stablecoin netflows — Sweep #6 + #7) breaks cleanly along this finer axis: token unlocks now have Keyrock; GEX has Glassnode (sales-gated, partial); stablecoin netflows have neither. **Implication for protocol:** at sweep time, when a practitioner reference is identified, do not stop at "no peer-reviewed paper." Apply a quality-tier check (is methodology disclosed? is sample size stated? are findings replicable in principle?) before routing to §4.4. If the practitioner reference clears the quality-tier check, route to §6.2 instead. Investigation-track candidates should also have their own filter-precision tracking in §6.5 — they're not failures of the §6 gate, they're a different track. *(Sweep #7 retrospective 2026-05-04)*

---

## 10. Version History

| Date | Change |
|---|---|
| 2026-05-22 | **v5.3.2 — S1 Phase 0 NO-GO; T1 blocked on Tokenomist data; session ended.** S1 backtest (Apr 20 – May 10, BTC+ETH): both fade (13 trades, 0% WR) and momentum (13 trades, 7.7% WR) failed. Pre-funding moves 5-15 bps below 10 bps fee. T1 §6.1 preliminary: 5/7 scorable PASS, data availability BLOCKED — historical unlock data + recipient-type segmentation unverified. Single decision gate for developer before next session: sign up for Tokenomist free trial, verify historical data + recipient types exist. If yes → §6.1 complete + Phase 0 event study. If no → pivot to A1 (GEX, 15%) or Sweep #9. OracleSurfer v14 monitoring (passive). 5 validated gates waiting for GatedExecution primary signal. §4.6 step 8 marked BLOCKED with decision branches. |
| 2026-05-21 | **v5.3.1 — A1-R Phase 0 NO-GO. Both OFI variants fail at 5m.** Phase 0 backtest on BTC+ETH (Jan 1-15, 2026, Freqtrade orderflow with `--dl-trades` on local Docker): V01 (OFI z-score, z=2.0): 73 trades, WR 17.8%, PF 0.21, −$107, 98.6% time_stop. V02 (cum_delta divergence): 312 trades, WR 10.6%, PF 0.11, −$457, 98.7% time_stop. Parameter sweep: z=3.0 → 1 trade, z=2.0 → too many false positives — no intermediate threshold. ETH's thinner books made results worse (WR 15.4% vs BTC 20.6%). Root cause: 3s OFI signal (dir_acc=54.2%, barely above noise) washes out at 5m — 100× longer aggregation + 15-20% tick rule misclassification destroy the edge. The tick-level informed-trader footprint does not aggregate to candle level. Strategies retained for reference. Freqtrade orderflow pipeline validated for future microstructure work. S1 (Funding Rate Timing) advanced as next candidate. §4.6 step 8 updated. Lesson candidate: tick/candle aggregation destroys edge. |
| 2026-05-21 | **v5.3.0 — Sweep #8 complete; A1-R (OFI/CVD at Candle Level) promoted as scalping-frequency primary-signal candidate.** Triggered by LiqCascade NO GO + OracleSurfer frequency disqualification. Single-axis focus (Axis A — scalping primary signal). Key finding: Freqtrade 2026.3+ has native orderflow support (public trades → per-candle delta, cum_delta, bid/ask volume, imbalances). Enables OFI/CVD signals at 5m-15m directly in `populate_indicators()` — no sidecar needed. A1-R resurrects Candidate A's validated OFI signal (IC=0.135, dir_acc=54.2%) at candle level where fee math is improved (10 bps vs 5-10 bps 5m move = 1-2× ratio, vs 6× at 3s). 3 candidates promoted: A1-R (OFI/CVD, 35% expected §6.2 survival), S1 (Funding Rate Timing, 25%), T1 (Token Unlocks — promoted from Sweep #7 investigation, 20%). A1 (GEX, 15%) demoted to backup — Glassnode paywall unresolved. A1-R §6.1 Buildability Filter is next action (expected 7/7). §4.5 GatedExecution primary-signal slot updated: A1-R path. §4.6 step 8 deflation order updated: A1-R → S1 → T1 → A1. §5.5 Axis A search terms extended with orderflow-specific terms. |
| 2026-05-21 | **v5.2.1 — OracleSurfer v14 post-overhaul evaluation.** SSH into droplet (104.248.17.129): 14 closed trades (8 pre-v14, 6 post-v14) + 1 active short (Trade #15, opened May 17 — first post-v14 short). Pre-v14 (Feb 25 – Mar 27): WR 50%, PF 0.31, −$81.20 — asymmetric stop/reward made 50% WR unprofitable. Post-v14 (Apr 11 – May 17, after structural overhaul): **WR 83.3%, PF 2.09, +$14.41** — both go/no-go thresholds cleared with strong margin. Halved stop (−10% → −5%) is the primary P&L driver. Trailing stops capturing +1.8–2.3% consistently (median 2-day hold). Only 1 post-v14 loss (−5.41%). All 6 post-v14 winners were longs — short performance untested under v14 parameters; Trade #15 is the first test. Sample below 15-trade minimum — continue dry-run, reassess at 15 post-v14 closed trades. **OracleSurfer is now #1 effort allocation and leading GatedExecution primary-signal candidate (Path B).** If PF > 1.0 sustained at 15 trades, OracleSurfer fills the primary-signal slot with cascade detection + CRISIS + OI as confirming gates — architecturally cleaner than building from A1. GatedExecution §4.5 updated with two-path primary-signal strategy (Path A: A1 deflation; Path B: OracleSurfer with precedence if 15-trade gate cleared). §4.6 effort allocation revised: 40% OracleSurfer / 35% GatedExecution / 25% B1+B2+infra. §4.6 step 2 updated with full trade log and mid-window criteria. |
| 2026-05-21 | **v5.2.0 — LiqCascade Phase 4 resolved NO GO; strategy archived; GatedExecution unblocked.** Final evaluation of deployed dry-run (droplet SSH, 2026-05-21): V05 (1,186 trades, 65 days, 5 pairs) PF 0.493, WR 40.1%, −$5,630 — time_stop 59.2% (0.1% WR), roi 39.6% (98.1% WR). V06 (294 trades, 19 days, ETH+SOL only) PF < 0.5, WR 34.0%, −$2,696 — time_stop 99.3% (33.6% WR), only 2 ROI exits. Kill criterion met: >50 V06 trades, PF < 1.0. OI filter did not improve selectivity (time_stop rate 57% post-V05 deploy vs 59% pre). Sidecar: 11,574 WebSocket stalls in 65 days (~181/day, uptime ~96.5% — below 99% threshold). Root cause unchanged from Mar 22 preliminary: false positives dominate. Cascade signal alpha is real (ROI 98% WR, trailing 100% WR) but unharnessable as standalone entry generator. Both V05 (ride cascade) and V06 (counter-trend fade) failed. Strategy archived. Sidecar infrastructure preserved. Cascade detection folded into GatedExecution §4.5 as gate signal (confirms/blocks, does not generate). §4.1 LiqCascade entry rewritten with final results. §4.5 GatedExecution: trigger now active — primary-signal slot open, cascade detection moved to gate slot, Dev Plan advances to v1.0. §4.6: 70/30 rule revised (50/30/20), steps 1, 7 marked DONE, step 8 NO-GO branch active with deflation order A1→B1→B2. C1-Risk §4.4: Phase-4-conditional deflations resolved; V06 ξ₀ re-verify moot; underlying-EV precondition now depends on A1 or successor primary signal. `LiquidationCascade_Deep_Dive.md` frozen with final post-mortem. |
| 2026-05-04 | **v5.1.2 — Candidate C1-Risk §6.2 deflation pass complete; CONFIRMED as risk overlay candidate for §4.5 GatedExecution §5.2.** First overlay-class candidate to receive a §6.2 pass. Outcome: C1-Sharpe REJECTED (Hoyle & Shephard diagnostic on 771 LiqCascade V04+V05 trades shows ξ₀ = 0.992 EWMA — convexity mechanism for Sharpe improvement is structurally absent in our PnL; Yuyama 2023 confirms BTC violates the precondition at the asset class level; Yuyama's Sharpe deltas are mixed and not statistically significant); C1-Risk CONDITIONAL PASS as risk overlay (Yuyama documents statistically significant — 1% level — reductions in std/VaR/CVaR/MDD across all four allocation methods and five VC strategies; mechanism transfers cleanly to LiqCascade because ξ₀ < 1 means high-vol periods are exactly the periods of worst returns). Four substantive deflations applied to the Yuyama transfer claim: (a) unit-of-analysis correction — Yuyama scales whole-portfolio vol with cash substitution; LiqCascade alone has no substitution mechanism, ~50% magnitude expected; (b) operationalization gap — Yuyama's 30d-measure / 10d-rebalance daily framework needs translation to trade-driven strategy semantics; (c) Phase-4-conditional — H&S diagnostic ran on V04+V05 dry-run, V06 production distribution may differ (likely not, but re-verify); (d) underlying-EV precondition — vol scaling on negative-EV strategy reduces magnitude of losses but does not improve Calmar in any meaningful sense; C1-Risk activates only after a positive-EV underlying is established. **Protocol gap surfaced and documented:** §6.2.6 standalone thresholds (deflated return >25%, Sharpe >1.0, MDD <30%) don't apply to overlay-class candidates by construction; the §6.2.6 last-bullet referral pattern (used for Candidate L) is the correct workaround, with §4.5 §5.2 (unified risk/exit framework) as the integration target rather than the §4.5 gate catalog. §6.2.6 should be amended at next §6.2 protocol revision to formalize the overlay/standalone distinction. New §4.4 entry for Candidate C1; new §4.5 gate catalog row for vol-scaling overlay (flagged as §5.2 risk overlay, not a gate); §6.5 filter-precision tracking gains C1 row with note that overlays don't enter the standalone-PASS denominator; §4.6 step 8 deflation order updated (C1 removed; B1/A1/B2 remain pending Phase 4); new §4.6 step 6.7 logging this work. Worksheet to be created at `Templates/Edge_Deflation_Worksheet_C1Risk_2026-05-04.md` (queued for Cursor session — referenced from §4.4 C1 entry). No changes to ACTIVE strategy work; LiqCascade Phase 4 monitoring (step 7) remains next-actionable. |
| 2026-05-04 | **v5.1.1 — Sweep #7 retrospective + Lesson #20; token-unlock investigation gains deflation-eligible references.** Honest scoring of Sweep #7 against the six Sweep #6 retrospective improvements: rules 1 and 4 vacuously satisfied (no candidates promoted, untested); rule 2 followed and confirmed by 2026-05-04 SSRN/arXiv pass — no peer-reviewed crypto-token-unlock event study exists; rule 3 followed and disconfirmed its premise (ETF data genuinely too young); rule 5 partially followed but not formalized as artifact (Sweep #8 to formalize); rule 6 done — exhaustive SSRN/arXiv/ScienceDirect/RePEc/Google Scholar search confirmed academic literature absent for crypto unlocks but identified Keyrock 2024 (16,000+ events, methodology disclosed) as a deflation-eligible practitioner reference and Field & Hanka 2001 (JFE, IPO lockup expiry) as a strong academic analogue with critical jurisdictional caveat (US-significant, EU-insignificant). Three structural observations added: (a) the "practitioner data rich + academic literature absent" pattern (now n=3) breaks more cleanly along "methodology-disclosed empirical reference at any tier" vs "no such reference at any tier" — captured as Lesson #20; (b) Sweep #7's 0-promotion outcome partly reflects axis depletion since #6, premature to act on but flagged for reassessment after Sweep #8; (c) "follow-on sweeps" triggered by the prior sweep's retro within the same week should be numbered as extensions (#N.5) for filter-precision accounting — recommendation logged, not retroactively applied. Token-unlock investigation charter (§8 Sweep #7) updated with three deflation-eligible references and quantitative effect-size discussion (Animoca 0.3%/week pre+post < 1.5% Phase 0 breakeven implies recipient-type segmentation needed). Investigation now has a §6.2 deflation surface — was from-scratch only. Five process improvements queued for next §5.6 revision (whitelist artifact, SSRN/arXiv mandatory for practitioner-rich terrain, practitioner-tier quality check, follow-on sweep numbering, axis-depletion rotation rule). No v5.2 release triggered — improvements accumulate. No changes to ACTIVE strategy work; LiqCascade Phase 4 monitoring (step 7 in §4.6) remains the next-actionable. |
| 2026-05-03 | **Sourcing Sweep #7 — token-unlock event flow, ETF rebalance, residual Axis B/C gaps.** First sweep under refined queueing constraint (§5.6 rule 5 revision). Three axes covered, ~13 sources reviewed. **0 candidates promoted.** Token unlocks: real mechanism (supply dilution), rich practitioner data (Tokenomist, CryptoQuant), but zero academic event studies with backtests. Noted as INVESTIGATION (token-unlock short bias) with scoped investigation charter. ETF flows: too young (~2yr spot BTC ETF data) for publication cycles. Axis B: gate catalog already covers major signal types. Axis C: C1 already covers. Honest sweep outcome — rejection is valid per §5.6. |
| 2026-05-03 | **Multi-year CRISIS gate true-positive calibration (2022-2025).** Extended calibration to 1556 daily candles per pair. BTC crisis rate 12.6% of days (range 12.6–15.0% across pairs). Detected 5/7 known post-2022 crisis events (LUNA, FTX, Japan carry, Trump tariff). Missed 3AC/Celsius (p90 adapted upward after LUNA) and Liberation Day tariffs. Structural limitation: rolling 30d percentile adapts too fast during clustered events — gate goes blind when crisis becomes the new normal. Per-year rates: 2022 lowest (6.3–10.4%), 2023-2024 highest (13.7–21.6%). Recommendation: keep gate mandatory, add per-pair calibration, consider longer lookback (60d/90d). Script: `user_data/scripts/crisis_calibration_multiyear.py`. |
| 2026-05-03 | **Queueing constraint refined (§5.6 rule 5).** Original v5.1 rule ("no implementation work until ACTIVE strategies resolve") was too blunt — created 13 days of dead time. Refined to: §6.1–§6.3 evaluation can begin immediately on new candidates; only Phase 0+ build work is gated behind §6.2 clearance. This correctly distinguishes evaluation from implementation while preserving the protection against the "sweep → build → fail" pattern (0/7). Updated in §5.6 rule 5, §5 introduction, and workflow overview. |
| 2026-05-03 | **Gate calibration on LiqCascade realized PnL (EMA200 + CRISIS gates).** 774 forward dry-run trades (V04+V05, 5 pairs, Mar 17 – May 3 2026) tagged with gate conditions using daily OHLCV data. **EMA200 gate:** 55.2% hit rate, all blocked trades were longs (price below EMA200 for entire period — bearish regime). Blocked longs: avg −0.53%, 64.2% losing. Allowed shorts: avg −0.25%, 57.6% losing. Gate correctly identified worse direction — CONFIRMED effective as directional qualifier. **CRISIS gate:** 0.0% hit rate (zero false positives during 6 weeks of active trading). Gate does not fire spuriously during "normal" crypto volatility. True-positive calibration requires multi-year dataset with actual crisis events. OI gate deferred (requires sidecar log data). Script: `user_data/scripts/gate_calibration.py`. Output: `user_data/results/gate_calibration_tagged_trades.csv`. |
| 2026-05-03 | **Sweep #6 B1 & B2 pre-deflation reads complete.** B1 (Stablecoin Netflow): found Unravel Finance and MEXC practitioner sources — signal is conceptually plausible but has ZERO quantitative validation (no backtests, no hit rates, no Sharpe). Revised estimate 30% → ~18%. B2 (IV Skew): Wang et al. 2024 paper behind paywall; Hoang & Baur 2020 not found in public search. Available public content is introductory only. Dependency on A1 (likely §6.1 fail) + BTC skew symmetry weakness (3:1 vs 10:1 for equities). Revised estimate 15% → ~8%. Aggregate expected survivors from Sweep #6 revised 0.90 → ~0.71 across all four pre-deflation reads. Process of pre-deflation reading continues to reduce estimates (every read has decreased survival), confirming sweep-time optimism bias. §8 Sweep #6 updated. |
| 2026-05-03 | **§6.2 deflation worksheet template + worked example created.** `Templates/Edge_Deflation_Worksheet_TEMPLATE.md` — blank reusable template covering all §6.2 stages (setup, Sharpe decay, fee downgrade, slippage, regime weighting, selection bias, standalone test, verdict, paper replication checklist, reopen triggers). `Templates/Edge_Deflation_Worksheet_CandidateL_WORKED_EXAMPLE.md` — same template populated from `EnhancedCointPairs_Deep_Dive.md` Part 8 as the canonical worked example. Research Log §6.2 updated with pointers to both files. |
| 2026-05-03 | **Hoyle & Shephard empirical test on LiqCascade + OracleSurfer realized PnL complete.** Per `Cursor_Next_Steps_2026-05-03.md` Item 1. LiqCascade (771 forward dry-run trades, V04+V05, extracted via SSH from droplet): ξ₀ = 0.992, γ₁ = 0.992 under EWMA (HS baseline) — HS test FAILS; trades cluster in high-vol periods (ξ₀ < 1), the convexity mechanism that makes vol scaling improve Sharpe in traditional futures is structurally absent. Shorts only (346 trades): ξ₀ = 0.878, γ₁ = 0.878 — most extreme ξ₀ < 1, HS test FAILS, but Sσ less negative than S (dampens losses). OracleSurfer: 11 trades — insufficient sample, not actionable. Implication: C1-Sharpe (naive vol targeting for Sharpe) very unlikely to pass §6.2; C1-Risk (drawdown reduction) remains viable. C1 survival estimate ~20% for Sharpe framing, ~40% for risk framing. Full report: `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md`. Analysis script: `user_data/scripts/hs_empirical_test.py`. Data extracted from LiqCascade droplet (138.197.188.16) and OracleSurfer droplet (104.248.17.129). |
| 2026-05-03 | **Sourcing Sweep #6 complete + post-sweep article reads (3 references) + Sweep #6 retrospective.** First sweep under v5.1 three-axis protocol. Four candidates queued for §6.2 deflation: C1 Conditional Vol Targeting, B1 Stablecoin Netflow Gate, A1 Crypto GEX Flow, B2 IV Skew Gate. Initial sweep estimates totaled 1.20 expected survivors (within v5.1 baseline 0–2). Developer supplied full-text PDFs of Hoyle & Shephard 2018, Yuyama et al. 2023, and the Glassnode GEX Dec 2025 article; full-text reading materially revised estimates: C1 50%→30% (Yuyama shows BTC violates the precondition for naive vol targeting to add Sharpe — risk-overlay framing more likely path than Sharpe-enhancer), A1 25%→15% (Glassnode methodology is sales-gated, requires paid Professional feed or DIY-without-benchmark; may fail §6.1 buildability), B1 and B2 unchanged. Total revised expected survivors 0.90. Article-derived deflation-relevant facts captured in §8 Sweep #6 entry to prevent silent-debt loss. C1 deflation charter split into C1-Sharpe (likely fails per Yuyama) and C1-Risk (drawdown/Calmar — more likely passes). Sweep #6 retrospective added to §8 with 4 protocol improvements for Sweep #7: enforce §6.3 population at sweep time; full-text reads required for ≥25%-survival candidates pre-sweep-conclusion; source-quality whitelist/blacklist; explicit "search NOT done" list per sweep. Lesson #19 added (sweep-time abstracts contain less failure-mode information than full-text reads). §4.6 sequencing updated: step 6 marked DONE; new step 6.5 added — Cursor session work covering Hoyle/Shephard empirical test on LiqCascade and OracleSurfer realized PnL + §6.2 worksheet template materialization. New file: `Cursor_Next_Steps_2026-05-03.md` brief for the next Cursor session. Hard queueing constraint held throughout: no implementation work on Sweep #6 candidates until LiqCascade Phase 4 resolves at ~2026-05-16. |
| 2026-05-03 | **GatedExecution Dev Plan v0.1 skeleton created.** `GatedExecution_Dev_Plan.md` drafted per §4.6 step 5. 9-part skeleton: signal interface contract (`{direction, confidence, freshness}` per pair per candle), gate catalog (4 CONFIRMED: spread/z-score, EMA200, CRISIS, OI; 4 CANDIDATE: XSMomentum rank, funding extreme, OFI, conformal; primary-signal placeholder), weighted-confidence combinator with mandatory gate veto and independence requirement, unified risk/exit (ATR trailing + ROI ladder + time stop + inverse-vol sizing), per-gate integration notes referencing existing candidate code, 5 open design questions for v1.0. Primary-signal slot invariant under both LiqCascade Phase 4 outcomes. Implementation phases deferred to v1.0 (post-Phase-4). §4.6 step 5 marked DONE; step 6 (Sweep #6) is now next-actionable. Candidate L reopen trigger (i) closed — gate confirmed. Related files list updated; memory files updated. |
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
