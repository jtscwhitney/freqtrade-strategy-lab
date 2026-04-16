# Research Audit — Findings and Path Forward

**Date:** 2026-04-17
**Auditor:** Claude Opus 4.7 (extended thinking, "xhigh" budget)
**Scope:** Full review of `AlgoTrading_Research_Log.md` v4.3 and ancillary candidate documentation in `user_data/info/`
**Outputs:**
1. This document — standalone summary of findings + go-forward
2. `AlgoTrading_Research_Log.md` — restructured to v5.0 incorporating recommendations
3. `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md` — frozen prior version

---

## TL;DR

1. **Process and documentation are exceptional. Candidate-discovery results are not.** Five strategies archived in five weeks; two parked at Phase 0; two active but neither yet profitable. The 7-point evaluation filter has a 0/4 confirmed hit rate among PASS / STRONG PASS candidates that reached Phase 0.
2. **The filter is the problem, not the candidates.** It scores buildability and literature plausibility — both necessary, neither sufficient to predict edge at our retail fee tier in our forward conditions. Two STRONG PASS (7/7) candidates failed Phase 0 outright.
3. **The path forward is to fix the gate, refocus effort on the one strategy with confirmed real signal (LiqCascade), and pivot toward synthesis (combining validated sub-signals from archived candidates) instead of repeatedly drawing fresh papers.**

---

## 1. The Hit-Rate Problem

| Status | Count | Strategies |
|---|---|---|
| ARCHIVED — Phase failure | 5 | RAME, LOB, CointPairs, Path Sigs, AdaptiveTrend |
| PARKED — Phase 0/1 NO-GO | 2 | XSMomentum, Donchian Ensemble |
| ACTIVE — still negative | 2 | LiqCascade (PF 0.47, refining), OracleSurfer (PF 0.31 v12; v14 unproven) |
| CANDIDATE / INVESTIGATION | 2 | Enhanced CointPairs (deferred), ShortBias Momentum (downgraded) |

**0 wins in 7 fully-evaluated strategies.** This is a directional signal about the process itself.

The 7-point Buildability Filter score history:

| Candidate | Filter Score | Phase 0 Outcome |
|---|---|---|
| F (CointPairs) | 6/7 + 1 cond | Phase 1 FAIL |
| E (Path Sigs) | 6/7 + 1 cond | Phase 1 FAIL |
| **G (XSMomentum)** | **7/7 STRONG PASS** | **Phase 1 FAIL** |
| **J (Donchian)** | **7/7 STRONG PASS** | **Phase 0 NO-GO** |
| M (AdaptiveTrend) | 6/7 + 1 cond | Phase 0 NO-GO |
| L (Enhanced CP) | 5/7 + 1 cond | not yet attempted |

Both 7/7 STRONG PASS candidates failed. The filter is decoupled from forward performance.

---

## 2. Five Structural Weaknesses in the Prior Approach

### 2.1 The 7-point filter scores buildability, not edge
It correctly rejects infeasible candidates. It does not reject candidates whose paper-stated edge will not survive the retail-fee-tier / regime / selection-bias deflation.

### 2.2 Source pipeline has severe publication bias
SSRN/arXiv crypto papers are systematically optimistic: in-sample, favorable regime windows (often pre-2022 bear), institutional fee assumptions, single-pair selection from larger universes (Palazzi: best of 37; M: paper claims SR 2.41 depends on 150-pair universe + monthly rotation; G: dependent on regime mix). The base rate of replicable edge in this pipeline is plausibly 5–10% — the filter does not deflate accordingly.

### 2.3 Candidate N (ShortBias) was promoted from a backtest noise artifact
+26.6% on 6 pairs short-only over 2022–2025 — a window dominated by a single −70% bear move — is consistent with naive short-beta capture. The prior log (v4.3) elevated this to #1 priority directly from a failed strategy's sub-leg result. That is a textbook source of false candidates.

### 2.4 Effort allocation is inverted
~80% of the last 5 weeks went to literature → MVP → fail loops on novel candidates. The one strategy with confirmed real signal (LiqCascade cascade detection) has had relatively little iteration. PF 0.47 with 60.7% time-stop rate is a known, addressable problem class with high marginal EV.

### 2.5 The "active trader frequency" objective selects against likely winners
Per-strategy frequency floor pushes toward intraday designs that get killed by retail fees (LOB) or by lack of mean-reversion at sub-daily TFs (CointPairs). Cross-asset literature is consistent: highest replicable Sharpes live at daily-to-weekly horizons. CointPairs failed partly on a frequency criterion (0.05 trades/day) — but a portfolio of 10 such spreads at daily granularity would meet a portfolio-level frequency requirement easily.

---

## 3. Seven Recommendations (now incorporated into v5.0)

