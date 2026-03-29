# Cross-Sectional Crypto Momentum (Candidate G) — Deep Dive
## Version 1.3 | Started: 2026-03-22 (plan) / 2026-03-29 (implementation) | Status: **PARKED** — Candidate G **empirically weak**; implementation + Phase 1 results **retained** for reference. **Reopen** policy: **`AlgoTrading_Research_Log.md`** (Candidate G). Technical reference below remains valid.

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session** for this project.  
> Pair with `AlgoTrading_Research_Log.md` for registry, roles, and lessons.  
> Shorter **layman** summaries: `CrossSectionalMomentum_Phase0_Summary.md`, `CrossSectionalMomentum_Phase1_Summary.md`.  
> Original phase checklist: `CrossSectionalMomentum_Dev_Plan.md`.

### Current Status (high level)

| Item | State |
|------|--------|
| **Phase 0** | **Done** — data downloaded, dispersion / rank exploration script run. |
| **Phase 1a** | **Done** — Freqtrade strategy **V01/V02** (4h and 1d variants) implemented; **2023-only** smoke backtests executed (not final validation). |
| **Phase 1 (full)** | **Done (baseline grid)** — see **`CrossSectionalMomentum_Phase1_Summary.md`**. Candidate **PARKED** after results; optional follow-ups **unscheduled**. |
| **Regime “tilt” overlay** | **Implemented** — **`V01` / `V02`:** tilt **off**. **`V03` / `V04`:** tilt **on** — BTC vol + trend drive **`custom_stake_amount`** and **`leverage()`** only; **same fixed −12% stop and `startup_candle_count` 300 as V01/V02** (since v1.2). Optional vol-based stop widening remains in **`_build_regime_frame`** but is **not** applied unless a subclass sets `use_custom_stoploss = True`. |

### When to “shift gears” and turn on regime tilting

Use **judgment**, not one metric. **Turn on or intensify** regime-based stake/leverage/stop **tilts** only after **most** of the following are true:

