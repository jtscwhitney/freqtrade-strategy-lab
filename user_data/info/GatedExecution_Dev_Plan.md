# GatedExecution — Development Plan
## Synthesis Initiative from AlgoTrading Research Log §4.5
## Created: 2026-05-03 | Version: v0.1 (SKELETON)
## Status: DESIGN — primary-signal slot placeholder; resolves on LiqCascade Phase 4 outcome

> **This is a v0.1 skeleton.** Structural design, interface contracts, and gate catalog are specified. Implementation sequencing, phase gates, and exact threshold values are deferred to v1.0 after LiqCascade Phase 4 resolves (§4.6 step 8).
>
> **Primary-signal slot:** Placeholder. If LiqCascade GO → cascade detection fills this slot. If LiqCascade NO-GO → highest-conviction Sweep #6 structural-alpha candidate fills it. All other gates, risk framework, and position sizing are independent of which signal becomes primary.

---

## Quick-Start for Claude (Session Resume)

> Read `AlgoTrading_Research_Log.md` §4.5 (thesis), §4.6 (sequencing), and this Dev Plan. The canonical signal-source catalog is `AlgoTrading_Research_Log.md` §4.5 table — this Dev Plan references those entries without duplicating them.

### What This Project Is

A single Freqtrade execution layer that consumes signals from multiple independently-validated gate sources, takes a trade only when ≥ N gates agree, and uses a unified risk/exit framework. Not a strategy in the traditional sense — a gate-combination engine where every input is a transparent rule with explicit thresholds.

### Why This Exists

The pattern of drawing standalone candidates from the literature produced 0 wins in 7 attempts (F through M). Several of those failed candidates produced *partial* validated signals or reusable infrastructure. Combined under multiplicative gate logic, they may form a robust edge that no single paper-replicated strategy achieved.

### Current Phase

**DESIGN (v0.1).** No code exists. No phase gates have been run. The primary-signal slot is a placeholder. Implementation begins only after LiqCascade Phase 4 resolves.

### Key Constraint

This Dev Plan is independent of which signal becomes primary. The gate catalog, interface contract, risk framework, and position sizing model are designed to accept either LiqCascade cascade detection (GO case) or a Sweep #6 structural-alpha candidate (NO-GO case) without redesign.

---

## Part 1: Architecture

### 1.1 Core Principle

**Every input is a gate. No input is a primary signal generator.** Trades fire only when the intersection of independent gates agrees. This is structurally different from additive signal combination (RAME) and from ensemble voting on correlated indicators (Donchian J).

Statistical assumption: independent gates kill false positives multiplicatively. If gate A has a false-positive rate of 40% and gate B has a false-positive rate of 30%, and they are independent, the joint false-positive rate is ~12% — not the average of the two. Signal generators add noise additively; gates multiply selectivity.

**No learned classifier.** Every gate is a transparent rule with explicit, configurable thresholds. No ML model produces the final entry decision.

### 1.2 System Diagram

```
Gate Sources (per pair, per candle)          GatedExecutionStrategy
─────────────────────────────────────        ─────────────────────────
                                              │
  [PRIMARY SIGNAL — PLACEHOLDER]  ─────────→  │  direction, confidence
  (LiqCascade cascade OR                       │
   Sweep #6 structural-alpha)                  │
                                              │
  Spread / z-score gate (L)        ─────────→  │  direction, confidence,
                                              │    freshness
  Cross-sectional rank gate (G)    ─────────→  │  direction, confidence
                                              │
  Macro EMA200 gate                ─────────→  │  direction qualifier
                                              │
  CRISIS gate (ATR p90)            ─────────→  │  mandatory block
                                              │
  Funding extreme gate             ─────────→  │  direction qualifier
                                              │
  OI confirmation gate             ─────────→  │  direction qualifier
                                              │
  OFI confirmation gate (opt)      ─────────→  │  direction qualifier
                                              │
  Conformal prediction wrapper     ─────────→  │  confidence modifier
                                              │
                                   GATE        │
                                   COMBINATOR  │
                                   ──────────→ │  entry signal {LONG,
                                              │    SHORT, NONE}
                                              │
                                   UNIFIED     │
                                   EXIT/RISK   │
                                   ──────────→ │  trailing stop + ROI
                                              │    + time stop + sizing
```

All gate sources produce output independently. The strategy reads their union per pair per candle. The gate combinator applies `min_agreeing_gates`, per-gate weights, and mandatory flags. The unified exit/risk layer handles all position management.

### 1.3 Why Not RAME

