# Cross-Sectional Momentum (Candidate G) — Phase 1 Summary

**Project:** freqtrade-strategy-lab  
**Candidate status:** **PARKED (2026-03-29)** — **empirically weak** after Phase 1; **no active development**. **Reopen** only if an **add-on or tool** plausibly addresses a **documented weakness** (see **`AlgoTrading_Research_Log.md`** → Candidate G). **All artifacts retained** (strategy, config, this doc).

**Document status:** Living document — Phase 1 **multi-year grid complete** (2026-03-29). Optional work is **not scheduled** unless G is reopened.  
**Last updated:** 2026-03-29  

---

## Phase 1 vs Phase 1a (plain English)

- **Phase 1 (full):** Multi-year backtests on the strategy grid, long+short vs long-only, regime tilt A/B, calendar-year splits, and explicit attribution notes. **Executed** on timerange **2022-01-01 → 2025-01-01** (effective first trades often **2022-01-13** after `startup_candle_count: 300`), **1h** candles, **`config_xsmom.json`**, **`--fee 0.0005`** (5 bps/side), **`--cache none`** when comparing variants.

- **Phase 1a:** Earlier **2023-only** smoke tests — still useful as a **single-year** sanity check but **not** the go/no-go basis.

---

## Reminder: what this strategy does

**~22 Binance USDT-M futures**, ranked by formation-period return on **1h** bars. **Long** top **N**, **short** bottom **N** (V01), or **long winners only** (V02). Rebalance on a UTC grid (**4h** or **1d** hold). Exits: **time stop**, **trailing stop**, **hard stop** (−12%). Up to **3×** leverage where allowed.

**V03/V04** add **regime tilt**: BTC-based multipliers on **stake** and **leverage** only (same **fixed −12%** stop as V01/V02 since 2026-03-29 — see *Implementation note* below).

---

## Standard backtest command (PowerShell, one line)

From **freqtrade-strategy-lab**:

`docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy <STRATEGY_CLASS> --timerange 20220101-20250101 --timeframe 1h --fee 0.0005 --cache none`

---

## Phase 1 results: full grid (2022-01-01 → 2025-01-01)

| Strategy | Horizon | L/S | Regime tilt | Trades (approx.) | Total profit % | Max DD % (report) | Verdict |
|----------|---------|-----|-------------|------------------|----------------|-------------------|---------|
| **V01_1d** | 1d | L/S | Off | ~7,312 | **~+17%** | ~54% | Only variant clearly **positive** full-sample; **profit factor ~1** — fragile. |
| **V01_4h** | 4h | L/S | Off | ~40,148 | **~−99.6%** | ~99.8% | **No-go** — majority of exits **`time_stop`** (Lesson #11-style churn). |
| **V02_1d** | 1d | Long only | Off | ~3,664 | **~−76.5%** | — | **No-go** — shorts mattered economically vs V01 on this window. |
| **V02_4h** | 4h | Long only | Off | 20,706 | **−97.69%** | ~98.6% | **No-go** — ~62% exits **`time_stop`**. |
| **V03_1d** / **_fair** | 1d | L/S | On (stake/lev) | ~7,303 | **−6.41%** | ~53% | Tilt **hurts** vs V01 here; **not** a wipeout once stop/startup aligned. |
| **V04_1d** / **_fair** | 1d | Long only | On | ~3,598 | **−76.7%** | ~83% | Same story as V02_1d; tilt does not rescue long-only. |

**Long vs short (V01_1d, full sample, prior run):** Dollar P&amp;L was **negative on longs** and **positive on shorts** — the short book **net-carried** the strategy over the period; do not assume “momentum = long-only” without testing.

**Regime tilt — important implementation note (2026-03-29):** An earlier **V03/V04** bundle used **`use_custom_stoploss=True`** (vol-widened stop toward **−22%**) and **`startup_candle_count=1000`**. That combination produced **~−99%** equity in backtest — **not** attributable to stake/lev tilt alone. **Code now aligns V03/V04 with V01/V02** on stop and startup; tilt applies **`custom_stake_amount`** and **`leverage()`** only. **`V03_1d_fair` / `V04_1d_fair`** are **CLI aliases** of **V03_1d** / **V04_1d**.

---

## Calendar-year splits: **V01_1d** only

Same fee and config; each row is **isolated** to that date range (not compounded across rows).

| Window (timerange) | Backtest from → to (log) | Trades | Total profit % | Max DD % (report) |
|--------------------|---------------------------|--------|----------------|-------------------|
| **20220101–20230101** | 2022-01-13 → 2023-01-01 | 1,631 | **+70.68%** | ~18.2% |
| **20230101–20240101** | 2023-01-01 → 2024-01-01 | 2,804 | **+14.27%** | ~42.0% |
| **20240101–20250101** | 2024-01-01 → 2025-01-01 | 2,878 | **−40.35%** | ~53.5% |

**Read:** Full-sample **~+17%** is **not** uniform — **2022–2023** lifts the curve; **2024** is **deeply negative**. This is consistent with **bull/regime sensitivity** and **short-leg behavior** (Lesson #10).

---

## Phase 1 go / no-go (condensed)

**Registry:** Candidate G is **PARKED** — the rows below are **historical Phase 1 conclusions**, not an active roadmap.

| Item | Decision |
|------|----------|
| **1d L/S baseline (V01_1d)** | **Marginal** full-sample result — **high DD**, **PF ~1**, **year-to-year unstable**; **not** enough for production. |
| **4h grid (V01_4h / V02_4h)** | **NO-GO** as implemented. |
| **Long-only (V02_1d)** | **NO-GO** on this universe/window. |
| **Regime tilt (V03/V04)** | **NO-GO as net improvement** vs V01 on this run; **safe defaults** match control stop/startup. |
| **Phase 2 (risk-managed / hyperopt / WFO)** | **Unscheduled** — **reopen** only with a **named add-on** per Research Log (Candidate G). |

---

## How to read this without fooling yourself

| Idea | Plain explanation |
|------|-------------------|
| **Backtest ≠ live** | Slippage, fills, funding, and your real fee tier differ. |
| **One good year ≠ edge** | **2022** dominated V01_1d; **2024** lost **~40%**. |
| **Confounded A/B kills trust** | Changing **stop width**, **startup**, and **tilt** together made **V03** look like a **−99%** “regime” failure; ablation showed the **stop/startup bundle** was the main villain. |
| **Long vs short** | Always split P&amp;L by side when shorts exist. |

---

## Related docs

- **Phase 0:** `CrossSectionalMomentum_Phase0_Summary.md`  
- **Technical / regime math:** `CrossSectionalMomentum_Deep_Dive.md`  
- **Original plan:** `CrossSectionalMomentum_Dev_Plan.md`  
- **Project context:** `AlgoTrading_Research_Log.md`  

---

*Candidate G is PARKED; document kept as historical record.*
