# AdaptiveTrend Strategy (Candidate M) — Deep Dive
## Version 2 | Started: 2026-04-08 | Last updated: 2026-04-09 | Status: ARCHIVED — Phase 0 NO-GO

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**
> Pair with `AlgoTrading_Research_Log.md` §4.3 (Candidate M entry) and `AdaptiveTrend_Dev_Plan.md`.

### Current Status

**ARCHIVED — Phase 0 NO-GO (2026-04-09)**

| Item | State |
|------|-------|
| **Phase 0 — V01** | **COMPLETE** — 15 large-cap pairs. Long-only FAIL (PF 0.81). Long+short PF 1.07 — short leg carried everything. |
| **Phase 0 — V02** | **COMPLETE** — 61 pairs. Long-only PF 0.63, −74.4%. Mid-cap expansion worsened results. |
| **Phase 0 — V03** | **COMPLETE** — 57 pairs + EMA(100) filter + 72-bar lookback + ATR-norm entry + momentum exit. PF 0.69, −62.2%. Momentum exit churned trades. Archived. |
| **Phase 1–3** | CANCELLED — Phase 0 failed. |

**Short leg salvaged as Candidate N (ShortBias Momentum).** See Research Log §4.3.

### V01 Results Summary

| Run | can_short | ATR_MULT | Timerange | PF | Total % |
|-----|-----------|----------|-----------|-----|---------|
| Full period | False | 2.5 | 2022–2025 | 0.81 | −42.2% |
| 2022 bear | False | 2.5 | 2022–2023 | 0.59 | −43.5% |
| 2023 | False | 2.5 | 2023–2024 | 1.08 | +8.3% |
| 2024 bull | False | 2.5 | 2024–2025 | 0.95 | −5.6% |
| Full period | False | 3.5 | 2022–2025 | 0.95 | −10.3% |
| **Full period** | **True** | **3.5** | **2022–2025** | **1.07** | **+23.4%** |

Long/short split at ATR_MULT=3.5: **Longs 758 trades −3.16% / Shorts 270 trades +26.60%**

### Archive Summary (2026-04-09)

All three long-only iterations failed. Long-side momentum signal has no consistent edge in this universe over the 2022–2025 test period. Candidate M is archived.

**Next action:** Candidate N (ShortBias Momentum) — run V01 regime splits (can_short=True) to evaluate the short leg in isolation across 2022/2023/2024 regimes.

### File Locations

| File | Status | Purpose |
|------|--------|---------|
| `user_data/info/AdaptiveTrend_Deep_Dive.md` | **THIS FILE (ARCHIVED)** | Technical reference |
| `user_data/info/AdaptiveTrend_Dev_Plan.md` | ARCHIVED | Phase plan, gates, anti-patterns, results log |
| `user_data/strategies/AdaptiveTrendStrategy_V01.py` | Reference | 15-pair large-cap MVP; can_short=True, ATR_MULT=3.5 — reuse for Candidate N |
| `user_data/strategies/AdaptiveTrendStrategy_V02.py` | Reference (FAIL PF 0.63) | 61-pair mid-cap expansion; can_short=False, ATR_MULT=3.5 |
| `user_data/strategies/AdaptiveTrendStrategy_V03.py` | Reference (FAIL PF 0.69) | 57-pair; EMA filter + 72-bar lookback + ATR-norm entry |
| `config/config_adaptivetrend.json` | Reference | 15-pair whitelist, port 8087 |
| `config/config_adaptivetrend_v2.json` | Reference | 61-pair whitelist, port 8088 |
| `config/config_adaptivetrend_v3.json` | Reference | 61-pair whitelist, port 8089 |

---

## Part 1: Why This Project Exists

### 1.1 One-sentence idea

**Buy any crypto that has been rising faster than its recent history, and exit when the price falls back by a calibrated multiple of its recent volatility** — repeated across as many pairs as possible so individual noise averages out and genuine trends dominate.

That is systematic trend-following, also called time-series momentum (TSMOM): the signal is not relative strength across pairs but whether each pair has positive momentum relative to its own recent history.

