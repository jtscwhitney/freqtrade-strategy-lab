# Hoyle & Shephard (2018) Empirical Test — LiqCascade & OracleSurfer Realized PnL

## Purpose
Pre-deflation diagnostic for Sweep #6 Candidate C1 (Conditional Vol Targeting). Runs the Hoyle & Shephard 2018 (SSRN 3279787) empirical test on our actual strategy PnL to produce a data-driven prior on whether C1 will pass its eventual §6.2 deflation.

## Methodology

### Return series
- **LiqCascade:** 771 closed trades from `tradesv3.dryrun.sqlite` (V04: 389 trades, V05: 382 trades), covering 2026-03-17 to 2026-05-03. Forward test dry-run data. V06 trades excluded (deployed 2026-05-02, no closed trades). Dataset slightly exceeds the 752-trade Phase 3.5 final due to continued V05 running. All 5 pairs (BTC/ETH/SOL/XRP/BNB), both directions.
- **OracleSurfer:** 11 closed trades (v12: 8, v14: 3) covering 2026-02-25 to 2026-04-22. BTC/USDT only. Sample is far below the ~50-trade minimum for a clean read — results shown for completeness only.
- **μₜ convention:** Both constant-μ (HS §3.3 case — ξ₁ collapses to 0) and rolling-μ (window matched to EWMA half-life) reported.

### Vol process
- **Primary:** EWMA with 12-day half-life (Hoyle & Shephard baseline), mapped to trade count via trades/day.
- **Robustness:** 30-day rolling std, mapped analogously.

### Quantities computed
Per Hoyle & Shephard Theorem 1, Lemma 1:

| Symbol | Definition |
|--------|------------|
| μ | Unconditional mean per-trade return |
| σ | Unconditional std of per-trade returns |
| S | Buy-and-hold Sharpe = μ / σ |
| ξ₀ | E(σ / σₜ) — convexity term, ≥ 1 by Jensen if σₜ < σ on average |
| ξ₁ | Cov(σ/σₜ, μₜ/μ) — timing/covariance term |
| γ₁ | ξ₀ + ξ₁ — the key scalar |
| γ₂ | Var(σ/σₜ · μₜ/μ) |
| HS test | γ₁ ≥ √(1 + S²·γ₂) → vol scaling improves Sharpe |
| Sσ | Vol-scaled Sharpe |
| Sσ - S | Sharpe delta from vol scaling (+ve = improvement) |

---

## Results

### LiqCascade V04+V05 Combined (771 trades)

| Quantity | EWMA, constant μ | EWMA, rolling μ | 30d roll, constant μ | 30d roll, rolling μ |
|----------|:---:|:---:|:---:|:---:|
| μ | −0.00407 | −0.00407 | −0.00407 | −0.00407 |
| σ | 0.01570 | 0.01570 | 0.01570 | 0.01570 |
| **S** (buy-hold) | **−0.259** | **−0.259** | **−0.259** | **−0.259** |
| ξ₀ | 0.992 | 0.992 | 1.047 | 1.047 |
| ξ₁ | 0 | −0.00345 | 0 | −0.00178 |
| **γ₁** | **0.992** | **0.989** | **1.047** | **1.046** |
| γ₂ | 0.00324 | 0.0142 | 0.00264 | 0.00222 |
| HS thld | 1.0001 | 1.0005 | 1.0001 | 1.0001 |
| **HS test** | **FAIL** | **FAIL** | **PASS** | **PASS** |
| Sσ | −0.257 | −0.256 | −0.271 | −0.271 |
| Sσ − S | **+0.002** | **+0.003** | **−0.012** | **−0.012** |

**Key observation:** ξ₀ = 0.99 under EWMA — below 1.0. This means conditional vol (σₜ) is on average *higher* than unconditional vol (σ). The strategy's trades cluster in high-volatility periods — exactly what you'd expect from a liquidation-cascade strategy. The convexity that drives vol scaling's Sharpe improvement (ξ₀ ≈ 1.36 in H&S's 142-market dataset) is absent in our trade series.

**Under the 30-day rolling vol measure:** ξ₀ = 1.05 — above 1.0 because the longer window smooths through the trade-clustered high-vol patches. The HS test technically passes, but Sσ − S is *negative* (−0.012). This is the negative-Sharpe paradox: when S < 0, γ₁ > 1 makes Sσ *more* negative, not less. Vol scaling amplifies a negative-expectancy process by putting larger positions in periods the vol model identifies as "calm" — which, for a strategy whose edge is in volatile events, means reduced exposure to the signal itself.

### LiqCascade Shorts Only (346 trades)

| Quantity | EWMA, constant μ | 30d roll, constant μ |
|----------|:---:|:---:|
| μ | −0.00255 | −0.00255 |
| σ | 0.01547 | 0.01547 |
| **S** (buy-hold) | **−0.165** | **−0.165** |
| ξ₀ | 0.878 | 0.915 |
| **γ₁** | **0.878** | **0.915** |
| HS test | **FAIL** | **FAIL** |
| Sσ | −0.145 | −0.151 |
| Sσ − S | **+0.020** | **+0.014** |

