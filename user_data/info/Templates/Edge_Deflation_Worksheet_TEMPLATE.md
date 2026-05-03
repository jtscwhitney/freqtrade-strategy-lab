# §6.2 Edge Deflation Worksheet — TEMPLATE

## Purpose
This is the reusable worksheet for performing an Edge Deflation Pass (§6.2) on a candidate strategy. Each candidate must clear this pass before proceeding to a Dev Plan per `AlgoTrading_Research_Log.md` §6.

## When to use
When a candidate has cleared §6.1 Buildability Filter (≥5/7) and is ready for the mandatory §6.2 deflation pass. Populate one worksheet per source paper per candidate.

## How to use
1. Copy this file and rename to `Edge_Deflation_Worksheet_{CandidateName}.md`
2. Fill in all sections. Items marked `⚠ inferred` require a re-read of the source paper before the conclusion is firm.
3. The worksheet should be attached to the candidate's Dev Plan or Deep Dive per §6.3 ("Output: a 1-page summary per candidate").
4. Cross-reference the worked example at `Templates/Edge_Deflation_Worksheet_CandidateL_WORKED_EXAMPLE.md`.

---

## Header

| Field | Value |
|-------|-------|
| Candidate name | [e.g., "Candidate X"] |
| Source paper(s) | [full citation] |
| Date worksheet started | [YYYY-MM-DD] |
| Status | [IN PROGRESS / COMPLETE] |
| Evaluator | [Claude model version + session context] |
| Inputs available | [list: paper files, lab backtests, forward results, etc.] |
| Inputs NOT available | [list: papers not on disk, missing data windows, fee assumptions] |

---

## §6.2.1 Setup — Claimed Edge

What does the paper claim? In the paper's own framing, what is the edge and why does it exist?

- **Headline metric:** [e.g., "Sharpe 1.5", "annual return 25%"]
- **Mechanism claimed:** [1-3 sentences on why the edge exists]
- **Universe / pairs / time horizon:** [what does the paper test on?]
- **Test window:** [what dates? includes bear 2022? bull 2024–25?]
- **Fee assumption:** [what fee tier? per-side or round-trip?]

---

## §6.2.2 Sharpe / Return Decay (§6.2.1 in Research Log)

Apply the post-publication decay factor.

- **Default decay factor:** 0.5 (Falck & Rej 2022)
- **Override?** [Yes/No + documented reason if yes]
- **Input Sharpe:** [paper headline]
- **Input annual return:** [paper headline, or ⚠ inferred]
- **After decay:** Sharpe = `____`, return = `____`

---

## §6.2.3 Fee-Tier Downgrade (§6.2.2 in Research Log)

Recompute paper's results at our fee tier.

- **Paper's assumed fee:** [bps/side or round-trip; ⚠ inferred if not confirmed]
- **Our fee:** 10 bps round-trip taker (Binance retail futures). For dual-leg strategies: 20 bps per spread cycle.
- **Fee delta:** `____` bps
- **Turnover proxy:** [trades/yr estimated from paper or lab backtest]
- **Annual drag from fee delta:** `turnover × fee_delta / 10000 = ____ %/yr`
- **After fee downgrade:** return = `____`, Sharpe = `____`

---

## §6.2.4 Slippage Layer (§6.2.3 in Research Log)

Add slippage beyond the taker fee.

- **Slippage per trade by pair class:**
  - Liquid majors (BTC, ETH): 2 bps RT
  - Liquid alts (SOL, BNB, XRP): 5 bps RT
  - Mid-caps: 15 bps RT
  - Small-caps: 30+ bps RT
- **Paper's universe composition:** [breakdown]
- **Weighted slippage per trade / cycle:** `____` bps
- **Annual slippage drag:** `turnover × slippage / 10000 = ____ %/yr`
- **After slippage:** return = `____`, Sharpe = `____`

---

## §6.2.5 Regime Weighting (§6.2.4 in Research Log)

Re-weight returns by expected forward regime mix.

- **Regime mix (standard):** 33% bear (≈2022), 34% chop (≈2023), 33% bull (≈2024–25)
- **Paper reports per-regime splits?** [Yes/No — if no, ⚠ flag, require Phase 0 regime-split backtest]
- **Regime returns (paper or lab):**
  | Regime | Weight | Return |
  |--------|--------|--------|
  | Bear-like | 33% | ___ |
  | Chop/sideways | 34% | ___ |
  | Bull-with-corrections | 33% | ___ |
- **Weighted return:** `____ %/yr`
- **After regime weighting:** return = `____`, Sharpe = `____`

---

## §6.2.6 Selection Bias / Multiple Testing (§6.2.5 in Research Log)

Assess whether the headline result is selection-biased.

- **Universe selection:** [pre-specified and fixed? current market-cap selection? best-of-N?]
- **Parameter optimization:** [walk-forward? in-sample grid search? test-window fitting?]
- **If best-of-N across pairs/params:** penalty = `(1/N)^0.3`
- **N =** `____`, penalty = `____`
- **Adjusted headline:** [multiply or divide Sharpe/return by penalty as appropriate]
- **Use portfolio average, not best-pair:** [applicable? Y/N]
- **After selection bias:** return = `____`, Sharpe = `____`

---

## §6.2.7 Standalone Economic Test (§6.2.6 in Research Log)

Does the candidate clear the pass threshold after ALL deflations applied sequentially?

- **Pass threshold:** deflated annual return > 25% AND deflated Sharpe > 1.0 AND deflated MDD < 30%
- **Final deflated return:** `____ %/yr`
- **Final deflated Sharpe:** `____`
- **Final deflated MDD:** `____` (⚠ inferred if paper doesn't report)
- **PASS / FAIL:** [ ]

If FAIL: is there a discrete signal that could plug into GatedExecution (§4.5)?

---

## §6.2.8 Verdict

One of:
- **(a) PASS — promote to §6.3 Paper Replication Checklist**
- **(b) NARROW — fold into GatedExecution as sub-signal/gate**
- **(c) FAIL — archive, document lessons**

**Verdict:** [a / b / c]

**Rationale:** [3-5 sentences on why this verdict]

**What carries forward:** [specific signal, code, infrastructure]

**What is intentionally NOT preserved:** [what to discard, why]

---

## §6.2.9 Paper Replication Checklist (§6.3 in Research Log)

Populate at sweep time if possible. If deferred, fill in now.

| # | Question | Answer / Note |
|---|----------|---------------|
| 1 | What exact fee tier does the paper assume? Per-side or round-trip? | |
| 2 | What exact data window? Does it include 2022 bear? 2024–2025 bull? | |
| 3 | Is the universe survivorship-biased? | |
| 4 | Are entry/exit times daily-close-to-close, or accounting for slippage and execution latency? | |
| 5 | What's the parameter optimization protocol? In-sample, walk-forward, or test-window? | |
| 6 | What's the reported MDD definition? Peak-to-trough on returns or on equity? | |
| 7 | Does the paper report regime splits (bull / bear / sideways)? | |
| 8 | Is there a single "best" parameter set or "best" pair selection? What's the dispersion? | |
| 9 | What's the live / forward-test track record (post-publication)? | |
| 10 | What infrastructure does the paper assume (low-latency, prime broker, custom matching)? | |

---

## §6.2.10 Reopen Triggers

What new evidence would justify revisiting this verdict?

1. [specific trigger condition]
2. [specific trigger condition]
3. [explicitly NOT triggers: open-ended hyperopt, "one more month of data"]