1. **Full Phase 1 grid** has been run on **V01 / V02** with **tilt off** (control), over **2022–2025+** (or dev-plan timerange), with trades exported.  
2. You can **explain** poor years: e.g. shorts bleeding in bulls (Lesson #10 style), or time-stop dominance (LiqCascade Lesson #11 analogue).  
3. A **hypothesis** fits: e.g. “short book needs scaling down when benchmark trend is strongly up.”  
4. Any tilt is **small** (narrow multiplier bands), **documented**, and tested **side-by-side** against the same code with tilt **off**.

If the **core** ranking shows **no** edge even long-only across years, **tilting won’t save it** — go back to design before tuning overlays.

### Key Commands (PowerShell-friendly, single lines)

```text
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_xsmom.json --timerange 20220101-20260101 --timeframes 1h
```

```text
docker compose run --rm --entrypoint python freqtrade user_data/scripts/xsmom_phase0_exploration.py
```

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V01_1d --timerange 20220101-20250101 --timeframe 1h --fee 0.0005 --export trades
```

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_xsmom.json --strategy XSMomentumStrategy_V03_1d --timerange 20220101-20250101 --timeframe 1h --fee 0.0005 --export trades
```

(Strategy classes: **Control** — `V01_*`, `V02_*`. **Regime tilt on** — `V03_*` (= V01 + tilt), `V04_*` (= V02 + tilt). See Part 5.)

### File Locations

| File | Status | Purpose |
|------|--------|---------|
| `user_data/info/CrossSectionalMomentum_Deep_Dive.md` | **THIS FILE** | Authoritative technical + layman reference for Candidate G |
| `user_data/info/CrossSectionalMomentum_Dev_Plan.md` | Active | Original phase gates and paper references |
| `user_data/info/CrossSectionalMomentum_Phase0_Summary.md` | Active | Layman Phase 0 results |
| `user_data/info/CrossSectionalMomentum_Phase1_Summary.md` | Living doc | Phase 1a results; update after full Phase 1 |
| `user_data/strategies/XSMomentumStrategy_V01.py` | Active | V01–V04 strategy classes (4h/1d; V03/V04 = regime tilt on) |
| `config/config_xsmom.json` | Active | 22-pair futures whitelist, `max_open_trades`, etc. |
| `user_data/scripts/xsmom_phase0_exploration.py` | Active | Phase 0 dispersion / rank diagnostics |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Candidate G evaluation (7/7), priority ranking |

---

## Part 1: Why This Project Exists (Layman + Context)

### 1.1 One-sentence idea

**Buy the recent leaders and (optionally) sell short the recent laggards among a basket of liquid crypto futures, on a fixed schedule, using only ordinary price data.**

That’s **cross-sectional momentum**: profit comes from **relative** strength, not from guessing whether *all* of crypto is up or down.

### 1.2 Why the research program cares

Earlier lab candidates failed for **specific** reasons:

- **Too little profit per trade after fees** (high-frequency microstructure idea).  
- **Almost no trades** (slow mean-reversion pair on one spread).  
- **Naked directional risk** on a complex signal (path-signature MVP).

Candidate G was scored **7/7** on the evaluation filter because it uses **OHLCV only**, should produce **enough trades** when many pairs rebalance, and **hourly-to-daily moves** are usually **much larger** than ~**10 basis points** round-trip fees. See `AlgoTrading_Research_Log.md` Candidate G section for papers (Drogen et al., Han et al., risk-managed momentum, etc.).

### 1.3 How this complements Liquidation Cascade (LiqCascade)

| | LiqCascade | Cross-sectional momentum (this) |
|---|------------|----------------------------------|
| **Signal** | A **specific event** (liquidation cascade) | **Continuous ranking** across a universe |
| **Data** | WebSocket / sidecar + OHLCV | OHLCV only |
| **Character** | Burst, event-driven | Steady, systematic |

They are meant to **diversify how** the book makes money, not replace each other.

---

## Part 2: Plain English — How the Current Bot Thinks

Think of **22 racers**. Every **4 hours** or every **day** (depending on version):

1. **Look back** the same amount of time (4 hours or 1 day) and compute how much each racer **gained or lost**.  
2. **Sort** them: who’s ahead, who’s behind.  
3. **Long+short version (V01):** put money on the **top few** and **bet against** the **bottom few**.  
4. **Winner-only version (V02):** put money only on the **top few** — **no** short bets (research often says the “loser” side is trickier in crypto).  
5. **Optional “tilt” (V03/V04 only):** same as V01/V02, but the bot also looks at **Bitcoin’s** recent **choppiness** and **direction** to **nudge** position size and **leverage** — **without** turning strategies fully on or off (see Part 6). **Default V03/V04 do not widen the hard stop** (same −12% as control).  
6. **Wait** until that same time window passes, then **repeat** the ranking.  
7. **Safety rails:** a **maximum hold time** (time stop), a **trailing stop** (lock in profit / cap give-back), a **hard stop** if things go badly wrong, and **modest leverage** (capped at 3× in code, then scaled again slightly if tilt is on).

**Important:** The bot does **not** know the future. It only knows **past** returns over the formation window. Whether that predicts **next** window’s returns is exactly what **backtesting** is for.

---

## Part 3: Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│           CROSS-SECTIONAL MOMENTUM (Candidate G)                   │
├────────────────────────────────────────────────────────────────────┤
│  Inputs: Binance USDT-M futures OHLCV, 1h candles                  │
│  Universe: ~22 liquid pairs (StaticPairList in config_xsmom)     │
│                                                                    │
│  For each pair’s dataframe (Freqtrade calls populate_indicators):  │
│    • Build aligned panel of closes across whitelist (DataProvider)│
│    • Formation return = price change over N bars (N=4 or 24)     │
│    • Require ≥15 valid pairs per bar for a trustworthy rank       │
│    • Rank: top TOP_N → long candidates; bottom BOTTOM_N → shorts   │
│    • Rebalance entries on UTC hour grid (4h: hour%4==0; 1d: h=0) │
│    • Regime tilt (V03/V04): BTC vol ratio + trend → stake / lev      │
│                                                                    │
│  Entries: enter_long / enter_short per populate_entry_trend       │
│  Exits: custom_exit time_stop after HOLDING_CANDLES hours;         │
│         trailing + fixed stoploss (−12%); optional custom_stoploss  │
│         only if enabled on a subclass (not default V03/V04)        │
│                                                                    │
│  No sidecar. No FreqAI in baseline V01–V04.                        │
└────────────────────────────────────────────────────────────────────┘
```

**Caching:** Cross-sectional signals (and regime series when tilt is on) are computed once per indicator “chunk” (cache key includes `REGIME_TILT_ENABLED`) so all pairs don’t rebuild the full panel 22 times per step.

**Startup candles:** **300** for all variants (same as V01/V02). Regime windows (168 / 720 bars) are satisfied once the backtest has enough BTC history in the slice.

---

## Part 4: Phase History (What’s Done vs Next)

| Phase | Goal (layman) | Status |
|-------|----------------|--------|
| **0** | “Is there enough **spread** between coins after a few hours/days to matter after fees? Are rankings stable enough to be worth testing?” | **Done.** See Phase 0 summary: 1h median dispersion slightly under 50 bps; **4h+** clearly above — Phase 1 emphasizes **≥4h formation** as primary. |
| **1a** | “Does the code run, and what does **one year** (2023) look like?” | **Done.** V01 4h: heavy activity, poor result on that year; V01 1d: fewer trades, positive on that year — **not** validation. |
| **1 (full)** | Multi-year, V02, long/short split, regimes, export trades, fee check vs dev-plan gates | **Baseline complete** — table + year splits + go/no-go in **`CrossSectionalMomentum_Phase1_Summary.md`**. |
| **2** | Risk-managed variant (e.g. vol-scaled sizing), hyperopt, walk-forward | Per dev plan — **after** Phase 1 go/no-go. |
| **3** | Dry-run deployment | Per dev plan. |

---

## Part 5: Strategy Variants and Parameters (Technical Reference)

**Module:** `user_data/strategies/XSMomentumStrategy_V01.py`

| Class | Formation (bars) | Hold (hours) | Long | Short | Regime tilt |
|-------|------------------|--------------|------|-------|-------------|
| `XSMomentumStrategy_V01_4h` | 4 | 4 | Yes | Yes | **Off** |
| `XSMomentumStrategy_V01_1d` | 24 | 24 | Yes | Yes | **Off** |
| `XSMomentumStrategy_V02_4h` | 4 | 4 | Yes | No | **Off** |
| `XSMomentumStrategy_V02_1d` | 24 | 24 | Yes | No | **Off** |
| `XSMomentumStrategy_V03_4h` | 4 | 4 | Yes | Yes | **On** |
| `XSMomentumStrategy_V03_1d` | 24 | 24 | Yes | Yes | **On** |
| `XSMomentumStrategy_V04_4h` | 4 | 4 | Yes | No | **On** (stake + lev) |
| `XSMomentumStrategy_V04_1d` | 24 | 24 | Yes | No | **On** |
| `XSMomentumStrategy_V03_1d_fair` | 24 | 24 | Yes | Yes | **On** — **alias of `V03_1d`** |
| `XSMomentumStrategy_V04_1d_fair` | 24 | 24 | Yes | No | **On** — **alias of `V04_1d`** |

**Key class attributes:** `TOP_N`, `BOTTOM_N` (default 4), `MIN_VALID_PAIRS` (15), `stoploss`, trailing settings, `leverage()` cap 3× (then multiplied by regime when tilt on).

**Backtest fee:** Typically `--fee 0.0005` (5 bps per **side**; ~10 bps round trip) unless your real tier differs.

**Hooks (tilt on):** `custom_stake_amount`, `leverage()`. **`custom_stoploss` / `use_custom_stoploss`:** default **False** on **V03/V04** (same as V01/V02). Subclasses may enable dynamic stops for experiments; Phase 1 showed vol-widened stops + high leverage are **dangerous** without careful caps.

---

## Part 6: Regime Tilt — “Middle Path” (Implemented)

### 6.1 Plain English

On **V03** and **V04**, the bot still uses the **same ranking** as V01/V02. On top of that, it watches **Bitcoin** (the benchmark) for two slow-moving clues:

1. **How jumpy is the market lately?** If recent **volatility** is **high** compared with the last ~30 days, the bot **slightly shrinks** how much you bet and how much leverage you use — a “take less risk when things are wild” idea (similar in spirit to **volatility targeting** and **risk-managed momentum** in the literature). The code can compute a **vol-widened** stop for experiments, but **default V03/V04 do not apply it** (fixed −12% stop matches V01/V02).

2. **Has Bitcoin been drifting up a lot over the last week?** If yes, the bot **nudges short positions smaller** and **nudges long positions a tiny bit larger** — not a ban on shorts, just a **tilt** that says “in a strong-up environment, be a bit more careful on the short side.”

Nothing here is a **hard switch** that says “no trades.” Multipliers stay in **tight bands** (roughly **0.85–1.0** for vol-related risk scaling) so behavior stays comparable to the control strategies for fair A/B tests.

### 6.2 Technical detail (for implementation / tuning)

All computed on **`REGIME_BENCHMARK_PAIR`** (default `BTC/USDT:USDT`), 1h:

| Building block | Meaning | Default params (class attributes) |
|----------------|---------|-------------------------------------|
| `vol_roll` | Std dev of BTC hourly returns | `REGIME_VOL_WINDOW` = 168 (~7d) |
| `ratio` | `vol_roll / rolling_median(vol_roll)` over `REGIME_VOL_RATIO_WINDOW` = 720, clipped to [0.5, 2.5] | High ratio = unusually jumpy recently |
| `stake_vol_mult` | Maps `ratio` linearly into [`REGIME_STAKE_VOL_MIN`, `REGIME_STAKE_VOL_MAX`] (0.85–1.0) | Shrinks size + lev in high vol |
| `trend_mom` | BTC `pct_change` over `REGIME_TREND_BARS` (168) | Raw trend dial |
| `trend_sig` | `tanh(trend_mom * REGIME_TREND_TANH_SCALE)` | Squashed to a smooth −1…1 scale |
| Long stake | `stake_vol_mult * (1 + REGIME_LONG_BULL_BONUS * max(trend_sig,0))`, clipped [0.75, 1.12] | Small boost when BTC trend_sig bullish |
| Short stake | `stake_vol_mult * (1 - REGIME_SHORT_BULL_TILT * max(trend_sig,0))`, clipped [0.75, 1.0] | Up to ~12% smaller shorts when bullish |
| Leverage | `stake_vol_mult` clipped to [`REGIME_LEVERAGE_MIN`, `REGIME_LEVERAGE_MAX`] | Same vol dial |
| Stop (series in dataframe) | `stoploss - widen` where `widen` ∈ [0, `REGIME_STOP_VOL_WIDEN` (=0.03)] from `ratio`, result clipped to [-0.22, `stoploss`] | **Only affects exits if `use_custom_stoploss` is True** on the strategy class (default **False** on V03/V04). |

### 6.3 Backtest lesson — confounded “regime” bundle (2026-03-29)

A short-lived implementation paired **regime tilt** with **`use_custom_stoploss=True`** (applying the widened stop above) and **`startup_candle_count = 1000`**. Multi-year backtests showed **~−99%** equity while **tilt-only** (fixed stop, startup 300) landed near **−6%** vs control **V01_1d ~+17%**. **Conclusion:** the catastrophe was **not** “BTC dials bad” in isolation — it was mainly **wider hard stops × leverage × path**. **Default V03/V04 were corrected** to match control stop and startup; treat any future dynamic-stop experiment as **high risk** and **ablate separately**.

**Rules of engagement (unchanged):**

- **Control runs:** Use **V01 / V02** (tilt **off**) for baseline Phase 1.  
- **Experiment runs:** Use **V03 / V04** with **identical** timerange and `--fee`, then compare.  
- **Do not** treat tilt as validated until A/B and multi-year checks say so.

---

## Part 7: Phase 0 / Phase 1 Results (Pointers)

- **Phase 0 (numbers + layman read):** `CrossSectionalMomentum_Phase0_Summary.md`  
- **Phase 1 (full grid + year splits + go/no-go):** `CrossSectionalMomentum_Phase1_Summary.md`  

Do **not** treat backtests as **go** for live capital without independent robustness work.

---

## Part 8: Phase 1 Go / No-Go (From Dev Plan — Reminder)

Before promoting to Phase 2, the dev plan targets (paraphrased):

- At least one formation/hold combo **profitable after realistic fees**.  
- Profit factor and trade frequency above documented floors.  
- Results **not** explained by a **single** lucky year (check **2022 bear**, **2024+**).  
- **Lesson #10 check:** if longs win and shorts lose in the same period, ask whether the “edge” is **beta**, not **ranking**.

Exact numeric gates stay in `CrossSectionalMomentum_Dev_Plan.md`.

---

## Part 9: Lessons From Prior Projects (Applied Here)

| Lesson | Application |
|--------|-------------|
| Fee economics first (LOB) | Phase 0 dispersion; backtests use explicit `--fee`. |
| ML accuracy ≠ edge (RAME) | Baseline **no FreqAI** — ranking is transparent math. |
| Bull-market validation bias (CointPairs) | **Year splits** and long/short attribution required in full Phase 1. |
| Don’t layer complexity before core signal (RAME) | Regime tilt **implemented** on V03/V04 but **V01/V02 remain default control** (tilt off). |
| Path signatures MVP (E) | Candidate **I** (signature-augmented ranking) remains **deferred** until **G** standalone validates — see Research Log. |

---

## Part 10: Version History (This Document)

| Date | Change |
|------|--------|
| 2026-03-29 | v1 — Initial Deep Dive: architecture, phases, middle-path regime policy, file map, shift-gears criteria. |
| 2026-03-29 | v1.1 — Regime tilt **implemented** in code (`V03`/`V04`); Part 5–6 and Quick-Start updated; Part 3 architecture box updated. |
| 2026-03-29 | v1.2 — Phase 1 baseline results linked; **V03/V04** aligned with V01/V02 on **fixed stop** and **startup 300**; **Part 6.3** documents confounded −99% backtest lesson; `_fair` classes documented as **aliases**; architecture / hooks text updated. |
| 2026-03-29 | v1.3 — Status **PARKED** (empirically weak); Quick-Start Phase 1 row note; no technical rollback. |

---

*Reference doc for parked Candidate G.*
