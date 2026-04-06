# Ensemble Donchian Trend-Following — Development Plan
## Candidate J from AlgoTrading Research Log
## Created: 2026-03-31 | **Last updated: 2026-04-06**
## **STATUS: PARKED** — Phase 0 **NO-GO**. See `AlgoTrading_Research_Log.md` §4.3–4.4 and `EnsembleDonchianTrend_Deep_Dive.md` (v1.5). **No further development** unless the candidate is **reopened** as a new hypothesis.

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session.**
> Pair with `user_data/info/EnsembleDonchianTrend_Deep_Dive.md` (authoritative implementation detail) and `AlgoTrading_Research_Log.md`.

### What This Project Is

Ensemble Donchian trend-following on a **14-pair** Binance USDT-M futures whitelist: **nine calendar-day lookbacks** (paper: 5–360d) computed on **`1d` OHLCV**, merged to **`1h`** for entries, vol/ATR, and order simulation (**`EnsembleDonchianStrategy_V01`**). Optional **`1d`-native** execution (**`EnsembleDonchianStrategy_V02`**) tests whether daily signals should be traded on daily candles only (less fee churn / simpler alignment). Long-only; inverse-vol sizing; Donchian-lower or ATR trailing. Candidate J scored **7/7** in the Research Log.

### Current Phase (**PARKED 2026-04-06**)

| Phase | Status | Notes |
|-------|--------|--------|
| **0** | **CLOSED — NO-GO** | `donchian_phase0_sweep.py` + manual backtests; **failed** profitability / robustness vs Dev Plan gates. Artifact: `user_data/results/donchian_phase0_sweep_20260406_105346.md`. |
| **1** | **Frozen** | Code retained: V01/V02, config, sweep script — **reference only**. |
| **2–3** | **Cancelled** | No Phase 0 GO. |

**Reopen policy:** Only via explicit Research Log decision and a **new Phase 0 charter** (e.g. different universe, filters, fee model, or execution design). Tweaking the current MVP without that is **out of scope** while PARKED.

### Implementation Realities (non-negotiable for stock Freqtrade + Binance)

- **Nine Donchian channels on raw `1h` bars out to 360 days (~8640h)** hits Freqtrade’s **startup / exchange chunk cap** (~**2494** one-hour bars). The supported design is **`1d` informative** for Donchian math + **`1h`** base timeframe for execution (V01), or **pure `1d`** (V02).
- **Whitelist** is **14 pairs** with **common `1d` history from 2022-01-01** (late-listed alts removed). See `config/config_donchian.json`.

### Key Commands (PowerShell, single lines)

Data (always use **`1h` + `1d`** futures):

```text
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_donchian.json --timerange 20220101-20260401 --timeframes 1h 1d --trading-mode futures
```

Backtest examples:

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V01 --timerange 20220101-20250101 --timeframe 1h --fee 0.0005 --cache none
```

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V02 --timerange 20220101-20250101 --timeframe 1d --fee 0.0005 --cache none
```

Phase 0 sweep (aggregates many runs; writes `user_data/results/donchian_phase0_sweep_*.json` + `.md`):

```text
docker compose run --rm --entrypoint python freqtrade user_data/scripts/donchian_phase0_sweep.py
```

---

## Part 1: Strategy Summary (updated)

### 1.1 What the running strategies do

**V01 (`timeframe = 1h`, Donchian on `1d`):**

1. For each pair, on **daily** bars: Donchian upper/lower at **`LOOKBACK_DAYS`** = (5, 10, 20, 30, 60, 90, 150, 250, 360).
2. Binary breakout per window: daily close > prior upper band.
3. **Ensemble score** = mean of nine signals (0–1), merged to each **1h** row (`merge_informative_pair`).
4. **Enter long** if score > `ENTRY_THRESHOLD` (default 0.5) and volume > 0.
5. **Exit:** ratcheted **Donchian lower** on the shortest active lookback **at entry** (daily bands on merged columns), or **ATR** trailing on **1h** (`_V01_ATR`); hard stop; **time stop** (default 720h).
6. **Stake:** inverse-vol vs cross-sectional median on **1h** returns (168-bar window).

**V02 (`timeframe = 1d`):** Same Donchian ensemble and exits on the **native daily** dataframe (no merge). Vol scaling uses **daily** returns (~21-day window). Use to test **execution timeframe = signal timeframe**.

### 1.2 Key academic findings

(Unchanged — see Deep Dive §1.2 / prior plan.) Zarattini et al. daily ensemble; multi-timeframe literature supports robustness.

### 1.3 Variants for Phase 0 sweeps

| Class | Purpose |
|-------|---------|
| `EnsembleDonchianStrategy_V01` / `_V01_ATR` | Default hybrid 1d-signal / 1h-exec |
| `EnsembleDonchianStrategy_V01_Entry030` … `_Entry090` | Entry threshold grid (0.3–0.9) |
| `EnsembleDonchianStrategy_V01_LookbackAblated` | Drops 150/250/360d windows |
| `EnsembleDonchianStrategy_V02` / `_V02_ATR` | Pure daily execution |

### 1.4 Difference from G

(Unchanged in spirit — J is per-asset breakout + trailing exit vs cross-sectional rank + rebalance.) Universe is **smaller and homogenous in history** than G’s 20+ list.

---

## Part 2: Architecture (updated)

```
┌────────────────────────────────────────────────────────────────────┐
│  V01: 1d Donchian → merge to 1h → entries / vol / ATR / fills     │
│  V02: 1d Donchian on native 1d dataframe → daily fills             │
├────────────────────────────────────────────────────────────────────┤
│  Config: config_donchian.json — 14 pairs, futures, fees in CLI    │
│  Sweep: user_data/scripts/donchian_phase0_sweep.py                  │
│  No sidecar. No FreqAI.                                             │
└────────────────────────────────────────────────────────────────────┘
```

