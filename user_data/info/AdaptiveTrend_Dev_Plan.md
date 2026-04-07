# AdaptiveTrend — Development Plan
## Candidate M from AlgoTrading Research Log
## Created: 2026-04-07 | Last updated: 2026-04-07
## STATUS: ACTIVE — Phase 0 (not yet started)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Pair with `AlgoTrading_Research_Log.md` §4.3 (Candidate M entry). A Deep Dive document will be created if Phase 0 produces a GO.

### What This Project Is

Systematic multi-pair momentum strategy (rate-of-change signal) on **6h candlesticks** across a fixed whitelist of **15–20 Binance USDT-M futures pairs**. ATR-calibrated trailing stop as the primary exit. 70/30 long/short slot allocation approximated via `max_open_trades` split. No ML, no sidecar, pure OHLCV.

**Source paper:** Bui & Nguyen (arXiv 2602.11708, Feb 2026) — *"Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets."* OOS: Jan 2022–Dec 2024 (36 months), 150+ pairs, SR 2.41, CAGR 40.5%, MDD −12.7% at 4 bps/trade costs.

**Supporting papers (analyzed 2026-04-07):**
- Karassavidis et al. (SSRN 5821842): validates ATR trailing stop as highest-value exit component (+0.73 SR in ablation). All results in-sample — treat parameter values as search ranges, not fixed targets.
- Huang et al. (SSRN 4825389): confirms volume-weighted momentum signal. Post-2018 attenuation noted. Phase 1 enhancement candidate only.

### Current Phase

| Phase | Status | Notes |
|-------|--------|-------|
| **0** | **NOT STARTED** | Fee-inclusive backtest + regime splits on fixed params |
| **1** | Pending Phase 0 GO | Add rolling Sharpe-based pair selection (monthly optimization) |
| **2** | Pending Phase 1 GO | Hyperopt on core parameters |
| **3** | Pending Phase 2 GO | Dry-run deployment |

### Critical Context Before Starting

**The MVP baseline is weaker than the paper headline.** The paper's SR 2.41 assumes monthly parameter optimization (+1.07 SR contribution per ablation study). Fixed-parameter MVP baseline is SR ~1.34. Phase 0 must be evaluated against this lower bar — not the headline number. SR > 1.0 and PF > 1.2 on fixed params would be a genuine Phase 0 success.

**Timeframe is 6h, not 4h, not 8h.** The paper tested H1/H4/H6/H8/D1 explicitly. H6 is optimal (SR 2.41). H4 is second (SR 2.08). H8 is third (SR 2.18). H1 significantly worse (SR 1.54). Do not deviate to H4 unless H6 produces no signal on Binance due to data availability issues.

**Fee sensitivity:** Paper baseline is 4 bps/trade. Our cost is 5 bps/side = 10 bps round-trip. Paper sensitivity table: 8 bps → SR 2.01, 12 bps → SR 1.62. At our 10 bps: estimated SR ~1.85. With fixed params (no monthly opt): adjust down further. Phase 0 must use `--fee 0.0005` throughout.

---

## Part 1: Strategy Summary

### 1.1 Algorithm

**Entry signal (long):**
```
MOM_t = (P_t - P_{t-L}) / P_{t-L}
Enter long if MOM_t > θ_entry
```

**Entry signal (short):**
```
Enter short if MOM_t < -θ_entry
```

**ATR trailing stop (long):**
```
S_t = max(S_{t-1}, P_t - α × ATR_t)
Exit long if P_t < S_t
```

**ATR trailing stop (short):**
```
S_t = min(S_{t-1}, P_t + α × ATR_t)
Exit short if P_t > S_t
```

**Default MVP parameters (Phase 0 starting point):**
| Parameter | Value | Source | Note |
|---|---|---|---|
| `L` (lookback bars) | 24 (= 6 days on H6) | Bui paper L range 1–30d | Center of 3–7d optimal from Huang; 6d ≈ 1-week momentum |
| `θ_entry` | 0.03 | Bui paper; start conservative | Sweep 0.01–0.07 in Phase 0 |
| `α` (ATR mult) | 2.5 | Bui paper optimal center | Paper range 2.0–3.5; Karassavidis 3.33 (in-sample) |
| `ATR_period` | 14 | Standard | — |

### 1.2 Portfolio construction (MVP approximation)

**Long universe:** Fixed whitelist of top-15 pairs by market cap — BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, DOT, LINK, UNI, ATOM, NEAR, APT, OP (all USDT perpetual, Binance Futures). Verify each has H6 data from 2022-01-01. Remove any pair without common history.

**Short universe:** Liquid subset only — ETH, SOL, BNB, XRP, ADA, AVAX (6 pairs). Paper uses bottom-KS by market cap (small caps) but we restrict to liquid alts to avoid slippage risk. Phase 1 decision: whether to expand short universe.

**70/30 allocation:** `max_open_trades = 15` total (10 long slots + 5 short slots). `stake_amount` equal per slot. Implement via two separate `max_open_trades` counters in `custom_info`, or approximate by restricting short entry to max 5 concurrent via `confirm_trade_entry()`.