### 1.2 Why this might work in crypto

Crypto markets are structurally prone to persistent trends:
- **Retail herding**: most participants are directional and momentum-chasing, which amplifies rather than dampens trends.
- **Leverage cascade**: rising prices force short liquidations which push prices higher; falling prices force long liquidations which push prices lower. Both create self-reinforcing trends.
- **Thin institutional arbitrage**: the capital required to arbitrage away momentum is large relative to the market's size and the patience required to hold a mean-reversion position through a trend.

The source paper (Bui & Nguyen, arXiv 2602.11708) documented these effects on 150+ Binance USDT-M perpetual futures pairs from 2020–2024, achieving SR 2.41, CAGR 40.5%, MDD −12.7% at 4 bps/trade cost.

### 1.3 Why the paper result is not the baseline expectation

The paper's headline SR 2.41 has two key components that are **not** in our Phase 0 MVP:
1. **Monthly Sharpe-based pair rotation** (+1.07 SR per ablation) — only keeps pairs that showed high risk-adjusted momentum in the prior month. This is Phase 1.
2. **150+ pair universe** — includes many mid/small-cap pairs where momentum is empirically stronger. Our initial 15-pair large-cap list is the worst-case subset.

The paper's fixed-parameter estimate (no monthly rotation) is SR ~1.34. At our 10bps fee vs. their 4bps baseline, adjusted SR ~1.7 expected. Phase 0 must be evaluated against this, not the headline.

---

## Part 2: Signal and Exit Architecture

### 2.1 Entry signal

```
MOM_t = (P_t - P_{t-L}) / P_{t-L}       # Rate-of-change over L bars
Enter long  if MOM_t > θ_entry
Enter short if MOM_t < -θ_entry
```

Default parameters (Phase 0):
| Parameter | Value | Source |
|-----------|-------|--------|
| `L` (lookback) | 24 bars (6 days on H6) | Bui paper; aligns with Huang et al. optimal 3–7 day window |
| `θ_entry` | 0.03 | Bui paper conservative center |
| `ATR_MULT` (α) | 3.5 | Empirically better than paper default 2.5 (see §4.1) |
| `ATR_period` | 14 | Standard |

### 2.2 ATR trailing stop (exit)

The only exit mechanism. No signal reversal exit, no ROI target.

**Long:**
```
S_t = max(S_{t-1}, P_t - α × ATR_t)
Exit long if P_t < S_t
```

**Short:**
```
S_t = min(S_{t-1}, P_t + α × ATR_t)
Exit short if P_t > S_t
```

This ratchet pattern — stop only moves in the profitable direction — is implemented in `custom_stoploss()` via `_trail_stop_abs` dict keyed on `trade.id`. The stop state persists across candles and is cleaned up in `bot_loop_start()` to prevent memory leaks.

**Key insight from V01 testing:** ATR_MULT=2.5 was too tight. Average winner duration at 2.5 was 8d 11h; at 3.5 it doubled to 16d 5h. Best trade improved from +127% to +312%. The stop was cutting trends before they matured.

### 2.3 Portfolio construction

**Long universe:** Fixed whitelist.
- V01: top-15 large-cap pairs (BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, DOT, LINK, UNI, ATOM, NEAR, APT, OP)
- V02: all 61 pairs (top-15 + 46 established mid-caps)

**Short universe:** Liquid subset only — V01 used 6 large-caps; V02 expands to 21 (6 large + 15 mid-cap).

**70/30 slot allocation:** Approximated via `confirm_trade_entry()` checking live counts of open longs vs. shorts against `MAX_CONCURRENT_LONG` and `MAX_CONCURRENT_SHORT`.

| Version | MAX_CONCURRENT_LONG | MAX_CONCURRENT_SHORT | max_open_trades |
|---------|--------------------|--------------------|-----------------|
| V01 | 10 | 5 | 15 |
| V02 | 25 | 12 | 37 |

**Leverage:** 1× (Phase 0 baseline).

---

## Part 3: Implementation Notes

### 3.1 Custom stoploss sign convention

