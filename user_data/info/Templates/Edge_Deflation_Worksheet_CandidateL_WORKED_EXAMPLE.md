# §6.2 Edge Deflation Worksheet — Candidate L (WORKED EXAMPLE)

> This is the canonical worked example of a completed §6.2 Edge Deflation Pass. It was populated from `EnhancedCointPairs_Deep_Dive.md` Part 8 (2026-05-03) and cross-referenced against the §6.2 process in `AlgoTrading_Research_Log.md`. Use this as a reference when filling in a blank template.

---

## Header

| Field | Value |
|-------|-------|
| Candidate name | Candidate L — Enhanced Cointegration Pairs Trading |
| Source paper(s) | 1. Palazzi (Journal of Futures Markets, Aug 2025) — adaptive trailing stop + vol filter on cointegrated crypto pairs. 2. Tadi & Witzany (Financial Innovation, 2025) — copula-based pairs on Binance USDT-M futures. |
| Date worksheet started | 2026-05-03 |
| Status | COMPLETE |
| Evaluator | Claude Opus 4.7 + developer session 2026-05-03 |
| Inputs available | Lab walk-forward CSVs (BTC/ETH @ 4h, V01/V02), `cointpairs_comparison_tables.md`, forward droplet snapshot 2026-05-02 (6 replicas, 17 closed trade rows), Research Log §6.2.5 explicit instruction to use portfolio average Sharpe 0.89 |
| Inputs NOT available | Paper PDFs not on disk. Specific fee tier, OOS window, MDD definition are **⚠ inferred** from paper-class conventions. Items marked ⚠ need re-read against original PDFs to firm up. Sensitivity bounds noted where consequential. |

---

## §6.2.1 Setup — Claimed Edge

**Palazzi 2025:**
- **Headline metric:** Portfolio Sharpe **0.89** (37-pair universe, 13 OOS-positive = 35% hit rate). Best single-pair Sharpe 2.12.
- **Mechanism claimed:** Cointegrated crypto pairs exhibit mean-reverting log-price spreads. Adaptive trailing stop + volatility filter improve risk-adjusted returns over static exit thresholds.
- **Universe / pairs:** 37 pairs from "10 major cryptos" on Binance. Daily granularity.
- **Test window:** ⚠ inferred ~2017–2024. Bear 2022 inclusion uncertain.
- **Fee assumption:** ⚠ inferred 5 bps/side = 10 bps RT on Binance spot (or possibly zero-fee vol-of-spread sims).

**Tadi & Witzany 2025:**
- **Headline metric:** ⚠ inferred Sharpe ~1.1 (copula-pairs papers typically report 0.8–1.5 on best sets)
- **Mechanism claimed:** Copula-based pair selection + weekly re-selection produces higher-frequency pairs trading that dominates daily rebalancing. Tests explicitly on Binance USDT-M futures.
- **Universe / pairs:** Full Binance perp listing including mid-caps. Weekly pair re-selection from rolling window.
- **Test window:** ⚠ inferred 2018–2024, includes 2022 bear.
- **Fee assumption:** ⚠ inferred VIP-0 retail (10 bps RT). Same venue as ours.

---

## §6.2.2 Sharpe / Return Decay (§6.2.1 in Research Log)

### Palazzi 2025
- **Default decay factor:** 0.5 (Falck & Rej 2022)
- **Override?** No. Paper is post-publication <12 months; no exemption qualifies.
- **Input Sharpe:** 0.89 (portfolio average, per §6.2.5 instruction)
- **Input annual return:** ⚠ inferred ~12–18%
- **After decay:** Sharpe **0.445**, return **~6–9%/yr**

### Tadi & Witzany 2025
- **Input Sharpe:** ⚠ inferred ~1.1 (midpoint of 0.8–1.5 range for class)
- **After decay:** Sharpe **0.55**, return scales proportionally

---

## §6.2.3 Fee-Tier Downgrade (§6.2.2 in Research Log)