**No monthly parameter optimization for MVP.** Fixed parameters throughout Phase 0. Sharpe-based pair selection (paper's SR ≥ 1.3 long / SR ≥ 1.7 short gate on prior month) is Phase 1 only.

### 1.3 What is NOT in Phase 0

- Monthly rolling Sharpe pair selection
- Volume-weighted signal (Huang et al.) — Phase 1 enhancement
- SMA crossover or RSI entry filter (Karassavidis) — not aligned with source paper's architecture; not in scope unless ROC signal underperforms
- Market cap filter (dynamic) — hardcoded whitelist for MVP
- EMA slope exit — negative evidence from Karassavidis; excluded

---

## Part 2: Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  Signal: 6h OHLCV → ROC(L=24) → threshold filter → entry/exit    │
│  Exit:   ATR(14) trailing stop (custom_stoploss)                  │
│  Portfolio: fixed whitelist, 70/30 long/short via custom_info     │
│  Config: config_adaptivetrend.json — H6, futures, fee 0.05%      │
│  No sidecar. No FreqAI. No ML.                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Freqtrade compatibility notes:**
- `timeframe = "6h"` — supported natively
- `custom_stoploss()` — already proven in LiqCascade/OracleSurfer stack
- `short_entry_signal` — requires `can_short: true` in config and futures mode
- 70/30 slot split via `confirm_trade_entry()`: track open long/short counts in `custom_info`, reject entries that exceed their respective slot cap
- `startup_candle_count`: max(L, ATR_period) + buffer = 24 + 14 + 10 = 48 bars (~12 days on H6)

---

## Part 3: Phase Plan

### Phase 0: Fee-inclusive validation + parameter sensitivity

**Goal:** Determine whether any ROC + ATR trailing stop configuration produces PF > 1.2 across regime splits with our fee structure. Validate long-only component separately before accepting short-side results.

**Tasks:**

1. Download H6 OHLCV for all whitelist pairs from 2021-07-01 (pre-period for startup candles):
   ```
   docker compose run --rm freqtrade download-data --config /freqtrade/config/config_adaptivetrend.json --timerange 20210701-20260407 --timeframes 6h --trading-mode futures
   ```

2. Run full-period baseline backtest (long-only first — set `can_short: false`):
   ```
   docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_adaptivetrend.json --strategy AdaptiveTrendStrategy_V01 --timerange 20220101-20250101 --timeframe 6h --fee 0.0005 --cache none
   ```

3. Run regime splits (same command, adjust `--timerange`):
   - 2022 bear: `20220101-20230101`
   - 2023 sideways: `20230101-20240101`
   - 2024 bull: `20240101-20250101`

4. Enable shorts (`can_short: true`) and rerun full-period + regime splits.

5. Parameter sensitivity sweep — vary `L` (12/24/42 bars = 3/6/10 days) and `θ_entry` (0.02/0.03/0.05) in a 3×3 grid. 9 backtest runs total.

6. Document regime-split table before declaring any GO.

**Phase 0 Go/No-Go gates (ALL must be met):**

| Gate | Threshold | Rationale |
|---|---|---|
| Profit factor (full period) | > 1.2 | MVP baseline SR ~1.34 → PF ~1.2 equivalent |
| Regime coverage | Positive (PF > 1.0) in ≥ 2 of 3 regime years | Prevents bull-only edge |
| Trade count | ≥ 150 over full period | Statistical minimum for trend-following |
| Long-only component | PF > 1.0 in isolation | Validates core signal before short-side noise |
| Fee-inclusive | Confirmed — `--fee 0.0005` throughout | Non-negotiable |

**Stop/pivot triggers (abort Phase 0 if any hit):**
- No parameter combination achieves PF > 1.0 across more than one regime year
- Trade count < 80 (signal too infrequent for our frequency objective)
- Long-only component loses money on the full period

### Phase 1: Rolling Sharpe pair selection + volume signal

**Prerequisite:** Phase 0 GO.

**Tasks:**
1. Implement monthly rolling Sharpe filter: compute prior-month SR per pair, enter longs only if SR ≥ 1.3, shorts only if SR ≥ 1.7.
2. Compare PF and SR vs Phase 0 fixed-param baseline — must show measurable improvement.
3. Evaluate volume-weighted ROC signal (Huang et al.): `MOM_t = VW_ROC(L)` where volume-weighting scales the signal by recent daily volume relative to its rolling mean. Compare vs plain ROC — does it improve win rate or reduce false entries?
4. If either enhancement improves results: add to strategy, rerun regime splits.
5. Go/No-Go: rolling Sharpe selection must improve SR by ≥ 0.1 over fixed-param baseline to justify the added complexity.

### Phase 2: Hyperopt

**Prerequisite:** Phase 1 GO.

**Hyperopt space:**
- `L`: 12–42 bars (3–10 days on H6)
- `θ_entry`: 0.01–0.08
- `α` (ATR mult): 2.0–4.0
- `ATR_period`: 10–21
- SR threshold for longs: 0.8–1.5
- SR threshold for shorts: 1.2–2.0

**Command:**
```
docker compose run --rm freqtrade hyperopt --config /freqtrade/config/config_adaptivetrend.json --strategy AdaptiveTrendStrategy_V01 --hyperopt-loss SharpeHyperOptLoss --timerange 20220101-20240101 --timeframe 6h --fee 0.0005 --epochs 200
```

OOS validation on 2024 data after hyperopt — must not show significant degradation.

### Phase 3: Dry-run deployment

**Prerequisite:** Phase 2 GO.

**Tasks:**
1. Create production config `config_adaptivetrend_dryrun.json`
2. Add to DigitalOcean droplet alongside LiqCascade/OracleSurfer
3. Go/No-Go: PF > 1.0, win rate > 40% after **30 closed trades or 90 days**, whichever comes first. At ~23 trades/month (142/month × 15/150 scale), 30 trades ≈ 5–6 weeks.

---

## Part 4: What Not To Repeat

| Anti-pattern | Addressed |
|---|---|
| Building before fee/regime evidence | Phase 0: all backtests use `--fee 0.0005`, regime splits mandatory |
| Assuming paper SR transfers to MVP | Explicitly: fixed-param baseline SR ~1.34, not 2.41 |
| Short-side without validating long-only first | Phase 0: long-only run before enabling shorts |
| Overfit parameter values from supporting papers | Karassavidis trail trigger (8.57 ATR) treated as in-sample artifact; not used |
| Frequency too low | Monitor: if trade count < 150, pivot to H4 or expand whitelist before parting |
| Volume-weighted signal before baseline proven | Huang et al. volume enhancement is Phase 1 only |

---

## Part 5: File Locations

| File | Purpose | Status |
|------|---------|--------|
| `user_data/strategies/AdaptiveTrendStrategy_V01.py` | Phase 0 MVP — ROC + ATR trailing | **To build** |
| `config/config_adaptivetrend.json` | Futures whitelist, H6, fee config | **To build** |
| `user_data/info/AdaptiveTrend_Dev_Plan.md` | THIS FILE | Created 2026-04-07 |
| `user_data/info/AdaptiveTrend_Deep_Dive.md` | Technical deep dive | Created on Phase 0 GO |

---

## Part 6: Reference Material

### 6.1 Source paper

**Bui & Nguyen (arXiv 2602.11708, Feb 2026)** — "Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets"
- OOS: Jan 2022–Dec 2024, 150+ pairs, H6 bars
- SR 2.41 (full strategy) → SR 1.34 (fixed params, no monthly optimization)
- ATR trailing stop: highest single-component contribution (+0.73 SR)
- Monthly optimization: +1.07 SR (Phase 1 only)
- Fee sensitivity: 8 bps → SR 2.01, 12 bps → SR 1.62
- Organization: Talyxion Research, Hanoi — no institutional pedigree; bootstrap significance strong but no independent replication yet

### 6.2 Supporting papers

**Karassavidis et al. (SSRN 5821842)** — "Quantitative evaluation of volatility-adaptive trend-following models in cryptocurrency markets"
- Architecture: SMA(10/38) crossover + RSI filter + ATR trailing stop on H8, BTC+ETH only
- **Critical caveat: ALL results in-sample (2020–2025). No walk-forward validation.**
- SR 1.67, CAGR 22%, MaxDD 11% — treat as ceiling, not production expectation
- Key M contribution: independently validates ATR trailing stop as dominant exit component; EMA slope exit explicitly discarded (inferior)
- ATR trail trigger (8.57 ATR) is suspicious precision — treat as in-sample artifact
- ~22 trades/year — fails our frequency objective as standalone; not a separate candidate

**Huang, Sangiorgi & Urquhart (SSRN 4825389, 2024)** — "Cryptocurrency Volume-Weighted Time Series Momentum"
- Volume-weighted WML portfolio outperforms capital-weighted
- Optimal TSMOM lookback: 3–7 days (aligns with M's L=24 bars = 6 days default)
- Effect attenuated post-2018 — weight this finding before committing to volume enhancement
- Transaction costs material at 20 bps (we're at 10 bps — less severe but not negligible)
- Portfolio-level evidence only; single-pair translation unvalidated
- Not a separate candidate; potential Phase 1 enhancement for M only

### 6.3 Freqtrade implementation notes

- **ATR trailing stop:** `custom_stoploss()` — same pattern as LiqCascade V05 and OracleSurfer v14. Copy and adapt.
- **Short-side 70/30 split:** Track `n_longs` and `n_shorts` in `custom_info` dict keyed by bot instance. Check counts in `confirm_trade_entry()` before approving entry.
- **H6 data availability:** Binance futures H6 bars are supported via CCXT; verify data runs back to 2021-07-01 for all whitelist pairs before running backtests.
- **Startup candles:** `startup_candle_count = 50` (covers max(L=24, ATR=14) + buffer).
- **`--cache none`:** Always use for Phase 0 runs since parameters are changing.

---

*Created 2026-04-07 by Claude + developer.*
*Phase 0 not yet started.*
