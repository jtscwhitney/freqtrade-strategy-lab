# Research Log Candidates — Review (Q&A)

**Purpose:** Shareable record of a review session comparing the `AlgoTrading_Research_Log.md` candidate list to prior project + independent analysis.

**Date:** 2026-03-21

---

## Question

> Based on your research / analysis, would you recommend a different set of candidates or any modifications to the existing ones in this doc: `AlgoTrading_Research_Log.md` (AlgoTrading research log — Section 4.3 CANDIDATES: A–D)?

*Context: The research log defines Candidates A (LOB + CatBoost), B (Funding rate arbitrage), C (Volatility commonality forecasting), D (CNN trend + stationarity preprocessing), plus ACTIVE Liquidation Cascade and ARCHIVED RAME.*

---

## Response

### Overall

The four candidates are **directionally right** for the stack: **microstructure (A)**, **structural carry (B)**, **vol as a layer (C)**, **ML technique (D)**. I would **not replace the set wholesale**. I **would add one major missing theme**, **tighten how two items are framed**, and **adjust priority** so the log matches the lessons already captured in Section 8 of the research log.

---

### Keep — with small modifications

#### Candidate A (LOB + CatBoost)

**Keep as top research-tier candidate.** It matches “structural / microstructure alpha” and complements liquidation cascades in spirit.

**Add to the write-up (risks / scope):**

- **Alpha vs beta:** For any short-horizon return model, add a line that you will check whether edge survives **controlling for concurrent spot/perp drift** (same concern as cascade strategies that might be “long vol / long beta” by accident).
- **Overlap with LiqCascade:** Correlation was already flagged. Extend that to: **same-day cluster counting** (one macro event → many signals) when evaluating performance, not only “LOB vs liq.”

No need to demote A; make **evaluation criteria** explicit so it passes the “clear mechanism” test under stress.

#### Candidate B (Funding / spot–perp / cross-exchange)

**Keep**, but **relabel the role** in the registry: this is a **carry / basis / funding sleeve**, not a “high ROI scalper.” That matches both the log’s own concern and the independent analysis (steady, **capital-intensive**, **infrastructure-heavy**).

**Modification:** Split mentally (and optionally in the log as B1/B2):

- **B1 — Same-venue spot vs perp basis + funding** (if wiring allows).
- **B2 — Cross-exchange funding diff** (two venues, execution + transfer risk).

Freqtrade is weak here; **“CANDIDATE + custom execution”** is honest. Worth keeping because **complementarity to LiqCascade is truly high** (income floor vs burst alpha).

#### Candidate C (Volatility commonality)

**Keep as a “meta” candidate**, not a standalone strategy — the existing text already says this.

**Modification:** Promote one sentence: **primary use case = dynamic leverage / position sizing / on-off gate** for active work (LiqCascade + future LOB), aligned with “entry quality > exit optimization” and avoiding RAME-style over-trading in wrong vol.

**Risk:** If implementation balloons, **time-box** it (e.g. “only as a filter column in sidecar,” not a full research fork).

#### Candidate D (CNN + stationarity on 15m)

**Do not treat as a full strategy candidate at equal weight to A.**

**Reason:** Matches the research log’s **Section 6 red flag** and **Lesson 1**: **~54% accuracy** without a clear **P&L / barrier / cost** story is the RAME failure mode in a new outfit.

**Recommended modification to the registry:**

- **Downgrade to:** “**Technique / preprocessing borrow**” or “**Infrastructure candidate** — apply stationarity pipeline to **economic targets** (returns, barriers), not as ‘CNN trend strategy’.”
- Optionally **merge into a future “Feature pipeline”** note rather than **CANDIDATE D** as a deployable system.

So: **keep the idea, demote the packaging.**

---

### Add — important gap vs prior analysis

#### New Candidate E: Statistical arbitrage / cointegration pairs (spread trading)

**Why add:** Independent literature and practice both support **pairs / mean-reversion on spreads** in crypto as a **distinct alpha family**: often **lower beta**, **different drawdown profile**, and **orthogonal** to cascade and LOB impulse strategies.

**Fit to constraints:**

- **Data:** OHLCV **can** start (unlike full LOB history).
- **Freqtrade:** Awkward but **possible** with informative pairs + custom logic — same class of complexity as accepting a **sidecar** for A.
- **Objective tension:** The log asks for **high trade frequency**; classical pairs can be **moderate** frequency unless you run **many** spreads — still can meet “active” if you scale breadth.

**Evaluation filter:** Score it explicitly (data PASS, Freqtrade CONDITIONAL, mechanism PASS, complementarity HIGH).

This is the **single biggest** “missing” candidate relative to the ROI analysis doc and the Kinetic-era review.

#### Optional Candidate F: Hybrid policy (supervised forecast + simple RL or rules for sizing only)

**Why optional:** Matches “RL = high ceiling, hard to validate” — **narrow scope** (sizing / exit **only**) avoids full RL pathologies. **Low priority** until A or E has a working baseline.

**Risk:** Easy to scope-creep; keep **PAUSED** until you have **clean labels** (barrier / return) and **honest backtests**.

---

### Sweep log / “not promoted” list

**Worth adding to Section 7 as “watchlist,” not candidates:**

- **Stat arb / pairs** — now promoted to **Candidate E** if you agree.
- **Pure RL** — sweep already cited an underperforming RL paper; **keep as caution**, not as a fourth pillar until environment + reward are nailed.

**Search terms:** Add `pairs trading cryptocurrency`, `cointegration crypto`, `spread trading perpetual`.

---

### Summary table

| Item | Action |
|------|--------|
| **A** LOB + CatBoost | Keep; add **beta/alpha check** + **event clustering** in evaluation |
| **B** Funding / basis | Keep; frame as **carry sleeve**; note **B1/B2** split; **custom execution** |
| **C** Vol commonality | Keep as **filter/sizing layer**; **time-box** |
| **D** CNN 15m | **Demote** to preprocessing / technique; **not** equal to A as deployable strategy |
| **New E** Pairs / stat arb | **Add** as major candidate |
| **Optional F** Hybrid RL sizing | **Add** as low-priority optional |

---

### File location note

The reviewed copy may live under a local WhatsApp transfers path; the research log preamble points to **`user_data/info/AlgoTrading_Research_Log.md`** as the canonical location for version control. Sync edits there when convenient.

---

### Bottom line

**Do not** swap A/B/C for a completely different set; **add pairs/stat arb (E)**, **demote D’s strategic status**, **sharpen B and C’s roles**, and **slightly harden A’s evaluation language**. That aligns the research log with both archived project lessons and the independent ROI analysis.

---

*End of document.*