**Capacity:** Override with `freqtrade backtesting --max-open-trades N` to test 5 vs 8 vs 10 concurrent positions.

---

## Part 3: Phase Plan (revised gates)

### Phase 0: Empirical validation + sweeps

**Goal:** Determine whether **any** fee-inclusive, regime-stable operating point exists for the hybrid (V01) or daily (V02) designs.

**Tasks:**

1. Maintain **full `1h` + `1d`** history for all 14 pairs (`download-data`).
2. Run **`donchian_phase0_sweep.py`** (or manual backtests): regimes e.g. **2022**, **2023**, **2024**, **2022–2025** combined.
3. Sweep **`ENTRY_THRESHOLD`**, **Donchian vs ATR** trailing, **V01 vs V02**, **lookback ablation**, **`--max-open-trades`**.
4. Export or log results; require **regime-split tables** before any “GO.”

**Revised Go/No-Go (all must be met to proceed to hyperopt/live planning):**

- At least one (**strategy**, **threshold**, **trailing**, **max_open_trades**) combo has **profit factor > 1.2** after **0.05%/side** fees on a **holdout** or **full-sample** test (document which — avoid pure in-sample p-hacking).
- **Regime split:** not **concentrating** all edge in a single year (Lesson #10); explicitly report **2022 bear / later years**.
- Trade count and hold durations consistent with design intent (daily signals may imply **low** frequency — that is acceptable if economics justify it).
- **STOP or pivot** if no combo clears bars after disciplined search: consider **K-filter (Phase 2)**, **fee tier assumption**, or **park** like G.

> **Note:** Original Phase 0 wording assumed “hourly Donchian channels for all nine windows.” That is **not** implemented on `1h` due to exchange limits; gates apply to the **`1d`-based** ensemble actually in code.

### Phase 1: Freqtrade MVP — status

**Delivered:** `config_donchian.json`, V01/V02 strategy modules, sweep script.

**Remaining:** Economic validation (Phase 0), regime documentation in Deep Dive / Research Log, optional `donchian_regime_breakdown.py` enhancements for exported zips.

### Phase 2: Enhancement + hyperopt + OOS

**Prerequisite:** Phase 0 GO.

**Tasks:** K-filter (Candidate K), hyperopt on promising region, walk-forward. Commands remain `docker compose run --rm freqtrade hyperopt ...` with **`--timeframe`** matching the chosen strategy (`1h` for V01, `1d` for V02).

### Phase 3: Dry-run deployment

(Unchanged.) Separate compose profile/instance; 2+ weeks forward simulation before live consideration.

---

## Part 4: What Not To Repeat

| Anti-pattern | Addressed |
|---|---|
| Building before fee/regime evidence | Phase 0 sweeps + mandatory splits |
| Assuming paper timeframe transfers | `1d` math documented; V01 vs V02 tests execution mismatch |
| Ignoring exchange data limits | `1d` informative path documented in Deep Dive |
| Bull-only validation | Regime columns required in sweep output |

---

## Part 5: File Locations

| File | Purpose | Status |
|------|---------|--------|
| `user_data/strategies/EnsembleDonchianStrategy_V01.py` | V01 hybrid + `_ATR` + threshold + ablation subclasses | **Built** |
| `user_data/strategies/EnsembleDonchianStrategy_V02.py` | V02 pure `1d` + `_V02_ATR` (`startup_candle_count` 0 — rollings warm up inside year; no pre-2022 fetch) | **Built** |
| `config/config_donchian.json` | 14-pair futures whitelist | **Built** |
| `user_data/scripts/donchian_phase0_sweep.py` | Phase 0 grid + result aggregation | **Built** |
| `user_data/results/donchian_phase0_sweep_*.json` | Machine-readable sweep output | Generated by script |
| `user_data/info/EnsembleDonchianTrend_Deep_Dive.md` | Technical deep dive **v1.5** | **PARKED** (reference) |
| `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` | THIS FILE | **PARKED** (reference) |

### Appendix A: Whitelist (2026-04-06)

**14 pairs:** BTC, ETH, SOL, BNB, XRP, DOGE, ADA, AVAX, DOT, LINK, LTC, ATOM, NEAR, FIL (all `USDT` perpetual). Removed late listings without **2022-01-01** common history.

### Appendix B: Lookback periods

**Implemented as calendar days on `1d` bars:** 5, 10, 20, 30, 60, 90, 150, 250, 360.

Historical “hourly equivalent ×24” table is **not** the running implementation for full horizons; see Deep Dive §4.4 *Lookback periods (paper = implementation)*.

---

## Part 6: Reference Material

### 6.1 Key papers

(Unchanged — Zarattini et al.; Beluská & Vojtko; Mesíček & Vojtko.)

### 6.2 Freqtrade implementation

- **Merge informative:** `merge_informative_pair` for V01 (`1h` ← `1d`).
- **Custom trailing:** `custom_stoploss()`; state in `_pair_entry_trail_n`, `_pair_ratched_stop`.
- **`--max-open-trades`:** CLI override for capacity studies.

### 6.3 Relationship to G

J reuses **DataProvider** multi-pair vol loading and **`custom_stake_amount`** pattern. J does **not** reuse G’s ranking/rebalance loop.

---

*Maintained by project contributors.*  
*2026-04-06 — v2 plan: 14-pair universe, `1d`/V01–V02 architecture, Phase 0 reframed, sweep + file table.*  
*2026-04-06 — **PARKED**: Phase 0 NO-GO; plan retained as historical record.*