Freqtrade's `Trade.adjust_stop_loss()` uses `abs(stoploss)` internally:
- Long: `stop = current_rate × (1 - abs(sl))`
- Short: `stop = current_rate × (1 + abs(sl))`

This means returning positive values for short stops (as this strategy does) is functionally identical to returning negative values. Verified against Freqtrade source 2026.2.

### 3.2 `_row_at()` pattern

`custom_stoploss()` needs the last closed candle to compute the current ATR stop level. `get_analyzed_dataframe()` returns the populated dataframe; `_row_at()` finds the last row with `date ≤ current_time`. This prevents lookahead bias during intra-candle stop evaluation. Pattern is identical to `EnsembleDonchianStrategy_V01`.

### 3.3 Class variable pitfall (fixed)

V01 initially used a class-level `_trail_stop_abs` dict, sharing state across instances. Fixed to an instance variable in `__init__()`. V02 inherits this fix.

### 3.4 Freqtrade cache behavior

`--cache none` is mandatory whenever `ATR_MULT`, `MOM_LOOKBACK`, `THETA_ENTRY`, or `can_short` is changed. The cache keys on strategy file hash — parameter changes that don't touch the file hash (e.g., editing a class attribute) will not invalidate the cache automatically. Always verify the strategy snapshot file in `backtest_results/Latest/` shows the expected parameter values before trusting a result.

---

## Part 4: Phase 0 Findings

### 4.1 ATR_MULT sensitivity (long-only, 15 pairs)

| ATR_MULT | PF | Total % | Avg winner | Best trade | Trade count |
|----------|-----|---------|-----------|-----------|------------|
| 2.5 | 0.81 | −42.2% | 8d 11h | +127% | 1323 |
| 3.5 | 0.95 | −10.3% | 16d 5h | +312% | 782 |

The improvement is monotone and substantial. Losses reduced by 75%. The stop at 2.5 was systematically cutting trends before maturity. 3.5 is the confirmed better default; further widening (e.g., 4.5+) has diminishing returns and has not been tested.

### 4.2 Large-cap long signal diagnosis

Win rate is stable at 31–33% across all ATR_MULT values and all regimes. This stability implies the rate is determined by the signal (ROC threshold), not the stop. For a trend-following strategy, 31–33% win rate is viable **if** the win/loss magnitude ratio compensates — here it doesn't (PF < 1.0) because large-cap crypto pairs have too-efficient price discovery at the 6h/6-day horizon.

Market context confirms the signal is regime-conditional: 2023 at ATR_MULT=2.5 produced PF 1.08 in a +179% market. The long signal exists; it's just not strong enough on large-caps at fixed parameters to overcome 2022 bear drag.

### 4.3 Long/short split at ATR_MULT=3.5 (15 pairs, can_short=True)

- **Longs (758 trades): −3.16%** — the long signal loses money on large-caps even with optimal stop width
- **Shorts (270 trades): +26.60%** — short signal on 6 liquid large-caps is highly profitable

This asymmetry is the key finding of V01. The strategy as designed is not a symmetric bidirectional momentum strategy on large-caps — it is effectively a short-carry strategy with a losing long component. The paper's claimed bidirectional edge almost certainly comes from the 135+ mid/small-cap pairs that generate stronger long-side momentum.

### 4.4 V02 results (2026-04-09)

**PF 0.63, −74.4%, 2,411 trades, 27.2% WR, avg hold 8.5 days.**

Mid-cap expansion made things materially worse. Only 11/61 pairs achieved PF > 1.0. Best: ZIL (PF 1.93), APT (PF 1.84), HBAR (PF 1.40), RUNE (implicitly via V03). Worst: DYDX (PF 0.27), ONE (PF 0.11), GRT (PF 0.30), XTZ (PF 0.03). The hypothesis that mid-caps exhibit stronger momentum was falsified — in 2022–2025, they were assets in secular downtrends with no recovery, not momentum vehicles.

Survivorship bias note: all pairs selected are still active on Binance futures. Delisted pairs are excluded — these results are an upper-bound estimate.

### 4.5 V03 results (2026-04-09)