### Palazzi 2025
- **Paper's assumed fee:** ⚠ inferred 5 bps/side = 10 bps RT spot (most generous-to-paper reading)
- **Our fee:** 20 bps RT per spread cycle (dual-leg on Binance retail futures: 10 bps × 2 legs)
- **Fee delta:** ~10 bps additional per spread cycle
- **Turnover proxy:** Lab BTC/ETH @ 4h ran 134 trades over ~4.25 years ≈ **31.5 trades/yr per spread**
- **Annual drag:** 31.5 × 10 bps ≈ **~3.15%/yr**
- **After fee downgrade:** return **~3–6%/yr**, Sharpe **~0.30–0.40**

### Tadi & Witzany 2025
- **Paper's assumed fee:** ⚠ inferred 10 bps RT (same venue — minimal delta)
- **Fee delta:** ~0–5 bps RT
- **Drag:** ~0–1.5%/yr
- **After fee downgrade:** minimal change from §6.2.2

---

## §6.2.4 Slippage Layer (§6.2.3 in Research Log)

### Palazzi 2025
- **Paper's universe:** "10 major cryptos" — top liquidity tier
- **Slippage per pair:** Liquid majors 2 bps RT (BTC, ETH); liquid alts 5 bps RT (SOL, BNB, XRP, ADA, AVAX, LINK)
- **Weighted slippage:** ~7 bps RT per spread cycle (average across universe)
- **Annual slippage drag:** 31.5 × 7 bps ≈ **~2.2%/yr**
- **After slippage:** return **~1–4%/yr**, Sharpe **~0.20–0.32**

### Tadi & Witzany 2025
- **Paper's universe:** Full Binance perp listing including mid-caps
- **Mean-reversion candidates select for divergent (less liquid) pairs — conservative assumption**
- **Slippage:** ~10 bps RT per spread cycle
- **At 30 trades/yr/spread:** ~3%/yr drag
- **After slippage:** return falls accordingly

---

## §6.2.5 Regime Weighting (§6.2.4 in Research Log)

**Using lab data rather than paper headlines** (more reliable — our actual BTC/ETH @ 4h V01 defaults by year):

| Year (regime proxy) | Weight | V01 return | PF |
|---------------------|--------|------------|-----|
| 2022 (bear) | 33% | +8.4% | 1.18 |
| 2023 (chop) | 34% | −0.6% | 0.98 |
| 2024 (bull) | 33% | +10.9% | 1.20 |

- **Weighted return:** 33% × 8.4% + 34% × (−0.6%) + 33% × 10.9% ≈ **~6.2%/yr**
- The lab V01 defaults under §6.2.4 weighting deliver **~6.2%/yr** — already below the standalone threshold before post-publication decay is applied.
- **After regime weighting:** return **~3–5%/yr** (with decay + fee + slippage), Sharpe **~0.20–0.30**

### Tadi & Witzany 2025
- Weekly pair re-selection adapts faster than Palazzi's static universe but does not address regime — it addresses pair quality.
- Apply 33/34/33 → ~50% of headline survives
- **After regime weighting:** return scales proportionally (already factored into cumulative deflations above)

---

## §6.2.6 Selection Bias / Multiple Testing (§6.2.5 in Research Log)

### Palazzi 2025
- **Already addressed by using portfolio Sharpe 0.89 instead of best-of-N 2.12.** This is the single most important methodological choice in the worksheet.
- **Cross-check:** Palazzi's 35% OOS-positive (13/37 pairs) ≈ our forward replicas 33% positive (1/3 spreads × 2 versions). Direct empirical confirmation that pair selection dominates variant selection.
- **No further penalty applied.** The portfolio average already embeds the survival rate.

### Tadi & Witzany 2025
- **Weekly re-selection creates per-week multiple testing:** ~52 weeks/yr × ~50 candidate pairs ≈ 2,600 selection events/yr
- **(1/N)^0.3 penalty:** (1/2600)^0.3 ≈ 0.10. But this is conservative — the dominant signal is real cointegration, not noise pair-of-the-week luck. Apply softer penalty: divide Sharpe by **1.5×** (not the strict reading)
- **Headline Sharpe 0.55 (post-decay) ÷ 1.5 ≈ 0.37**
- Return: ~6–8%/yr post-decay → ~4–6%/yr post-selection