| Aspect | RAME (Failed) | GatedExecution |
|--------|---------------|----------------|
| Signal generation | Regime labels as primary signal | No primary signal — gates only |
| Combination | Additive (regime routes to sub-strategy) | Multiplicative (intersection of independent gates) |
| Classifier | Learned (FreqAI Catboost) | None — transparent rules with explicit thresholds |
| Exit signals | Regime-change exits (destructive: 2–24% WR) | Unified ATR trailing + ROI + time stop only |
| Statistical assumption | Regime predicts direction | Gates kill false positives; no directional prediction required |

---

## Part 2: Signal Interface Contract

Every gate source MUST produce a normalized output conforming to this contract. The GatedExecution strategy reads signal files/dataframes and expects these fields per pair per candle.

### 2.1 Required Fields

```python
@dataclass
class GateSignal:
    direction: Literal['LONG', 'SHORT', 'NEUTRAL']  # trade direction this gate supports
    confidence: float                                 # [0.0, 1.0] — gate's conviction
    freshness: float                                  # [0.0, 1.0] — recency of last meaningful observation
```

**Field semantics:**

- **`direction`**: Which trade direction this gate agrees with for this candle. `NEUTRAL` means the gate abstains (no opinion). A gate voting `NEUTRAL` does NOT count toward `min_agreeing_gates` and does NOT block a trade — it is an abstention, not a veto.
- **`confidence`**: How strongly the gate supports its direction. Normalized to [0, 1]. Used for weighted gate combination (a gate with confidence 0.9 carries more weight than one with 0.5). Gate-specific calibration — each gate defines its own mapping from raw signal strength to [0, 1].
- **`freshness`**: How recent the last meaningful observation was. 1.0 = observation within the current candle or lookback window. Decays toward 0.0 as the data ages. Prevents stale signals from voting. Gates that produce per-candle output set freshness to 1.0 always. Gates that rely on external data (sidecar files, API polls) track recency explicitly.

### 2.2 Output Format

**File-based (sidecar gates):** JSON per pair, written to `user_data/data/gate_signals/{gate_name}/{pair}.json`:

```json
{
  "timestamp": "2026-05-03T14:00:00+00:00",
  "direction": "LONG",
  "confidence": 0.72,
  "freshness": 0.95
}
```

**DataFrame-based (in-strategy gates):** Column prefix convention — `gate_{name}_direction`, `gate_{name}_confidence`, `gate_{name}_freshness` added to the strategy's analyzed dataframe.

### 2.3 Mandatory vs Advisory Gates

- **Mandatory gates** (e.g., CRISIS gate): if this gate votes against a direction, the trade is blocked regardless of other votes. A mandatory `NEUTRAL` is treated as agreement (abstention ≠ veto). A mandatory gate voting `SHORT` when the consensus is `LONG` blocks the trade.
- **Advisory gates**: contribute to `min_agreeing_gates` count and weighted confidence scoring but cannot unilaterally block.

---

## Part 3: Gate Catalog

### 3.1 CONFIRMED Gates (validated signal, integration path clear)

| Gate | Signal | Status | Mandatory | Origin |
|------|--------|--------|-----------|--------|
| **Spread / z-score** | Per-pair mean-reversion: `{direction, confidence ∝ |z| above entry threshold, freshness from lookback}` | CONFIRMED (2026-05-03) | Candidate L §4.3; `EnhancedCointPairsStrategy_V01/V02.py` |
| **Macro EMA200** | Block longs below daily EMA200; block shorts above | VALIDATED (RAME → LiqCascade) | No | LiqCascade Phase 3.5 |
| **CRISIS (ATR p90)** | Block all entries when realized vol > 90th percentile rolling 30d | VALIDATED (RAME → LiqCascade) | **Yes** — always mandatory | LiqCascade Phase 3.5 |
| **OI confirmation** | OI change rate > threshold (per-pair calibrated); validated on shorts (XRP/BNB/ETH/SOL) | VALIDATED | No | LiqCascade Phase 3.5 |

### 3.2 CANDIDATE Gates (real signal, integration path defined, not yet calibrated for gate use)

| Gate | Signal | Status | Origin |
|------|--------|--------|--------|
| **Cross-sectional rank** | Top-N momentum / bottom-N anti-momentum from XSMomentum infrastructure | PARTIAL (signal weak standalone, real as gate) | Candidate G; `XSMomentumStrategy_V01.py` |
| **Funding extreme** | Block longs / favor shorts when funding > 90th percentile rolling 30d | RESEARCH | Technique 7.4 (Inan SSRN 5576424) |
| **OFI confirmation** | LOB order flow imbalance agrees with entry direction | RESEARCH (real signal, fee-incompatible standalone) | Candidate A salvage; Technique 7.3 |
| **Conformal prediction** | Tighten entries when prediction interval is narrow and one-sided | RESEARCH | Technique 7.1 |