**PF 0.69, −62.2%, 2,639 trades, 28.0% WR, avg hold 5.4 days.**

Changes: EMA(100) trend filter, MOM_LOOKBACK 24→72, ATR-normalized entry (replaces fixed 3%), 4 worst pairs pruned (DYDX/ONE/GRT/XTZ), momentum exit (`mom < 0` exits longs).

The momentum exit backfired: trade count increased (2,411→2,639), hold time dropped (8.5→5.4d). EMA(100) on 6h (= 25 days) is too responsive to function as a genuine regime filter in crypto — whipsaws frequently. The ATR-normalized entry reduced some bad entries but couldn't compensate for structurally weak long signal across 40+ pairs with no trending structure.

### 4.6 Phase 0 archive diagnosis

All three versions failed. The long signal does not work in this universe over this period. The paper's strategy likely works because of: (1) monthly Sharpe rotation that eliminates non-performing pairs dynamically, (2) a 150+ pair universe where a small number of strong-momentum pairs drive returns while the rest are excluded in rotation, (3) test period coverage that may coincide with more favorable conditions for specific pairs. Our fixed-whitelist, fixed-parameter implementation cannot replicate this dynamic selection effect.

**Short leg survival:** The V01 short leg (+26.6%, 270 trades, 6 pairs) is a different thesis. Candidate N investigates it as a standalone.

---

## Part 5: Source Papers

### Bui & Nguyen (arXiv 2602.11708, Feb 2026)
*"Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets"*

- OOS: Jan 2022–Dec 2024, 150+ USDT-M pairs, H6 bars
- Full strategy: SR 2.41, CAGR 40.5%, MDD −12.7% at 4 bps/trade
- Fixed params (no monthly rotation): SR ~1.34
- ATR trailing stop: highest single-component contribution (+0.73 SR in ablation)
- Monthly Sharpe rotation: +1.07 SR (Phase 1 of our dev plan)
- Fee sensitivity: 8 bps → SR 2.01; 12 bps → SR 1.62
- Organisation: Talyxion Research, Hanoi — no institutional pedigree; bootstrap significance strong; no independent replication

### Karassavidis et al. (SSRN 5821842)
*"Quantitative evaluation of volatility-adaptive trend-following models in cryptocurrency markets"*

- SMA(10/38) crossover + RSI filter + ATR trailing, H8, BTC+ETH only
- **All results in-sample (2020–2025) — treat as search ranges, not targets**
- Independently validates ATR trailing stop as dominant exit component
- ATR trail trigger 8.57 (suspicious precision — in-sample artefact; not used)
- ~22 trades/year on 2 pairs: fails frequency objective as standalone

### Huang, Sangiorgi & Urquhart (SSRN 4825389, 2024)
*"Cryptocurrency Volume-Weighted Time Series Momentum"*

- Volume-weighted WML portfolio outperforms capital-weighted
- Optimal TSMOM lookback: 3–7 days (consistent with L=24 bars = 6 days on H6)
- Effect attenuated post-2018 — relevant caution for Phase 1 volume-weighted enhancement
- Portfolio-level evidence only; single-pair translation unvalidated
- Phase 1 candidate enhancement only

---

## Part 6: What Not To Repeat

| Anti-pattern | Lesson |
|---|---|
| Running combined (can_short=True) before long-only baseline | Skips the diagnostic isolation step; composite PF obscures which leg is profitable |
| Accepting ATR_MULT from paper without testing | Paper's 2.5 was too tight for our universe; always confirm empirically |
| Treating paper SR 2.41 as the baseline | Fixed-param baseline is ~1.34; our fee-adjusted realistic target is lower still |
| Evaluating long-only results without market context | 2022 −69% market change makes any long-only result look bad; regime splits are mandatory |
| Trusting backtest cache across parameter changes | Always pass `--cache none` and verify the strategy snapshot in results |
| Mid-cap results without survivorship bias caveat | Delisted pairs are excluded; upper-bound interpretation required |

---

*Created 2026-04-08 by Claude + developer. Phase 0 V01 complete; V02 in progress.*
