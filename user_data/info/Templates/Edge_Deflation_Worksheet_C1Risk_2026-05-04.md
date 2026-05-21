# §6.2 Edge Deflation Worksheet — Candidate C1-Risk (Conditional Volatility Targeting)

> Populated from `AlgoTrading_Research_Log.md` v5.1.2 §4.4 Candidate C1 entry and the pre-deflation H&S empirical test on actual LiqCascade PnL. First overlay-class candidate to receive a §6.2 pass — surfaced a protocol gap (§6.2.6 standalone thresholds don't apply to overlays); resolution applied per §6.2.6 last-bullet referral pattern (same as Candidate L). See "Process notes" at end for the recommended §6.2.6 amendment.

---

## Header

| Field | Value |
|-------|-------|
| Candidate name | C1 — Conditional Volatility Targeting (split into C1-Sharpe and C1-Risk sub-charters) |
| Source paper(s) | 1. Hoyle & Shephard 2018 (SSRN 3279787) — "Volatility scaling's impact on the Sharpe ratio" — theoretical framework. 2. Yuyama et al. 2023 (SSRN 4548964) — "The effectiveness of volatility control strategies in incorporating crypto or digital assets into portfolios" — crypto-specific empirical evidence on portfolios containing BTC, 2016–2022. |
| Date worksheet started | 2026-05-04 |
| Status | COMPLETE |
| Evaluator | Claude Opus 4.7 + developer session 2026-05-04 (web-based) |
| Inputs available | Both source PDFs uploaded and read in full this session. Pre-deflation diagnostic `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md` covering 771 LiqCascade V04+V05 closed dry-run trades. C1 deflation framing from Research Log §8 Sweep #6 (split into C1-Sharpe and C1-Risk on 2026-05-03). |
| Inputs NOT available | V06 production PnL distribution (V06 currently soaking; ~50-trade Phase 4 mark expected ~2026-05-16). OracleSurfer sample is far below 50-trade minimum (n=11) — not actionable. Operationalization spec for vol-scaling-as-strategy-overlay (Yuyama operates in a portfolio framework; translation to per-trade strategy semantics not yet written). |

---

## §6.2.1 Setup — Claimed Edge

This candidate has **two sub-charters** with distinct claims; they must be evaluated separately.

### C1-Sharpe (Sharpe-improvement claim — based on Hoyle & Shephard 2018)
- **Headline metric:** H&S empirical work shows mean γ₁ ≈ 1.33 (median 1.08) across 142 futures and forwards markets, with mean ξ₀ ≈ 1.36. Where γ₁ > 1, vol scaling improves the unconditional Sharpe ratio (H&S Theorem 2). Implication: vol scaling typically improves Sharpe in traditional asset markets.
- **Mechanism claimed:** Convexity of the precision process σ⁻¹ₜ (Jensen's inequality) plus timing covariance between σ⁻¹ₜ and conditional mean. The convexity term ξ₀ alone is typically ≥ 1 and dominates the result; ξ₁ is more variable and often modestly negative.
- **Universe / pairs / time horizon:** 142 futures and forward markets across 7 categories (agricultural, bonds, currencies, energy, equities, metals, short rates). 30 years daily data (1988–2017).
- **Test window:** 1988–2017. Predates crypto's full history.
- **Fee assumption:** None directly modeled — H&S explicitly defers transaction-cost analysis to a follow-on paper (their §5).

### C1-Risk (drawdown-reduction claim — based on Yuyama et al. 2023)
- **Headline metric:** Statistically significant (1% level) reductions in standard deviation, VaR(5%), CVaR(5%), and Maximum Drawdown across all four allocation methods (1/N, BL, MK, RP) and all five VC strategies. Best Max DD reduction at VC(4) (0.5% target, 30-day measurement): total-period MDD reduces from −0.131/−0.205/−0.343/−0.075 (1/N/BL/MK/RP reference) to −0.032/−0.038/−0.055/−0.026 — **roughly 60–80% MDD reduction** depending on allocation method.
- **Mechanism claimed:** Vol scaling reduces exposure during high-vol periods. For a portfolio containing BTC, this primarily reduces BTC's contribution during high-vol windows while leaving the bond/equity/gold sleeves intact. Result: portfolio risk is reduced even though BTC violates the standard "high-vol = low-return" precondition (Yuyama explicitly notes BTC has high-risk-and-high-return, low-risk-and-low-return — opposite of what makes vol scaling improve Sharpe).
- **Universe / pairs:** 7-asset traditional portfolio (US/EU/HK/CN/JP equities + gold + 20+yr Treasury) plus BTC. Daily granularity.
- **Test window:** 2016-01-04 to 2022-12-30 daily, weekday-only. Includes 2018 crypto winter, 2020 COVID, 2021 bull peak, 2022 crypto winter.
- **Fee assumption:** 10 bps per transaction (interpreted as round-trip per Section 3.3.2). **Matches our 10 bps assumption.**

### Pre-deflation diagnostic on actual project PnL

H&S empirical test on 771 LiqCascade V04+V05 closed dry-run trades (full report: `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md`):

| Sample | EWMA ξ₀ | EWMA γ₁ | HS test | Sσ − S |
|---|---|---|---|---|
| Combined V04+V05 (771 trades) | 0.992 | 0.992 | FAIL | +0.002 |
| Shorts only (346) | 0.878 | 0.878 | FAIL | +0.020 |
| Longs only (425) | 1.210 | 1.210 | PASS-but-S<0 | −0.069 |

**Key finding for C1-Sharpe:** ξ₀ < 1 under EWMA on the combined sample and on shorts. LiqCascade trades cluster in high-volatility periods. The convexity mechanism that makes vol scaling improve Sharpe in H&S's 142-market dataset (mean ξ₀ ≈ 1.36) is structurally absent in this PnL.

**Key finding for C1-Risk:** ξ₀ < 1 means high-vol periods are exactly where the strategy has its worst returns. Yuyama's risk-reduction mechanism — reduce exposure during high-vol periods — operates exactly where it would help most. This is a *positive* transfer for the risk-reduction claim, even as it confirms the *negative* result for the Sharpe-improvement claim.

---

## §6.2.2 Sharpe / Return Decay (§6.2.1 in Research Log)

### C1-Sharpe
- **Default decay factor:** 0.5 (Falck & Rej 2022)
- **Override?** No — H&S 2018 is post-publication 7+ years; standard decay applies.
- **Input headline:** mean γ₁ ≈ 1.33 in H&S's empirical distribution → expected Sσ − S typically positive.
- **After decay:** N/A — **the project-specific empirical test (771 actual trades) supersedes the literature decay.** Our ξ₀ = 0.992 directly measures the relevant quantity in our system. The literature would give us a generic prior of "γ₁ > 1 likely"; the empirical test tells us γ₁ ≈ 1 in our system. Decay applied to the literature is moot when the project-specific evidence is direct.
- **Conclusion:** **C1-Sharpe REJECTED.** No Sharpe improvement to harvest in our PnL. H&S's class-level result simply does not transfer.

### C1-Risk
- **Default decay factor:** 0.5 (Falck & Rej 2022)
- **Override?** No — Yuyama 2023 is post-publication ~2.5 years; standard decay applies.
- **Application to risk-reduction claim:** Apply 0.5 decay to the **MDD-reduction magnitude** rather than to a Sharpe/return number. Defensible because (a) the Falck & Rej result is about post-publication decay of *edges*; an overlay's edge is its risk-reduction magnitude; (b) Yuyama's result is non-trivial enough to be subject to the same skepticism — practitioners have likely incorporated similar techniques since publication.
- **Input headline:** Yuyama VC(4) MDD reduction = 60–80% (across 1/N/BL/MK/RP allocations).
- **After decay:** **30–40% MDD reduction expected** as the headline before further deflations.

---

## §6.2.3 Fee-Tier Downgrade (§6.2.2 in Research Log)

### C1-Sharpe
- **N/A** — already rejected at §6.2.2 on direct empirical grounds.

### C1-Risk
- **Paper's assumed fee:** 10 bps per transaction (Yuyama §3.3.2).
- **Our fee:** 10 bps RT taker. **Match.**
- **Crucial divergence:** Yuyama operates in a daily-rebalance portfolio framework with rebalance every 10 trading days, which adds rebalance trades. **Vol scaling applied per-entry on LiqCascade does NOT add transaction costs** — it modifies the size of trades that would happen anyway. No additional turnover relative to the underlying strategy.
- **Fee delta:** ~0 bps if operationalization specifies per-entry-only scaling.
- **Operationalization constraint:** Per-entry-only scaling (no separate rebalance trades) must be specified in the Phase 0 spec to preserve this property. Folded into §6.2.11 reopen trigger #2 below.
- **After fee downgrade:** No change to the 30–40% MDD reduction estimate.

---

## §6.2.4 Slippage Layer (§6.2.3 in Research Log)

### C1-Sharpe
- **N/A** — already rejected.

### C1-Risk
- **Paper's universe slippage:** Yuyama assumes 10 bps inclusive of slippage on a basket of liquid majors (BTC, US/EU/HK/CN/JP equity ETFs, gold spot, TLT). Reasonable.
- **Application to LiqCascade:** Slippage applies to the *underlying strategy's trades*, which already include slippage in their realized PnL (LiqCascade backtests use 5 bps for liquid alts per §6.2.3 standard). The vol-scaling overlay does not introduce additional trades, so it does not introduce additional slippage.
- **Second-order effect:** Smaller position sizes might marginally improve slippage (less market impact), but this is a small effect — ignore.
- **After slippage:** No change to the 30–40% MDD reduction estimate.

---

## §6.2.5 Regime Weighting (§6.2.4 in Research Log)

### C1-Sharpe
- **N/A** — already rejected.

### C1-Risk
- **Yuyama's data:** 2016–2022 inclusive of 2018 crypto winter, 2020 COVID, 2021 bull peak, 2022 crypto winter. Per-year tables (Tables 6–10 in Yuyama) report results separately for each year.
- **Per-regime risk reduction (selected from Yuyama Table 9 VC(4), 1/N allocation):**

  | Year (regime proxy) | Reference MDD | VC(4) MDD | Reduction |
  |---------------------|---------------|-----------|-----------|
  | 2018 (bear) | −0.077 | −0.029 | 62% |
  | 2020 (chop+shock) | −0.131 | −0.032 | 76% |
  | 2022 (bear) | −0.104 | −0.027 | 74% |

- **Robustness check:** MDD reduction holds in 2018 and 2022 (worst BTC years) — the windows where overlay effectiveness matters most. The reduction is strongest in the most volatile periods, not weakest.
- **Standard regime mix (33% bear / 34% chop / 33% bull) applied:** Already embedded in Yuyama's 60–80% multi-year average. No further deflation needed for the *risk-reduction* claim.
- **⚠ Caveat for return:** Yuyama also shows return reduction is worse in 2018 and 2022 (vol scaling reduces upside in bull years too). Captured in §6.2.6 below (underlying-EV precondition).
- **After regime weighting:** No change to 30–40% MDD reduction estimate.

---

## §6.2.6 Selection Bias / Multiple Testing (§6.2.5 in Research Log)

### C1-Sharpe
- **N/A** — already rejected.

### C1-Risk
- **Yuyama's design:** Reports results across all 4 × 5 = 20 cells (allocation × VC-strategy), all showing significant risk reductions. This is the **opposite of selection bias** — robustness across the design space.
- **No (1/N)^0.3 penalty applied** — there is no best-of-N selection on the headline result.
- **⚠ Caveat:** The five VC strategies vary substantially in *return* outcomes (VC(4) produces the worst returns; VC(3) the best). If we calibrate to the "best" VC strategy on returns, that's selection bias. **Operationalization spec must commit to one VC variant ex ante.** Defensible default: VC(4) at 0.5% target, since that's where the headline MDD reduction is strongest and risk reduction is the goal of an overlay.
- **After selection bias:** No change to 30–40% MDD reduction estimate.

### C1-Risk-specific deflations (overlay-class concerns at this stage)

The standard §6.2.1–§6.2.5 deflations are largely vacuous for an overlay-class candidate because there's no headline return number to deflate. Four substantive concerns specific to overlay transfer apply at this stage instead:

#### (i) Unit-of-analysis correction
Yuyama scales **whole-portfolio** vol. Bitcoin allocation: 12.5% under 1/N (Yuyama Table 7). Of the headline MDD reduction, roughly half comes from cash substitution for bitcoin during high-vol periods (the other 87.5% of the portfolio is held). LiqCascade has no substitution mechanism — vol scaling only reduces position size, leaving the underlying signal exposure shape unchanged.

**Magnitude estimate:** ~50% of Yuyama's reported MDD reduction transfers to a single-strategy application.

After §6.2.2 0.5 decay: 60–80% × 0.5 = 30–40%.
After unit-of-analysis correction: 30–40% × 0.5 = **15–20% MDD reduction expected** on LiqCascade-style PnL.

#### (ii) Operationalization gap
Yuyama's framework: 30-day vol measurement, 10-day rebalance, daily-priced portfolio. LiqCascade is trade-driven (~16 trades/day average). Translation requires defining: (a) vol-measurement basis (per-trade returns, per-calendar-day P&L, or per-candle returns of the underlying assets); (b) position-scaling cadence (per-entry, per-rebalance, or per-candle); (c) rebalance trigger semantics; (d) vol target definition (Yuyama's 0.5% daily target → what in a per-trade context).

**§6.1 buildability concern:** Concrete but not yet specified. Phase 0 spec work required before Cursor build. Folded into §6.2.11 reopen trigger #2 below.

#### (iii) PnL distribution conditional on Phase 4
H&S diagnostic ran on V04+V05 dry-run; V06 (counter-trend, OI-filtered) is the production variant in active forward testing. ξ₀ characteristic of V06 PnL may differ. If V06 ξ₀ ≥ 1 with positive S (counter-trend works), C1-Risk becomes *less* attractive — vol scaling on a positive-EV strategy with ξ₀ ≥ 1 reduces upside without proportional risk reduction.

**Treatment:** C1-Risk verdict is **conditional on V06 ξ₀ remaining < 1** at Phase 4 resolution. Re-verify at ~50 closed V06 trades. Folded into §6.2.11 reopen trigger #3 below.

#### (iv) Underlying-EV precondition
Yuyama's Calmar improvements come from MDD reduction *outpacing* return reduction. On a long-bitcoin portfolio with positive expected return, this works — strategy makes a bit less but with much less drawdown. **On a strategy with negative expected return, vol scaling reduces magnitude of losses but does not improve Calmar in any meaningful sense** (both shrink proportionally; ratio unchanged or worse).

V04+V05 dry-run sample showed S = −0.259 (negative-expectancy in the dry-run window). Vol scaling on a negative-S strategy would just make it smaller, not better.

**Treatment:** C1-Risk activates only after a positive-EV underlying signal is established. LiqCascade GO at Phase 4 with positive PF, OR another GatedExecution primary signal validated independently. Folded into §6.2.11 reopen trigger #1 below.

---

## §6.2.7 Standalone Economic Test (§6.2.6 in Research Log)

### C1-Sharpe
- **Pass threshold:** N/A — there is no return number to test against the >25% / Sharpe >1.0 / MDD <30% threshold; C1-Sharpe is a Sharpe-improvement claim, not a strategy.
- **Direct empirical disconfirmation:** ξ₀ = 0.992 EWMA on 771 LiqCascade trades — convexity mechanism for Sharpe improvement is structurally absent. Yuyama 2023 confirms BTC-class assets violate the asymmetry precondition; Yuyama's Sharpe deltas are mixed and not statistically significant.
- **PASS / FAIL:** **REJECTED** (effective FAIL — no further work).

### C1-Risk
- **Critical framing.** §6.2.6 standalone thresholds (deflated annual return >25% AND deflated Sharpe >1.0 AND deflated MDD <30%) are designed for **return-generating strategies**. C1-Risk is a **risk overlay** — by construction, an overlay applied in isolation produces zero return. Applying §6.2.6 standalone thresholds to an overlay produces an automatic FAIL by construction, which is meaningless.
- **Resolution:** Treat C1-Risk under the §6.2.6 last-bullet referral pattern that was used for Candidate L's spread/z-score sub-signal: "if a candidate fails standalone but has a discrete signal that could plug into GatedExecution, refer it there rather than archiving." The integration target for an overlay is **§4.5 GatedExecution §5.2 (unified risk/exit framework)** rather than the §4.5 gate catalog (which is for direction/confirmation gates, not position-sizing layers).
- **Final magnitude expectation table:**

  | Stage | MDD reduction estimate |
  |---|---|
  | Yuyama 2023 headline (VC(4), 0.5% target, multi-allocation average) | 60–80% |
  | × §6.2.2 0.5 decay | 30–40% |
  | × Unit-of-analysis correction (~0.5×) | **15–20%** |

- **Bar for "worth integrating" as an overlay:** A meaningful but not heroic magnitude. 15–20% MDD reduction on GatedExecution PnL would translate to a Calmar improvement of roughly the same proportion (assuming return reduction is smaller than MDD reduction — Yuyama VC(4) shows this generally holds). **This is worth integrating if and only if operational complexity is low.** If the operationalization spec turns out clean (per-entry scaling, no separate rebalance trades, well-defined vol measurement), the overlay adds little operational burden and a meaningful Calmar improvement. If complex (sidecar infrastructure, rebalance triggers, calibration drift handling), the cost-benefit shifts.
- **PASS / FAIL:** **CONDITIONAL PASS** as risk overlay candidate, referred to §4.5 GatedExecution §5.2.

---

## §6.2.8 Verdict

**Verdict: split — C1-Sharpe (c) FAIL/archive; C1-Risk (b) NARROW — fold into GatedExecution §5.2 as risk overlay.**

This means C1 does NOT get a standalone Dev Plan. C1-Sharpe is closed out (no further work). C1-Risk is absorbed into the GatedExecution synthesis initiative (§4.5) as a CONFIRMED risk overlay candidate for §5.2 (unified risk/exit framework), with four explicit reopen conditions before Phase 0+ build authorization.

**Rationale:**
1. The C1-Risk mechanism is real and class-level documented — Yuyama 2023 reports statistically significant (1% level) MDD reductions across all four allocation methods and five VC strategies, robust through 2016–2022 including 2018 and 2022 crypto crashes.
2. The mechanism transfers cleanly to LiqCascade-style PnL because ξ₀ < 1 on actual project PnL means high-vol periods are exactly the periods of worst returns — vol scaling reduces exposure where it would help most.
3. But the magnitude does not transfer 1:1: unit-of-analysis correction (no substitution mechanism in single-strategy application) plus standard 0.5 post-publication decay reduce expected magnitude from 60–80% to 15–20% MDD reduction.
4. C1-Risk depends on a positive-EV underlying — vol scaling on a negative-EV strategy reduces magnitude of losses but does not improve risk-adjusted performance. Phase 4 resolution must produce a positive-EV primary signal before the overlay can be activated.
5. Operationalization spec is concrete-but-not-yet-written — Yuyama operates in a daily-rebalance portfolio framework; per-entry strategy-overlay translation needs specification.

**What carries forward into GatedExecution §5.2:**
- Conditional vol-targeting overlay design (vol measured per rolling 30-day window, position size scaled inversely with conditional vol relative to target)
- Default VC variant: **VC(4) at 0.5% daily-equivalent target** (Yuyama's strongest MDD-reduction cell)
- Per-entry scaling cadence (no separate rebalance trades — preserves zero-fee-delta property)
- Activation gating: only when underlying primary signal is positive-EV (confirmed forward at Phase 4 or equivalent)

**What is intentionally NOT preserved:**
- Standalone-strategy framing for vol targeting — closed out via C1-Sharpe REJECTED
- Yuyama's multi-asset portfolio context — not applicable to single-strategy application
- The "improve Sharpe via convexity" framing of H&S 2018 — empirically disconfirmed on our PnL (ξ₀ = 0.992)
- Multi-VC-variant selection at runtime — operationalization commits to one variant ex ante

---

## §6.2.9 Paper Replication Checklist (§6.3 in Research Log)

### Hoyle & Shephard 2018
| # | Question | Answer / Note |
|---|----------|---------------|
| 1 | Fee tier? | Not modeled. H&S explicitly defers to a follow-on paper (their §5). Not material — H&S is a theoretical decomposition, not a strategy claim. |
| 2 | Data window? | 1988–2017 daily, 142 futures and forwards markets. Predates crypto. |
| 3 | Survivorship-biased universe? | "Markets where at least 10 years of data are available." Some survivorship at the market level, but the conclusion is about the *distribution* of γ₁ across markets, not a strategy return. ✓ |
| 4 | Daily-close-to-close vs slippage-aware? | Not applicable — no strategy executed; this is an econometric decomposition of theoretical vol-scaled returns. |
| 5 | Param-opt protocol? | EWMA half-life of 12 days fixed; 30-day rolling std as robustness check. No optimization. ✓ |
| 6 | MDD definition? | Not applicable — H&S analyzes Sharpe ratio properties, not drawdowns. |
| 7 | Regime splits reported? | Yes — Table 1 reports per-market-category breakdowns (agricultural, bonds, currencies, energy, equities, metals, short rates). ✓ |
| 8 | Best parameter set / dispersion? | Reports full distribution: γ₁ mean 1.33, median 1.08, sd 2.20, Q0.1 0.63, Q0.9 1.77 across 142 markets. **Wide dispersion — γ₁ < 1 is not rare.** Our LiqCascade γ₁ ≈ 0.99 sits in the lower decile of H&S's distribution. |
| 9 | Live / forward-test track record? | Not applicable — theoretical paper. |
| 10 | Infrastructure assumptions? | Not applicable — econometric framework only. ✓ |

### Yuyama et al. 2023
| # | Question | Answer / Note |
|---|----------|---------------|
| 1 | Fee tier? | 10 bps per transaction (Section 3.3.2). Round-trip per common interpretation. **Matches our 10 bps assumption.** ✓ |
| 2 | Data window? | 2016-01-04 to 2022-12-30 daily, weekday-only. Includes 2018 winter, 2020 COVID, 2021 bull peak, 2022 winter. ⚠ Does NOT include 2024–2025 — cannot validate post-publication generalization from the paper alone. |
| 3 | Survivorship-biased universe? | Fixed universe of 7 traditional assets + bitcoin specified ex ante. ✓ |
| 4 | Daily-close-to-close vs slippage-aware? | Daily close-to-close. Slippage embedded in 10 bps fee assumption. ✓ for daily portfolio framework; ⚠ for trade-driven strategy port — operationalization spec must address this. |
| 5 | Param-opt protocol? | Out-of-sample with 252-day training, 5-day rebalance, expanding window. Both in-sample (Table 6) and out-of-sample (Table 7) reported. ✓ |
| 6 | MDD definition? | Peak-to-trough on cumulative returns (Section 3.4.1, Eq. 15). Standard. ✓ |
| 7 | Regime splits reported? | Yes — per-year tables (Tables 6–10) cover 2017–2022 separately. Per-year MDD reductions hold in 2018 and 2022. ✓ |
| 8 | Best parameter set / dispersion? | All 4 × 5 = 20 (allocation × VC-strategy) cells reported, not best-of. Robustness across the design space, not selection within it. ✓ |
| 9 | Live / forward-test track record? | None observable from paper. ⚠ Mitigated by §6.2.2 0.5 decay applied to magnitude. |
| 10 | Infrastructure assumptions? | Daily-rebalance portfolio framework — needs translation to trade-driven strategy semantics. ⚠ This is the operationalization gap (§6.2.6 deflation (ii) above). |

---

## §6.2.10 Forward Cross-Validation

**H&S empirical test on actual project PnL (2026-05-03):**

771 LiqCascade V04+V05 closed dry-run trades, 11 OracleSurfer trades (insufficient sample). Full report: `HS_Empirical_Test_LiqCascade_OracleSurfer_2026-05-03.md`.

| Sample | EWMA ξ₀ | EWMA γ₁ | HS test verdict | Interpretation |
|---|---|---|---|---|
| LiqCascade combined V04+V05 (771) | 0.992 | 0.992 | FAIL | Sits in lower decile of H&S 142-market distribution. Convexity mechanism absent. C1-Sharpe REJECTED. |
| LiqCascade shorts only (346) | 0.878 | 0.878 | FAIL | Most extreme ξ₀ < 1. Short trades cluster heavily in high-vol periods. Vol scaling would dampen losses (Sσ less negative than S by ~0.02), but no Sharpe improvement. |
| LiqCascade longs only (425) | 1.210 | 1.210 | "PASS" but S<0 | γ₁ > 1 on a negative-S leg makes Sσ *more* negative — worst-case interaction. |
| OracleSurfer (11) | 0.912 | 0.912 | n/a — sample too small | Not actionable. Re-run at ≥50 trades. |

**Implication:** The class-level H&S result (mean γ₁ ≈ 1.33) does not transfer to LiqCascade-style PnL. This is the primary system-specific evidence supporting C1-Sharpe REJECTED. It also confirms the *positive-transfer* finding for C1-Risk: ξ₀ < 1 means vol scaling reduces exposure where the strategy has its worst returns, exactly the mechanism Yuyama documents.

**Forward replication check on Yuyama's risk-reduction claim:** Not yet performed — would require operationalizing vol scaling on actual PnL and comparing pre/post drawdown distributions. This is the Phase 0 work that C1-Risk authorization unlocks (subject to all four reopen triggers being met first).

---

## §6.2.11 Reopen Triggers

C1-Risk reopens for Phase 0+ build authorization **only if all four conditions are met**:

1. **Phase 4 resolves with positive-EV underlying.** LiqCascade GO with PF > 1.0 at ≥50 closed V06 trades, OR another GatedExecution primary signal is established with positive expected return on its own forward-test data.

2. **Operationalization spec drafted and reviewed.** A written specification of (a) vol-measurement basis, (b) position-scaling cadence (default: per-entry only, no separate rebalance), (c) rebalance trigger semantics (default: none — pure per-entry), (d) vol target definition (default: VC(4)-equivalent 0.5% daily-equity-vol target). Spec should be reviewed (web session or Cursor session) before any code is written.

3. **V06 ξ₀ re-verified < 1 at Phase 4 resolution.** Re-run the H&S diagnostic on V06 production trades at the ~50-closed-trade Phase 4 mark. If ξ₀ ≥ 1 on V06 (distribution shape inverts from V04+V05), C1-Risk verdict needs revision — likely downgrade because vol scaling on a positive-EV ξ₀≥1 strategy reduces upside without proportional risk reduction.

4. **Operational complexity confirmed low.** If the operationalization spec turns out to require sidecar infrastructure, rebalance triggers, calibration drift handling, etc., the cost-benefit shifts. Re-evaluate whether 15–20% MDD reduction justifies the complexity. If complex, archive instead of building.

**NOT valid reopen triggers** (per §6.2 protocol):
- "Yuyama's results are real, let's just build it" — ignores the four substantive deflations.
- "The droplet has cycles, let's try it" — violates §5.6 hard queueing constraint and the 70/30 rule.
- Open-ended hyperopt or speculative implementation.
- "One more month of data" — V06 needs to actually reach the ≥50-trade Phase 4 mark before re-verification is meaningful.

---

## Process notes — protocol gap surfaced

C1-Risk is the **first overlay-class candidate** to receive a §6.2 pass. It surfaced a real protocol gap: §6.2.6 standalone thresholds (deflated return >25%, Sharpe >1.0, MDD <30%) are designed for return-generating strategies and produce an automatic FAIL by construction when applied to overlays, which is meaningless.

This gap will recur for future overlay candidates (e.g., conformal prediction wrapper, dynamic Kelly sizing, regime-conditional leverage). Recommended §6.2.6 amendment for next protocol revision:

> §6.2.6 Pass threshold (revised proposal):
>
> **Standalone candidates** (return-generating signals that could become a Dev Plan on their own):
> - After all deflations, if deflated annual return > 25% AND deflated Sharpe > 1.0 AND deflated MDD < 30%, advance.
> - If a standalone candidate fails this stage but has a discrete signal that could plug into GatedExecution, refer to §4.5 gate catalog.
>
> **Overlay candidates** (position-sizing, risk-management, or signal-conditioning layers that modify the risk profile of an underlying strategy's PnL but do not generate return on their own):
> - The standalone return/Sharpe/MDD thresholds do not apply.
> - Apply: (a) does the underlying-strategy risk-profile change clear a meaningful improvement threshold (e.g., ≥10% MDD reduction or ≥15% Calmar improvement after deflations); (b) is the underlying expected to be positive-EV at activation; (c) is the operationalization spec well-defined and low-complexity?
> - If yes to all three, refer to §4.5 GatedExecution §5.2 (unified risk/exit framework).
> - If no to any, archive with reopen trigger conditions.

This amendment is **not retroactively adopted** in v5.1.2. It is queued for the next §6.2 protocol revision. Until then, the C1-Risk verdict stands as-is, with the routing pattern (§6.2.6 last-bullet referral to §4.5 §5.2) as the workaround.