| # | Recommendation | Where it lives in v5.0 |
|---|---|---|
| 1 | **Reweight effort 70/30** toward LiqCascade + OracleSurfer iteration | §4.6 Effort Allocation |
| 2 | **Add a Phase −1 Edge Deflation Pass** before any Dev Plan work | §6.2 (Sharpe ×0.5, fee tier downgrade, slippage layer, regime weighting, selection bias) |
| 3 | **Stop promoting sub-leg artifacts as candidates.** Demote N to INVESTIGATION pending regime-split + benchmark-spread test | §4.4 Candidate N (4 explicit investigation steps) |
| 4 | **Reframe the frequency objective** to portfolio-level (≥30 trades/month at portfolio sum), allowing daily-granularity individual strategies | §2 Objectives revised |
| 5 | **Build a synthesis layer (GatedExecution), not the next standalone** | §4.5 Synthesis Initiative, with 8-source signal table and architecture sketch |
| 6 | **Reduce sweep cadence, increase per-paper rigor** (≤15 papers/sweep, target a specific gap, populate Paper Replication Checklist at sweep time) | §5.6 Sourcing Sweep Protocol; §6.3 Paper Replication Checklist |
| 7 | **Add Filter Precision Tracking and a Workflow Kill Criterion** | §6.5 + §6.6 |

---

## 4. The New Multi-Stage Gate (v5.0 §6)

A candidate must clear all four stages, in order, before reaching ACTIVE deployment:

```
Stage 1: Buildability Filter (≥5/7) ────► REJECT if fail
        │
        ▼
Stage 2: Edge Deflation Pass ──────────► REJECT or refer to GatedExecution
        │  • Sharpe × 0.5 (Falck & Rej post-pub decay)
        │  • Fee tier recompute at our 10 bps round-trip
        │  • Slippage layer (2/5/15/30 bps by liquidity tier)
        │  • Regime weighting (33% bear / 34% sideways / 33% bull)
        │  • Selection bias adjustment (best-of-N → portfolio-avg)
        │  Pass: deflated ann return > 25% AND Sharpe > 1.0 AND MDD < 30%
        ▼
Stage 3: Paper Replication Checklist ──► Surface hidden assumptions (10 questions)
        │
        ▼
Stage 4: Phase 0 Empirical Gate ───────► REJECT if fail
        │  • Fee economics sweep (existing Technique 7.3)
        │  • Regime-split (PF > 1.0 in ≥2/3 years)
        │  • Per-pair PF distribution (≥50% of pairs > 1.0)
        │  • Beats buy-and-hold of universe by ≥5% absolute
        ▼
Phase 1+ implementation
```

**Meta-stages:**
- §6.5 Filter Precision Tracking — log every filter outcome to monitor v5.0's own accuracy.
- §6.6 Workflow Kill Criterion — if 0/3 next §6.2-passing candidates reach ACTIVE, halt new candidate evaluation and run a process retrospective (potential v6.0 release).

---

## 5. The GatedExecution Synthesis Initiative (v5.0 §4.5)

The single biggest architectural shift in v5.0. Instead of repeatedly drawing standalone candidates from the literature (0 wins in 7 attempts), build a single Freqtrade execution layer that combines validated sub-signals from prior work as **gates** (not signal generators).

| Source | Signal | Status |
|---|---|---|
| Cascade detection | LiqCascade sidecar event stream | VALIDATED, refining selectivity |
| Cross-sectional rank gate | XSMomentum top/bottom-N | PARTIAL — weak standalone, real as a gate |
| Funding extreme gate | >90th percentile funding rate | RESEARCH (Inan SSRN) |
| Macro EMA200 | Below daily EMA200 → block longs | VALIDATED |
| CRISIS gate (ATR p90) | Block all when realized vol > p90 | VALIDATED |
| OI confirmation | OI change rate > threshold | VALIDATED on shorts |
| OFI confirmation | LOB order flow direction agrees | RESEARCH (real signal, fee-incompatible standalone) |
| Conformal prediction wrapper | Tighten when interval narrow + one-sided | RESEARCH |

**Why structurally different from RAME (which used regime *labels* as primary signals):**
- Every input is treated as a *gate*, never a primary signal.
- Trades fire only when an *intersection* of independent gates agrees.
- Gates kill false positives multiplicatively; signal generators add noise additively.
- No learned classifier; every gate is a transparent rule with explicit thresholds.

**First Dev Plan trigger:** When LiqCascade Phase 4 returns either a clean GO (cascade signal becomes the primary gate) or a clean NO-GO (alternative primary gate must be designed). Estimated calendar: late April to mid-May 2026.

---

## 6. Concrete Diff vs Prior Log