### 3.3 PRIMARY SIGNAL — PLACEHOLDER

> **Resolves on LiqCascade Phase 4 outcome (estimated ~2026-05-16).**

| Outcome | Primary Signal | Notes |
|---------|---------------|-------|
| **LiqCascade GO** (short PF ≥ 1.0 at 50 trades) | Cascade detection sidecar event stream | Direction from liquidation imbalance; confidence from USD volume × dominance ratio; freshness from sidecar timestamp. Already producing `{LONG, SHORT, NONE}` per minute — needs `confidence` and `freshness` fields added per §2 contract. |
| **LiqCascade NO-GO** (short PF < 1.0 at 50 trades) | Highest-conviction Sweep #6 structural-alpha candidate | Sweep #6 eligible 2026-05-19 per §4.6 step 6. Must clear §6.2 deflation before filling this slot. Structural-alpha bias (Lesson #3): forced flows, information-asymmetry events, carry/basis, microstructure dislocations — terrain with a *why* before a *how*. |

**The rest of this Dev Plan is invariant under both outcomes.** The gate catalog, combinator logic, risk framework, and position sizing do not depend on which signal fills the primary slot.

---

## Part 4: Gate Combination Logic

### 4.1 Combinator Algorithm

For each pair, for each candle, after all gate signals are collected:

```
votes = {direction: weighted_confidence_sum}

for each gate in active_gates:
    if gate.signal.direction == 'NEUTRAL':
        continue  # abstention — no vote cast
    if gate.mandatory and gate.signal.direction != consensus_candidate:
        return NO_TRADE  # mandatory gate veto
    votes[gate.signal.direction] += gate.signal.confidence * gate.weight * gate.signal.freshness

# Determine consensus direction
if votes['LONG'] == 0 and votes['SHORT'] == 0:
    return NO_TRADE

consensus_direction = argmax(votes)
agreeing_gates = count of gates voting consensus_direction
total_confidence = votes[consensus_direction] / sum of all gate weights

if agreeing_gates < min_agreeing_gates:
    return NO_TRADE

if total_confidence < min_combined_confidence:
    return NO_TRADE

return ENTRY(consensus_direction, confidence=total_confidence)
```

### 4.2 Configurable Parameters

| Parameter | Type | Description | Default (v0.1) |
|-----------|------|-------------|-----------------|
| `min_agreeing_gates` | int | Minimum number of gates that must agree on direction for an entry | 2 (when primary is placeholder; revisit at v1.0) |
| `min_combined_confidence` | float [0, 1] | Minimum weighted confidence sum to enter | 0.5 |
| `gate_weights` | dict[str, float] | Per-gate multiplier on confidence | 1.0 for all (uniform); calibrate at Phase 1 |
| `mandatory_gates` | list[str] | Gates whose veto is absolute | `['crisis']` |
| `primary_gate_weight` | float | Weight multiplier for the primary signal | 1.5 (primary signal carries more weight but is not mandatory) |

### 4.3 Gate Independence Requirement

The multiplicative false-positive reduction depends on gate independence. Two gates built on the same underlying data (e.g., both derived from OHLCV momentum) do NOT provide multiplicative benefit — their errors are correlated.

**Independence audit (to be completed at v1.0):**
- Spread/z-score gate: price ratio mean-reversion → independent of liquidation flow, funding, OI
- Cascade detection: exchange forced-liquidations → independent of cointegration spread, cross-sectional momentum
- EMA200: price vs moving average → weakly correlated with most directional signals; acceptable as a qualifier
- CRISIS: realized vol → independent of direction; measures magnitude only
- Funding extreme: perp funding rate → independent of price data; derivative market structure
- OI confirmation: open interest flow → partially correlated with cascade detection (liquidations affect OI); flag for v1.0 independence check
- OFI: LOB flow → independent of OHLCV; may correlate with cascade detection at very short horizons

---

## Part 5: Unified Risk & Exit Framework

### 5.1 Exit Layer

All positions, regardless of which gates triggered entry, use the same exit framework. No gate-specific exits. No regime-change exits.

**Exit components (applied simultaneously — first to trigger wins):**

1. **ATR-based trailing stop:** `stop_price = extreme_price - N × ATR(period)` where `extreme_price` is the best price achieved since entry and `N` is a configurable multiplier. Direction-aware (for shorts, `stop_price = extreme_price + N × ATR(period)`). **Proven in LiqCascade and OracleSurfer.**