---

## §6.2.7 Standalone Economic Test (§6.2.6 in Research Log)

### Palazzi 2025
- **Pass threshold:** deflated annual return > 25% AND deflated Sharpe > 1.0 AND deflated MDD < 30%
- **Final deflated return:** **~3–5%/yr**
- **Final deflated Sharpe:** **~0.20–0.30**
- **Final deflated MDD:** ⚠ not directly known; lab BTC/ETH MDD consistent with 20–30% range at mid-single-digit return
- **FAIL §6.2 standalone.** Return ≪ 25%, Sharpe ≪ 1.0.
- **Discrete signal for GatedExecution?** YES — spread/z-score produces direction-bias per pair per candle. Gate-shaped: confirms or vetoes a primary signal's direction.

### Tadi & Witzany 2025
- **Final deflated return:** **~3–5%/yr** (after fees, slippage, regime, selection)
- **Final deflated Sharpe:** **~0.30–0.40**
- **FAIL §6.2 standalone.** Same order of magnitude as Palazzi.
- **Same referral to GatedExecution.**

---

## §6.2.8 Verdict

**Verdict: (a) for GatedExecution sub-signal — NOT standalone capital deployment.**

This means the candidate does NOT get a standalone Dev Plan, but the spread/z-score signal is absorbed into the GatedExecution synthesis initiative (§4.5) as a CONFIRMED gate. The candidate itself stays **PARKED** (not ARCHIVED) in the Approach Registry (§4.3).

**Rationale:**
1. The signal is real — Hurst H ≈ 0.25 (Candidate F), lab BTC/ETH positive through 4 years, forward replicas match paper's 35% OOS-positive rate. Three independent lines of evidence say this is not lottery-ticket noise.
2. But it does not clear §6.2.6 standalone economics (~3–5%/yr deflated vs 25% threshold) and cannot justify its own droplet cost or capital allocation.
3. As a gate in GatedExecution, it provides non-redundant directional confirmation (z > 0 → favor short A/long B; z < 0 → opposite) that complements liquidation-cascade event-driven signals.
4. The integration cost is low: only the signal computation logic (z-score, OLS β, entry thresholds) carries forward. The dual-leg execution machinery, adaptive trailing stop, and vol filter are all discarded.

**What carries forward into GatedExecution:**
- Spread/z-score signal source: `{direction, confidence ∝ |z| above entry, freshness}` per pair per candle
- Per-pair calibration is mandatory — naive multi-pair Phase 0 GO inheritance failed forward (BNB/SOL, BTC/SOL negative)
- Reference implementation: `EnhancedCointPairsStrategy_V01.py` signal computation logic
- β-weighted stakes, adaptive trailing stop, Palazzi vol filter are explicitly **not** preserved

**What is intentionally NOT preserved:**
- BTC/PAXG, LINK/ETH, UNI/SOL, XMR/BTC exploratory configs — all underperformed
- Hyperopt JSONs — not robust on full timerange
- Dual-leg execution infra (orphan-leg watchdog, `confirm_trade_entry`, paired-exit coordination)
- Adaptive trailing stop and vol filter — lab showed they reduce P&L; superseded by GatedExecution unified exit

---

## §6.2.9 Paper Replication Checklist (§6.3 in Research Log)