Shorts show the most extreme ξ₀ < 1 (0.878 under EWMA). Short trades cluster even more strongly in high-vol periods than the combined sample. Vol scaling reduces position sizes in those periods, which dampens losses — Sσ is less negative than S by ~0.02. But γ₁ < 1 means the [convexity + timing] benefit that would give vol scaling a clean Sharpe improvement is not present.

### LiqCascade Longs Only (425 trades)

| Quantity | EWMA, constant μ | 30d roll, constant μ |
|----------|:---:|:---:|
| μ | −0.00531 | −0.00531 |
| σ | 0.01577 | 0.01577 |
| **S** (buy-hold) | **−0.336** | **−0.336** |
| ξ₀ | 1.210 | 1.335 |
| **γ₁** | **1.210** | **1.335** |
| HS test | **PASS** | **PASS** |
| Sσ | −0.406 | −0.447 |
| Sσ − S | **−0.069** | **−0.110** |

Longs have ξ₀ > 1 (trades are spread more evenly across vol regimes), so γ₁ > 1 and the HS test passes. But S is negative (−0.336), so γ₁ > 1 makes Sσ substantially *more* negative. This is the worst-case interaction: vol scaling boosts the convexity term on a negative-Sharpe directional leg.

### OracleSurfer (11 trades — INSUFFICIENT SAMPLE)

| Quantity | EWMA, constant μ |
|----------|:---:|
| μ | −0.02102 |
| σ | 0.06189 |
| S | −0.340 |
| ξ₀ | 0.912 |
| γ₁ | 0.912 |
| HS test | **FAIL** |
| Sσ | −0.310 |
| Sσ − S | +0.030 |

**11 trades is far below the ~50-trade minimum for a clean read.** These numbers are noise. Not actionable.

---

## Honest Read: What This Means for C1

### C1-Sharpe (can vol scaling improve Sharpe?)

**Very unlikely to pass §6.2 on our actual PnL data.** The core finding is ξ₀ < 1 under EWMA: LiqCascade trades cluster in high-volatility periods, so the convexity benefit that drives vol scaling's Sharpe improvement in traditional futures (ξ₀ ≈ 1.36 in H&S's dataset) is absent. When a strategy's trade returns are most dispersed in high-vol windows, vol scaling reduces exposure exactly when the signal is most active — it's a volume knob that turns down the strategy, not a filter that improves selectivity.

This result aligns with Yuyama et al. 2023's finding that BTC violates the preconditions for vol scaling to add Sharpe (return does not reliably fall when risk rises and rise when risk falls in crypto). Our trade data shows the same structural pattern at the single-strategy level.

**Add the comparison to H&S's 142-market empirical distribution:**
- H&S median γ₁ ≈ 1.08, driven by ξ₀ ≈ 1.36 with ξ₁ ≈ 0 (modestly negative)
- Our LiqCascade γ₁ ≈ 0.99 under EWMA, driven by ξ₀ ≈ 0.99
- We are on the *wrong side of 1.0* for the convexity term that makes vol scaling work

### C1-Risk (can vol scaling reduce drawdowns?)

**More likely to pass if deflated against drawdown/Calmar criteria.** Vol scaling reduces position sizes in high-vol periods. For LiqCascade, those periods have the worst returns (that's why ξ₀ < 1). Reducing exposure in those windows would reduce drawdowns, even if it doesn't improve Sharpe. Yuyama 2023 found statistically significant Max DD reductions of 60–70% from vol control. This aligns with our finding.

### Implication for C1 deflation charter

The post-sweep reads bifurcated C1 into C1-Sharpe (likely fails) and C1-Risk (more likely passes). The H&S test on our actual PnL data **confirms this bifurcation and adds evidence on the C1-Sharpe side:** the convexity mechanism that makes vol scaling improve Sharpe in traditional assets (ξ₀ ≈ 1.36) is structurally absent in our liquidation-cascade PnL (ξ₀ ≈ 0.99). C1-Sharpe enters its §6.2 deflation with a prior that is now lower than the post-sweep 30% estimate.

**Revised C1 survival estimate:** ~20% for C1-Sharpe (down from 30%), ~40% for C1-Risk (drawdown framing). Combined probability of at least one framing passing: still ~40% — the risk framing was always the more likely path.

### What this test is NOT

This is a pre-deflation diagnostic, not a §6.2 deflation pass. C1 enters formal deflation when LiqCascade Phase 4 resolves and it reaches the front of the queue.

---

## Data Provenance

- LiqCascade trade DB: `ssh root@138.197.188.16:/opt/freqtrade/freqtrade-scalper/user_data/tradesv3.dryrun.sqlite`, extracted 2026-05-03 18:25 UTC (771 closed trades, last close_date 2026-05-03 18:25)
- OracleSurfer trade DB: `ssh root@104.248.17.129:/opt/freqtrade/user_data/tradesv3.sqlite`, extracted 2026-05-03 (11 closed trades)
- Analysis script: `user_data/scripts/hs_empirical_test.py`