2. **ROI ladder:** Time-decaying take-profit table. Example: `{"0": 0.10, "60": 0.05, "120": 0.02, "240": 0}` — take 10% if hit in first 60 minutes, 5% in first 120 minutes, 2% in first 240 minutes, no minimum after that. Exact values TBD at Phase 1 calibration.

3. **Time stop:** Close position after `max_trade_duration_minutes` regardless of P&L. Prevents capital from being tied up in stagnant positions. LiqCascade uses 15 minutes; GatedExecution likely longer (15–120 min range based on gate composition). TBD at Phase 1.

**What is NOT included:**
- No indicator-based exits (crossover, regime change, RSI threshold)
- No per-gate exit logic
- No ML-predicted exit timing

### 5.2 Position Sizing

**Base formula:** `stake = base_stake × (target_vol / realized_vol_30d)`

- `base_stake`: configured in Freqtrade `stake_amount` or `tradable_balance_ratio`
- `realized_vol_30d`: 30-day rolling standard deviation of returns, annualized, per pair
- `target_vol`: configurable per pair (e.g., 0.30 = target 30% annualized vol per position)

**Constraints (applied after base formula):**
- `max_stake_per_pair`: hard cap as fraction of portfolio (default 0.25 = 25% max in one pair)
- `max_concurrent_trades`: total positions across all pairs (default 5)
- `max_portfolio_heat`: sum of `|stake × direction|` across all positions ≤ `max_heat_ratio` × portfolio value (default 1.0 = up to 100% gross exposure)

### 5.3 Leverage

Configurable per direction: `leverage_long` / `leverage_short`. Default 1× (spot-like). Higher leverage requires correspondingly tighter stops and lower `max_portfolio_heat`. TBD at Phase 1 based on primary signal characteristics.

---

## Part 6: Implementation Phases (Deferred to v1.0)

> **All phases below are placeholders.** Exact sequencing, gates, and success criteria will be filled in at v1.0 after LiqCascade Phase 4 resolves. This section exists to signal that the Dev Plan will follow the standard Research Log §6 structure.

| Phase | Scope | Gate | Status |
|-------|-------|------|--------|
| **0** | Fee economics sweep + regime-split backtest (per §6.4) | PF ≥ 1.0 each calendar year, net return > 0 after fees | NOT STARTED |
| **1** | Core implementation: strategy file, gate file readers, combinator, exit layer, config | Phase 0 GO + backtest stable across timeranges | NOT STARTED |
| **2** | Gate calibration: per-gate weights, confidence mappings, independence audit | Improvement over uniform weights in backtest | NOT STARTED |
| **3** | Dry-run forward test (≥ 50 closed trades, ≤ 60 calendar days) | PF ≥ 1.0, Sharpe ≥ 0.5, trade count ≥ 30/month | NOT STARTED |
| **4** | Live (if Phase 3 GO) | Same as Phase 3, monitored weekly | NOT STARTED |

---

## Part 7: Signal Source Integration Notes

### 7.1 Spread / Z-Score Gate (Candidate L)

**Reference implementation:** `user_data/strategies/EnhancedCointPairsStrategy_V01.py` and `_V02.py`.

**What to preserve:** The signal computation pipeline — cointegration test, OLS β estimation, z-score calculation, entry/exit threshold logic. Output: `{direction, confidence ∝ |z|, freshness from lookback window}`.

**What to discard:** Dual-leg execution machinery (`confirm_trade_entry`, orphan-leg watchdog, β-weighted stakes), Palazzi adaptive trailing stop, Palazzi vol filter. These are superseded by GatedExecution's unified exit framework and single-leg execution model.

**Integration path:** Extract the z-score computation into a standalone function or sidecar that writes per-pair gate signals conforming to the §2 interface contract. The GatedExecution strategy reads these signals — it does NOT run cointegration tests or manage pairs legs.

**Per-pair calibration requirement:** The CointPairs L forward experiment showed 33% OOS-positive replicas (BTC/ETH only), matching the paper universe's 35%. Per-pair calibration is mandatory — a single global z-score threshold produces different false-positive rates across pairs. The gate MUST support per-pair threshold configuration.

### 7.2 Cross-Sectional Rank Gate (Candidate G)

**Reference implementation:** `user_data/strategies/XSMomentumStrategy_V01.py` — `_build_cross_sectional_signals()` method.

**What to preserve:** Formation-period momentum ranking, top-N / bottom-N selection, continuous multiplier rather than binary on/off.

**What to discard:** Standalone entry/exit logic, holding-period management, the assumption that XSMomentum alone is sufficient for live deployment.

**Integration path:** Adapt `_build_cross_sectional_signals()` to produce gate-compatible output per pair per candle. The formation period and holding period become gate configuration parameters.