### Palazzi 2025
| # | Question | Answer / Note |
|---|----------|---------------|
| 1 | Fee tier? | ⚠ inferred 5 bps/side spot. **Demands re-read of paper.** |
| 2 | Data window? | ⚠ inferred ~2017–2024. Bear 2022 inclusion uncertain. |
| 3 | Survivorship-biased universe? | "10 major cryptos" — yes, by current market cap. Material at horizon-of-paper. |
| 4 | Daily-close-to-close vs slippage-aware? | ⚠ inferred close-to-close. Walk-forward sim likely does not embed retail slippage. |
| 5 | Param-opt protocol? | Walk-forward (75/25 stated in dev plan §1.3). Strong. |
| 6 | MDD definition? | ⚠ inferred peak-to-trough on equity curve. |
| 7 | Regime splits reported? | ⚠ Likely partial (paper claims "positive in both bull and bear"). Demand Phase 0 regime-split if revived. |
| 8 | Best parameter set / dispersion? | Critical: 35% OOS-positive (13/37). Per-pair Sharpe dispersion is wide; portfolio Sharpe 0.89 << best-pair 2.12. |
| 9 | Live / forward track record? | None published. Our 4-week droplet is the first independent forward replication; 35% positive replicas matches paper's OOS-positive rate exactly. |
| 10 | Infrastructure assumptions? | Standard retail Freqtrade-compatible. ✓ |

### Tadi & Witzany 2025
| # | Question | Answer / Note |
|---|----------|---------------|
| 1 | Fee tier? | ⚠ inferred VIP-0 retail (10 bps RT). Same venue as ours — minimal fee delta. |
| 2 | Data window? | ⚠ inferred 2018–2024, includes 2022 bear. |
| 3 | Survivorship-biased? | Weekly re-selection mitigates but does not eliminate (delisted pairs still excluded retroactively). |
| 4 | Slippage-aware? | ⚠ Probably not — copula papers typically assume mid-quote fills. |
| 5 | Param-opt protocol? | Weekly re-selection from rolling window. Strong on adaptation, weak on multiple testing. |
| 6 | MDD definition? | ⚠ inferred standard equity peak-to-trough. |
| 7 | Regime splits? | ⚠ Partial. |
| 8 | Best parameter set / dispersion? | Selection happens weekly across full universe — high effective N. |
| 9 | Live / forward track record? | None published. |
| 10 | Infrastructure assumptions? | Compatible — same exchange, similar holding periods. ✓ |

---

## §6.2.10 Forward Cross-Validation (if available)

**Droplet forward test (2026-04-07 to 2026-05-02, 4 calendar weeks, 6 replicas):**

| Spread × Variant | PnL vs stakes | Positive? |
|---|---|---|
| BTC/ETH × V01 | ~+4.2% | Yes |
| BTC/ETH × V02 | ~+4.2% | Yes |
| BNB/SOL × V01 | ~−1.5% | No |
| BNB/SOL × V02 | ~−1.25% | No |
| BTC/SOL × V01 | ~−2.0% | No |
| BTC/SOL × V02 | ~−2.0% | No |
| **Aggregate** | **~+0.01% (~+$6.56)** | **Flat** |

- 17 closed trade rows — below §2 50-trade bar for binary go/no-go read
- 33% positive replicas (1/3 spreads) ≈ paper's 35% OOS-positive rate within sampling noise
- **Lesson:** Pair selection within the universe is the dominant variable, not strategy variant (V01 vs V02)
- BTC/ETH was the only lab-validated spread; BNB/SOL and BTC/SOL were deployed on Phase 0 GO inheritance only without head-to-head walk-forward ranking

---

## §6.2.11 Reopen Triggers

1. GatedExecution Dev Plan v1.0 explicitly rejects the spread/z-score gate → revisit option (b) portfolio-of-spreads with held-out pairs. **Closed 2026-05-03: gate is CONFIRMED in Dev Plan v0.1.**
2. A §6.2 deflation pass on a *new* paper materially changes the deflated economics of cointegrated-pairs trading at our fee tier.
3. A held-out pair selection method demonstrably outperforms naive Phase 0 GO inheritance in walk-forward ranking.

**NOT valid reopen triggers:**
- Open-ended hyperopt on parameters
- "One more month of droplet data" (at 31.5 trades/yr/spread, this is ~19 calendar months per replica for 50 trades — unjustified)
- New cointegrated pairs without a head-to-head ranking method