| Section | v4.3 | v5.0 |
|---|---|---|
| Roles (§1) | "push back, propose alternatives" | + "track empirical accuracy of own methods" |
| Objectives (§2) | "scalping frequency" / per-strategy | Portfolio-level ≥30 trades/month; individual strategies may be daily |
| Stack (§3) | Fee tier implicit in Lessons | Fee tier (10 bps round-trip) in main constraint table |
| Active (§4.1) | LiqCascade + OracleSurfer (no priority signal) | + "v5.0 priority: #1/#2 effort allocation" |
| Archived (§4.2) | Verbatim | Verbatim + v5.0 reframing notes (CointPairs frequency criterion no longer kill; AdaptiveTrend short leg goes to INVESTIGATION) |
| Parked (§4.3) | Mixed in with Candidates | Separate section; reusable artifacts catalogued for GatedExecution |
| Candidates (§4.4) | N=#1 (from sub-leg artifact); L=#2 | N=INVESTIGATION (4 required steps); L=deferred pending GatedExecution design |
| GatedExecution synthesis | — | NEW §4.5; 8-source signal table; architecture sketch; trigger and sequencing |
| Priority Ranking (§4.6) | candidate ordering | Effort allocation rule (70/30) + sequenced action list |
| Sourcing (§5) | Cadence ~biweekly, ~30 papers per sweep | §5.6 protocol: ≤15 papers, target specific gap, populate §6.3 at sweep time |
| Evaluation (§6) | 7-point filter only | Multi-stage gate (§6.1 buildability + §6.2 edge deflation + §6.3 paper replication checklist + §6.4 phase 0 empirical + §6.5 filter precision tracking + §6.6 workflow kill criterion) |
| Techniques (§7) | catalogue | + cross-references to GatedExecution gate roles |
| Lessons (§9) | 14 lessons | + #15 buildability ≠ edge; + #16 sub-leg artifacts ≠ candidates; + #17 archetype-level base rate |

---

## 7. Next-Session Action Checklist

**Order matters. Do not parallelize.**

### Step 1 — Candidate N Investigation (≤ 1 day)
Run V01 short-only (`can_short=True`, drop long entries) on 6 large-cap pairs, split by year. Produce a single results table:

| Year | Trades | PF | Return | WR | MDD | Short BnH return | Spread (strat − BnH) |
|---|---|---|---|---|---|---|---|
| 2022 | | | | | | | |
| 2023 | | | | | | | |
| 2024 | | | | | | | |

**Decision rule:**
- Spread > +5% in ≥ 2/3 years → run with EMA(200)-on-daily macro filter, then promote to CANDIDATE eligible for §6 evaluation
- Spread < +5% or negative in 2+ years → ARCHIVE permanently (was beta capture, not edge)

Commands referenced in `project_adaptivetrend.md`.

### Step 2 — LiqCascade Phase 3.5 Reassessment (2026-04-20 checkpoint)
Pull V05 dry-run results since 2026-04-06 (10–14 days of forward data). Apply Phase 4 gate criteria:
- PF > 1.0
- WR > 40%
- Time-stop rate < 50%

If GO → draft Phase 4 hyperopt plan. If NO-GO → analyze whether to tighten OI threshold further OR revert and rebuild the entry signal architecture.

### Step 3 — OracleSurfer v14 Mid-Window Check
At 8 closed v14 trades (estimated mid-May 2026 at v12-equivalent frequency), check WR. If < 30%, pause and diagnose. Otherwise continue to 15-trade gate.

### Step 4 — Deflation Pass on Candidate L (1 session)
Apply §6.2 deflations to Palazzi 2025 results. Document in a `Candidate_L_Deflation_Pass_<date>.md` file. Decide: re-promote as portfolio-of-pairs Candidate, fold into GatedExecution as market-neutral signal layer, or shelve permanently.

### Step 5 — GatedExecution Dev Plan v0.1 (1 session, only after Step 2 outcome known)
Draft `GatedExecution_Dev_Plan.md` per §4.5 architecture, using whichever primary signal source the LiqCascade Phase 4 outcome justifies.

### Step 6 — Sourcing Sweep #6
**Defer until Step 5 is drafted OR until 2026-05-29, whichever later.** Follow §5.6 protocol when run.

---

## 8. What This Audit Is Not

- **Not a recommendation to abandon the project.** The infrastructure, documentation, lesson capture, and ability to fail fast are all genuinely strong. The pipeline is the problem; the discipline is not.
- **Not a recommendation to abandon novel candidates entirely.** Sweep #6 still happens. The sweep cadence is reduced and the per-paper rigor is increased; the door is not closed.
- **Not a claim that the v5.0 gate will work.** It is an explicit hypothesis: that a multi-stage gate including edge deflation will improve the 0/4 hit rate. §6.5 tracks the answer. §6.6 says what to do if it doesn't.

---

## 9. Bottom Line

The last 5 weeks produced excellent process artifacts and zero profitable strategies. The next 5 weeks should produce fewer process artifacts, focused iteration on LiqCascade and OracleSurfer, an honest investigation of Candidate N, and a draft of the GatedExecution synthesis. The new evaluation gate is a hypothesis, not a guarantee — but it is at least a hypothesis tied to the empirical failure modes we have actually observed.

If the v5.0 gate produces 0/3 wins on its first 3 fully-evaluated candidates, §6.6 says we revise the process again. The willingness to do that — to treat the meta-process as itself a hypothesis under test — is the most important thing v5.0 introduces.

---

*End of audit document. Source: `AlgoTrading_Research_Log_v4.3_archive_2026-04-17.md` (read in full) and ancillary candidate documentation. Restructured Research Log: `AlgoTrading_Research_Log.md` v5.0.*