### 7.3 LiqCascade-Derived Gates

**Macro EMA200, CRISIS, OI confirmation** — already implemented in LiqCascade strategy. These are pure OHLCV (EMA200, ATR) or sidecar-derived (OI). Extract into standalone gate functions that the GatedExecution strategy calls directly — no sidecar needed for EMA200 and CRISIS; OI may require the existing LiqCascade sidecar or a lightweight poll.

### 7.4 Funding Extreme Gate (Technique 7.4)

**Evidence:** Inan SSRN 5576424. Extreme positive funding (> 0.1%/8h sustained for 3+ periods) = crowded longs = elevated unwind risk → favor shorts or block longs.

**Data:** Binance REST API `GET /fapi/v1/fundingRate`, poll every 8h. Sidecar required.

**Integration path:** Lightweight sidecar that polls funding rates every 8h, computes percentile thresholds (rolling 90d), writes per-pair gate signals. The GatedExecution strategy reads these signals alongside other gates.

### 7.5 OFI Confirmation Gate (Candidate A Salvage)

**Evidence:** LOB order flow imbalance has IC = 0.135 at 3-second horizon. Fee-incompatible as standalone. As a gate: confirms or rejects an entry direction generated by other gates, adding selectivity without adding fee cost.

**Integration path:** Lower priority. Requires LOB data feed. Only activate if false-positive rate on the gate combination is unacceptably high and OFI is demonstrably independent of the other active gates.

### 7.6 Conformal Prediction Wrapper (Technique 7.1)

**Integration path:** Wraps any ML-based gate's output. If a gate uses a point prediction internally, conformal prediction produces intervals with coverage guarantee. The wrapper then maps interval narrowness and one-sidedness to `confidence`. Plugs into the §2 interface without changing the combinator.

---

## Part 8: Open Design Questions (Resolve at v1.0)

1. **Gate output cadence:** Should all gates produce per-candle output, or should slower gates (funding, whale flow) produce per-period output that is forward-filled? Per-candle is cleaner but some gates are naturally slower. Proposal: all gates produce at their natural cadence; the combinator forward-fills the most recent non-stale signal.

2. **Direction-only vs direction+confidence voting:** The current design uses weighted confidence voting. An alternative is pure direction voting (each gate = 1 vote, majority wins). Weighted confidence is theoretically better but requires gate-level confidence calibration that is itself a source of error. Resolve at Phase 1 with synthetic gate data.

3. **Gate timeout / staleness:** How long after a gate's last update does its signal become invalid? Current `freshness` field handles this implicitly (decays to 0), but explicit timeout per gate may be simpler. Proposal: `freshness` field with per-gate configurable decay function; default linear decay over `gate_timeout_minutes`.

4. **Minimum trade count by gate combination:** When `min_agreeing_gates = 3` and only 2 gates are active for a given pair (e.g., funding gate data missing for a newly listed pair), should the system refuse to trade or fall back to `min_agreeing_gates = 2`? Proposal: refuse to trade — missing data is not a reason to loosen constraints. Configurable override per pair if justified.

5. **Correlated gate penalty:** If two gates are partially correlated (e.g., OI and cascade detection), their combined confidence should be discounted. How to measure and apply this discount? Proposal: rolling correlation of gate direction votes over a 90d lookback; if corr > 0.5, apply `discount = 1 - (corr - 0.5)` to the less-weighted gate.

---

## Part 9: Reference Files

- `AlgoTrading_Research_Log.md` §4.5 — GatedExecution thesis and signal-source table
- `AlgoTrading_Research_Log.md` §4.6 — sequencing and priority ranking
- `AlgoTrading_Research_Log.md` §7 — Techniques Library (conformal prediction, funding extreme, OFI, whale flow)
- `EnhancedCointPairs_Deep_Dive.md` Part 8 — §6.2 deflation worksheet and verdict for Candidate L
- `EnhancedCointPairs_Dev_Plan.md` — reference implementation for spread/z-score signal (FROZEN; signal computation only)
- `CrossSectionalMomentum_Dev_Plan.md` / `Deep_Dive.md` — reference for cross-sectional rank gate
- `LiquidationCascade_Deep_Dive.md` — cascade detection signal, EMA200/CRISIS/OI gate implementations
- `LOB_Microstructure_Dev_Plan.md` / `Deep_Dive.md` — OFI signal reference
- `user_data/strategies/EnhancedCointPairsStrategy_V01.py` — spread/z-score signal computation
- `user_data/strategies/XSMomentumStrategy_V01.py` — cross-sectional momentum ranking
