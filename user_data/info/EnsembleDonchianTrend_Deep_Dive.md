# Ensemble Donchian Trend-Following (Candidate J) — Deep Dive
## Version 1.5 | Started: 2026-03-31 | Status: **PARKED (2026-04-06)** — Phase 0 **NO-GO**; MVP and docs **retained for reference** only. Do not extend unless reopened as a **new hypothesis** with a fresh Phase 0 charter (see `AlgoTrading_Research_Log.md`).

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session** for this project.
> Pair with `AlgoTrading_Research_Log.md` for registry, roles, and lessons.
> Original phase checklist and go/no-go gates: `EnsembleDonchianTrend_Dev_Plan.md`.

### Current Status (high level)

| Item | State |
|------|--------|
| **Phase 0** | **CLOSED — NO-GO (2026-04-06)** — Fee-inclusive backtests and `donchian_phase0_sweep.py` grid failed Dev Plan economics / robustness gates. Representative artifact: `user_data/results/donchian_phase0_sweep_20260406_105346.md`. |
| **Phase 1** | **MVP frozen** — `EnsembleDonchianStrategy_V01.py` / `V02` / variants, `config_donchian.json` (14 pairs). **No further product work** unless Research Log **reopens** J. |
| **Phase 2–3** | **Cancelled** for this candidate (no Phase 0 GO). |

### Primary Risk

The source paper uses **daily** bars for the Donchian ensemble. The MVP computes the **nine daily lookbacks on 1d OHLCV** and merges them onto the **1h** dataframe for entries, sizing, and stops (signal updates daily, ffill on 1h; fills on 1h). **Phase 0 (closed 2026-04-06)** ran fee-inclusive sweeps across thresholds, trailing methods, **V01 vs V02**, lookback ablation, and `max_open_trades` — **no operating point** cleared project gates. A **pure 8640×1h** Donchian on all nine windows is **not supported** on stock Freqtrade + Binance because of the **startup candle / API chunk limit** (~2494 one-hour bars); **`1d` informative** was the supported implementation path for full paper horizons.

### Key Commands (PowerShell-friendly, single lines)

```text
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_donchian.json --timerange 20220101-20260401 --timeframes 1h 1d --trading-mode futures
```

```text
docker compose run --rm --entrypoint python freqtrade user_data/scripts/donchian_phase0_sweep.py
```

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V01 --timerange 20220101-20260101 --timeframe 1h --fee 0.0005 --export trades
```

Phase 0 parameter grid (writes `user_data/results/donchian_phase0_sweep_<timestamp>.json` + `.md`; use `--entrypoint python` so runs call `freqtrade` directly):

```text
docker compose run --rm --entrypoint python freqtrade user_data/scripts/donchian_phase0_sweep.py
```

### File Locations

| File | Status | Purpose |
|------|--------|---------|
| `user_data/info/EnsembleDonchianTrend_Deep_Dive.md` | **THIS FILE** | Technical + layman reference; candidate **PARKED** — read §Quick-Start status first |
| `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` | **PARKED** (reference) | Phase gates, go/no-go criteria, anti-pattern table |
| `user_data/strategies/EnsembleDonchianStrategy_V01.py` | **Built** | V01 + `_ATR` + entry-threshold + lookback-ablation subclasses |
| `user_data/strategies/EnsembleDonchianStrategy_V02.py` | **Built** | Pure `1d` execution (same lookbacks; `startup_candle_count` 0 for short on-disk spans) |
| `config/config_donchian.json` | **Built** | **14-pair** futures whitelist (pairs with Binance USDT-M history from **2022-01-01**; late-listed alts removed so 1d lookbacks align across the universe), `max_open_trades` 5, API 8085 |
| `user_data/scripts/donchian_phase0_sweep.py` | **Built** | Docker-aware grid of backtests → `user_data/results/donchian_phase0_sweep_*.json`/`.md` |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Registry; **J PARKED** §4.3–4.4; 7/7 filter note ≠ Phase 0 GO; sweep log |

**Reusable from Candidate G:**

| File | Reuse How |
|------|-----------|
| `user_data/strategies/XSMomentumStrategy_V01.py` | Reference for `DataProvider` cross-pair pattern, `custom_info` storage, `custom_stake_amount()` vol-scaling |
| `config/config_xsmom.json` | Reference for StaticPairList structure, fee settings, leverage config (J uses a **smaller** whitelist than G) |
| `user_data/scripts/xsmom_phase0_exploration.py` | Reference for Phase 0 sweep script structure |

---

## Part 1: Why This Project Exists (Layman + Context)

### 1.1 One-sentence idea

**Buy any crypto that is hitting new highs across multiple time horizons at once, and ride the trend until it breaks** — using a basket of ~14 liquid futures pairs (whitelist in `config_donchian.json`) so exposure is diversified.

That's **ensemble trend-following**: the word "ensemble" means we're not asking "is this coin at a 20-day high?" — we're asking "is this coin at a 5-day high *and* a 20-day high *and* a 90-day high *and* a 250-day high... all at the same time?" The more time horizons agree, the more confident we are that a real trend is underway, not just noise.

### 1.2 What are Donchian channels?

Think of a **price corridor**. For any given lookback period (say, 20 days):

- The **upper band** is the highest price the asset reached in the last 20 days.
- The **lower band** is the lowest price the asset reached in the last 20 days.
- The **middle** is just the average of those two.

When price **breaks above** the upper band, it means the asset just made a new high for that period — in other words, it's doing something it hasn't done recently. That's a **breakout**. In trend-following, a breakout is a buy signal because it often marks the start (or continuation) of a sustained move.

Richard Donchian invented this in the 1950s. The famous "Turtle Traders" experiment in the 1980s used Donchian channels to train novice traders who went on to make hundreds of millions of dollars. The core insight has been validated across stocks, bonds, commodities, and currencies for over 40 years.

### 1.3 What makes this an "ensemble"?

Instead of picking one lookback period (which is always a bit arbitrary — why 20 days instead of 30?), we compute Donchian channels at **9 different lookback periods** simultaneously and average the signals. Each lookback votes "breakout" (1) or "not breakout" (0), and we average the votes into a score from 0.0 to 1.0.

- **Score = 0.0:** No lookback sees a breakout. The asset is probably in a range or downtrend.
- **Score = 0.5:** About half the lookbacks see a breakout. A trend may be forming but isn't confirmed across all horizons.
- **Score = 1.0:** All 9 lookbacks agree — the asset is at new highs across every time horizon from 5 days to a year. This is a strong, confirmed trend.

The ensemble approach is more robust to regime changes than any single lookback because short lookbacks adapt quickly to new trends while long lookbacks prevent overreacting to noise. This **smoothing effect across multiple time horizons** is exactly what we believe killed Candidate G (cross-sectional momentum used a single lookback and was regime-unstable).

### 1.4 Why the research program cares

Five earlier candidates failed or were parked for specific reasons:

- **RAME:** Tried to predict market regimes — the per-trade edge was too small to survive fees.
- **LOB Microstructure:** The signal was real but operated at a timescale (3 seconds) where fee costs were 6× larger than the available profit.
- **CointPairs:** Mean-reversion signal was real, but only generated 0.05 trades per day — far too infrequent. Also, trading only one leg exposed us to directional risk.
- **Candidate E (Path Signatures):** The lead-lag signal was too noisy to overcome stop-loss costs on unhedged alt positions.
- **Candidate G (Cross-Sectional Momentum):** Return-based ranking scored 7/7 on our evaluation filter, but empirical testing showed the edge was **regime-unstable** — it performed well in some years and catastrophically in others (−40% in 2024).

Candidate J was scored **7/7** on our evaluation filter — the second clean pass in project history. It addresses G's regime instability through ensemble smoothing, uses standard OHLCV data with no sidecar, and the source paper demonstrates Sharpe > 1.5 on survivorship-bias-free data. See `AlgoTrading_Research_Log.md` Candidate J section for full evaluation and paper references.

### 1.5 How this complements LiqCascade and (parked) G

| | LiqCascade | G (parked) | **J (this project)** |
|---|-----------|-----------|----------------------|
| **Signal** | A specific **event** (liquidation cascade) | Continuous **return ranking** across a universe | Continuous **breakout detection** per asset |
| **Signal type** | Event-driven | Relative (who's winning the race?) | Absolute (is this asset trending?) |
| **Data** | WebSocket sidecar + OHLCV | OHLCV only | OHLCV only |
| **Direction** | Long or short (with trend) | Long + short (or long-only variant) | **Long-only** |
| **Exit** | ATR stop / time stop / ROI target | Time-based rebalance | **Trailing stop at Donchian lower band** |
| **Weakness** | False positives (59% time-stop rate) | Regime instability (−40% in 2024) | **Unknown — to be tested** |

J and LiqCascade are designed to **diversify how the book makes money**, not replace each other. LiqCascade fires during volatility spikes; trend-following captures sustained directional moves. J also differs structurally from G: breakout detection is per-asset (absolute), not cross-sectional (relative), and exits are signal-driven, not calendar-driven.

---

## Part 2: Plain English — How the Bot Will Think

Imagine watching **14 runners** (our current futures whitelist) on a track. **Once per day** (when the daily candle closes), for each runner:

1. Draw **9 "highest point" lines** — one for the last 5 days, one for the last 10 days, one for the last 20 days, and so on up to the last **360 calendar days**. Each line uses **daily** highs and lows (same as the paper). Between daily updates, the bot **reuses the last completed day’s** ensemble values on each **hour** (no intraday change to the Donchian votes).
2. Check: **is the runner’s daily close above each line?** If yes, that's a "breakout vote" for that horizon. If no, no vote.
3. **Count the votes.** If a runner is above 7 out of 9 lines (score = 0.78), they're in a strong trend across almost all time horizons. If they're above 2 out of 9 (score = 0.22), they might have a short-term bounce but aren't in a real trend.
4. **Bet on runners scoring above the threshold** (e.g., > 0.5 — majority of horizons confirm trend). The higher the threshold, the more selective we are (fewer trades, higher confidence per trade).
5. **Size each bet** based on how volatile each runner has been recently — bet less on the wild ones, more on the steady ones. (In technical terms: inverse-volatility position sizing.)
6. **Keep holding** as long as the trend persists. Exit when the runner drops below their **lower** Donchian band (their recent low point), which means the trend has broken. This is a **trailing stop** — it moves up as the trend strengthens but never moves down.
7. **No short selling.** We only bet on uptrends. If nothing is trending, we hold cash and wait. (The literature is clear: shorting momentum losers in crypto is where losses concentrate — see Han et al., Lesson #12.)

**Important:** The bot does **not** predict the future. It identifies assets that are *currently* in confirmed uptrends across multiple time horizons and rides along until the trend breaks. Whether this produces profit depends on whether trends in crypto persist longer than the fees it costs to enter and exit — which is what backtesting will determine.

---

## Part 3: Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│           ENSEMBLE DONCHIAN TREND-FOLLOWING (Candidate J)             │
├──────────────────────────────────────────────────────────────────────┤
│  Inputs: Binance USDT-M futures OHLCV — **1d** (Donchian) + **1h**   │
│          (volatility, ATR, order timing)                              │
│  Universe: **14** liquid pairs (StaticPairList in config_donchian)   │
│                                                                      │
│  For each pair (populate_indicators):                                 │
│    • Load **1d** series; compute Donchian upper/lower at **9 paper**  │
│      lookbacks: **5,10,20,30,60,90,150,250,360** calendar days       │
│    • merge_informative_pair(1h, 1d) — **no lookahead** (daily bar   │
│      aligned per Freqtrade rules)                                     │
│    • Binary breakout per lookback: daily close > prior daily upper    │
│    • Ensemble score = mean of 9 signals (0.0–1.0), ffill on 1h rows │
│    • Trailing stop = **daily** Donchian lower for shortest active N  │
│    • Vol for sizing = **1h** rolling std of returns (168-bar window) │
│    • ATR(14) on **1h** if using ATR trailing variant                 │
│                                                                      │
│  Entries: enter_long when ensemble_score > threshold (default 0.5)   │
│  Exits: custom_stoploss (Donchian lower or ATR) + hard stop + time   │
│                                                                      │
│  Position sizing: custom_stake_amount with inverse-vol scaling       │
│  Direction: LONG ONLY.                                                │
│                                                                      │
│  No sidecar. No FreqAI. No ML. Pure price channels.                   │
│  Reuses G’s DataProvider cross-pair pattern for vol scaling.          │
└──────────────────────────────────────────────────────────────────────┘
```

**Caching consideration:** Unlike G which needed cross-sectional ranking (all pairs compared each candle), J computes Donchian signals **per pair** on **1d** data. Cross-pair loading is only for **inverse-vol** denominators (median vol across the whitelist).

**Why not nine channels on raw 1h bars out to 360 days?** On Binance, Freqtrade caps how many **1h** candles can be loaded at strategy startup (~**2494** bars from the exchange chunk rule). That caps the longest **hourly** Donchian at roughly **~100 days**, not 360. Implementing the paper’s **360-day** horizon therefore uses **`1d` informative candles** for Donchian math; **`startup_candle_count` on the strategy stays modest (~400)** because it only warms up **1h** indicators (vol, ATR), not 8640 hourly Donchian bars.

**Whitelist note:** Pairs listed on Binance **after** 2022-01-01 were removed so every symbol has the same **1d** history anchor; otherwise the “universe” would be limited by the **newest** listing date.

---

## Part 4: The Donchian Channel — Technical Detail

### 4.1 Mathematical definition

For a given lookback period `N` and a price series with high (`H`) and low (`L`) values:

- **Upper band:** `DC_upper(t, N) = max(H[t-N+1], H[t-N+2], ..., H[t])` — the highest high over the last N periods.
- **Lower band:** `DC_lower(t, N) = min(L[t-N+1], L[t-N+2], ..., L[t])` — the lowest low over the last N periods.
- **Middle band:** `DC_mid(t, N) = (DC_upper + DC_lower) / 2` — not used in our strategy.

In plain English: the upper band is just the ceiling of recent prices, and the lower band is the floor. When price punches through the ceiling, it's doing something it hasn't done in a while — that's the breakout signal.

### 4.2 Breakout signal (per lookback)

```
signal_i(t) = 1   if close(t) > DC_upper(t-1, N_i)
              0   otherwise
```

We compare the current close to the *previous candle's* upper band to avoid look-ahead bias (i.e., we don't use today's candle to compute today's channel — the channel is always "as of last candle").

### 4.3 Ensemble score

```
ensemble_score(t) = (1/K) × Σ signal_i(t)    for i = 1 to K
```

where `K` is the number of lookback periods (**9** in the paper and in **V01**). The result is a value between 0.0 and 1.0.

### 4.4 Lookback periods (paper = implementation)

The Zarattini paper uses **daily** bars with **calendar-day** lookbacks. **V01 implements these directly on the `1d` timeframe** (not ×24 hourly bars):

| Lookback (days) | Role | Notes |
|---|---|---|
| 5, 10 | Short horizon | Fastest to flip; more noise |
| 20, 30 | Medium | Classic Turtle-ish windows |
| 60, 90 | Medium-long | Quarter-scale context |
| 150, 250, 360 | Long | Slow trend confirmation; 360d ≈ one year |

**Merged to 1h:** After computing signals on `1d`, Freqtrade’s `merge_informative_pair` attaches them to each **1h** row (forward-filled until the next daily close). Entries and `custom_stoploss` therefore run on **1h** timestamps, but the **Donchian math updates daily**—matching the paper’s bar size, not “9 channels on 1h out to 8640 bars.”

**Phase 0 / research:** Whether to **drop** long windows (e.g. 250d–360d) for simplicity or robustness is now an **empirical** question (ablation on this codebase), not a Freqtrade startup workaround.

### 4.5 Why the ensemble is more robust than a single lookback

This is the **core insight** of the Zarattini paper and the reason J is expected to handle regime changes better than G.

A single lookback period creates a fragile dependency: if you use a 20-day Donchian channel and the market shifts from a slow grind to a fast impulse, the 20-day window may be too slow to catch the new trend. Conversely, if you use a 5-day channel, you'll catch fast moves but also get whipsawed by noise in slow trends.

The ensemble eliminates this fragility by letting the *data* decide which lookback is relevant. In a fast-moving market, the short lookbacks fire first and pull the ensemble score up. In a slow trend, the long lookbacks provide the persistent signal while short lookbacks may flip back and forth. The ensemble score naturally adapts to the character of the current trend without any explicit regime detection or parameter switching.

This is why G failed and J may succeed: G used a single formation period (4h or 1d) to rank assets. If that formation period happened to be wrong for the current regime, the entire signal broke down. J hedges across 9 formation-equivalent windows simultaneously.

---

## Part 5: Exit Mechanism — Trailing Stop at Donchian Lower Band

### 5.1 Plain English

Once we're in a trade, we draw a "floor" under the price — the **daily** Donchian lower band for the **shortest lookback (in days) that was active at entry**. That floor is updated when each **daily** candle completes (and is forward-filled on 1h bars). In implementation the stop **ratchets**: the effective stop price only moves **up**, never down (`custom_stoploss` in V01).

If the price falls and touches this rising floor, we exit. The trend is over.

This is called a **trailing stop** because it "trails" behind the price as it rises. It locks in profit during a strong trend and cuts losses quickly when the trend reverses.

### 5.2 Technical detail

Two trailing stop approaches to test in Phase 0:

**Approach A — Donchian lower band trailing:**
```
trailing_stop_level(t) = DC_lower(t, N_shortest_active)
```
where `N_shortest_active` is the shortest lookback (here **in days**) whose breakout signal was active at entry. This gives the tightest trailing stop — exits when price violates that **daily** lower band (evaluated on 1h bars via merged columns).

Exit when price hits the stop implied by `DC_lower` (Freqtrade: `custom_stoploss` returns relative stop distance).

**Approach B — ATR-based trailing:**
```
trailing_stop_level(t) = highest_close_since_entry - (ATR_multiplier × ATR(t, 14))
```
This trails at a fixed distance (in volatility terms) below the peak price since entry. More conventional, not tied to the Donchian framework.

In Freqtrade, V01 implements both via `custom_stoploss()` by reading the latest analyzed **1h** row (`get_analyzed_dataframe`): Donchian variant uses column `dc_lower_{N}` (daily-based, merged); ATR variant uses **1h** `atr` and peak price since open. Per-pair state (`_pair_entry_trail_n`, `_pair_ratched_stop`) stores the entry lookback and ratcheted stop. Return value is a **negative fraction** of current price (stop below market), floored at the hard `stoploss`.

### 5.3 Time stop (backup)

A maximum holding period (e.g., 168h = 7 days, or 720h = 30 days) as a safety net. If a position hasn't been stopped out by the trailing stop within this window, close it anyway. This prevents capital from being trapped in a slowly decaying position that hasn't technically broken the lower band but isn't making progress.

The time stop should **rarely fire** — if it fires on > 30% of trades, the trailing stop calibration needs tightening or the entry threshold needs raising (per Lesson #11 — time-stop rate as a diagnostic).

---

## Part 6: Position Sizing — Inverse-Volatility Scaling

### 6.1 Plain English

Not all coins are equally volatile. SOL might swing 5% in a day while BTC swings 2%. If we bet the same dollar amount on both, our actual risk on SOL is 2.5× higher than on BTC.

Inverse-volatility sizing fixes this: we bet **less** on the wild coins and **more** on the steady ones, so that each position contributes roughly the **same amount of risk** to the portfolio. This prevents one volatile coin from dominating the portfolio's results.

### 6.2 Technical detail

```
vol_asset(t) = std(returns_asset, window=168)  # 7-day rolling volatility of hourly returns
target_vol = median(vol across all universe assets)  # or a fixed target like 0.02
stake_multiplier = target_vol / vol_asset(t)
stake_multiplier = clip(stake_multiplier, 0.5, 2.0)  # floor and cap to prevent extremes
final_stake = base_stake × stake_multiplier
```

Implemented via `custom_stake_amount()` in Freqtrade — the same pattern already used in G's V01.

### 6.3 Why this matters for trend-following specifically

Trend-following strategies are vulnerable to **momentum crashes** — sudden, violent reversals that wipe out gains from weeks of steady trending. These crashes typically happen in the most volatile assets. By sizing positions inversely to volatility, we automatically underweight the assets most prone to crashes, which acts as a built-in crash protection mechanism. Zarattini et al. use this approach in their paper and credit it as a key contributor to the strategy's risk-adjusted performance.

---

## Part 7: Relationship to Candidate G's Codebase

J is designed for **maximum infrastructure reuse** from the parked Candidate G. Here's what carries over and what changes:

### 7.1 What we reuse

| Component | G's Implementation | J's Adaptation |
|---|---|---|
| `DataProvider` cross-pair loading | Loads whitelist pairs, computes returns, ranks | Same idea: load pairs for **median vol**; Donchian signal is **per pair** on `1d` |
| `custom_info` storage | Stores cross-sectional ranks per pair per candle | J uses **instance dicts** for trail lookback + ratcheted stop (not `custom_info`) |
| `custom_stake_amount()` | Inverse-vol scaling with floor at 50% | Same pattern — **1h** returns for vol |
| `config_xsmom.json` structure | Large StaticPairList, futures mode, fee settings | `config_donchian.json`: **14** pairs, same modes/fees philosophy |
| Phase 0 sweep script pattern | `xsmom_phase0_exploration.py` | Adapt for Donchian signal sweep instead of return-ranking sweep |

### 7.2 What changes

| Aspect | G (Cross-Sectional Momentum) | J (Ensemble Donchian) |
|---|---|---|
| **Signal source** | Return ranking (relative: who gained most?) | Breakout detection (absolute: is price above channel?) |
| **Signal computation** | Cross-sectional (all pairs compared) | Per-pair independent (each pair has its own score) |
| **Entry trigger** | Pair is in top N by return rank | Pair's ensemble score exceeds threshold |
| **Exit trigger** | Periodic rebalance (time-based) + fixed stoploss | Trailing stop at Donchian lower band (signal-based) |
| **Direction** | Long + short (V01) or long-only (V02) | **Long-only always** |
| **Regime sensitivity** | High — single formation period brittle to regime changes | **Low (expected)** — ensemble smooths across 9 horizons |

### 7.3 Why we don't just "tweak" G

It would be tempting to add Donchian signals as another indicator in G's framework. But the strategies are architecturally different:

- G **rebalances on a schedule** (every N hours, sell old positions, buy new ones). J **holds until the trend breaks** (exit is signal-driven, not calendar-driven). These are incompatible exit mechanics.
- G requires **cross-sectional comparison** (you can't rank one pair in isolation). J is **per-pair independent** (each pair's ensemble score depends only on its own history). This simplifies the code and reduces coupling.
- G's "ranking" and J's "breakout" are answering different questions. Ranking asks "which horse is ahead?" — breakout asks "is this horse running at all?"

A clean implementation from scratch (reusing infrastructure components but not the signal logic) is the right approach. Attempting to merge them would create a hybrid that's harder to debug, harder to attribute performance to either signal, and harder to maintain.

---

## Part 8: Phase History (What's Done vs Next)

| Phase | Goal (layman) | Status |
|-------|----------------|--------|
| **0** | Fee-inclusive economics + regime robustness | **NO-GO (2026-04-06)** — see `user_data/results/donchian_phase0_sweep_20260406_105346.md`. |
| **1** | MVP fidelity | **Frozen** — sufficient to conclude Phase 0; no hyperopt warranted. |
| **2–3** | K-filter / live | **Cancelled** while candidate is PARKED. |

Exact numeric gates for each phase are in `EnsembleDonchianTrend_Dev_Plan.md`.

---

## Part 9: Strategy Variants (Planned)

**Module:** `user_data/strategies/EnsembleDonchianStrategy_V01.py` (+ `EnsembleDonchianStrategy_V01_ATR`).

### V01 — MVP (Phase 1)

| Parameter | Default | Range to Test |
|---|---|---|
| `DONCHIAN_TIMEFRAME` | `'1d'` | Fixed — required for full 360d lookback under Binance startup rules |
| `LOOKBACK_DAYS` | `(5, 10, 20, 30, 60, 90, 150, 250, 360)` | Ablation: drop long tails (e.g. 250–360) vs full paper set |
| `timeframe` (base) | `1h` | Alternative research: `1d`-only strategy (different execution model) |
| `startup_candle_count` | `400` | Warm-up for **1h** vol/ATR only; raise only if vol window grows |
| `ENTRY_THRESHOLD` | 0.5 | 0.3, 0.5, 0.7, 0.9 (Phase 0 sweep) |
| `TRAILING_STOP_METHOD` | `'donchian_lower'` | `'donchian_lower'` vs `'atr'` (`_V01_ATR` class) |
| `TRAILING_STOP_LOOKBACK` | shortest active at entry | shortest vs median active lookback (future variant) |
| `ATR_MULTIPLIER` (if ATR method) | 3.0 | 2.0, 3.0, 4.0 |
| `VOL_SCALING_WINDOW` | 168 (7d of 1h) | Fixed for V01 |
| `VOL_SCALING_FLOOR` / `CAP` | 0.5 / 2.0 | Fixed for V01 |
| `MAX_OPEN_TRADES` | 5 | 5–10 vs **14** pairs — capacity study |
| `LEVERAGE` | 2 (capped in strategy) | Fixed for V01 |
| `TIME_STOP_HOURS` | 720 (30d) | Safety net; diagnostic if rate high |
| `stoploss` | -0.12 | Hard catastrophic cap |
| Whitelist | **14** pairs | See `config_donchian.json`; expand only if **common 1d** history exists |

**Backtest fee:** `--fee 0.0005` (5 bps per side; ~10 bps round trip).

### V02 — K-Filter Enhancement (Phase 2, if V01 validates)

Same as V01 plus a **multi-timeframe trend confirmation filter** (from Candidate K):
- Require a higher-timeframe indicator (e.g., daily MACD or 4h EMA200 direction) to confirm the trend direction before entry
- This addresses Lesson #4 (short-term indicators lie in macro trends) — prevents entering Donchian breakouts that are counter to the larger trend
- If V01 shows excessive entries during counter-trend periods (identifiable via regime-split analysis), V02 adds this filter
- Implementation note: V01 **already** uses `informative_pairs()` for **`1d` Donchian**. V02 adds a **second** daily (or 4h) **macro** filter column and ANDs it with `ensemble_score` in `populate_entry_trend()`.

---

## Part 10: Key Technical Decisions to Resolve in Phase 0

MVP code **exists**; **Phase 0 is closed (NO-GO 2026-04-06)** — this section is **archived design intent**; reopen only with a new hypothesis charter.

### 10.1 How many daily lookbacks?

The paper uses **9** lookbacks (5d–360d); V01 implements all nine on **`1d`**. **Phase 0** included **lookback ablation** (`_LookbackAblated`); it did **not** produce a gate-clearing operating point.

### 10.2 Donchian trailing stop vs ATR trailing stop?

Donchian lower band trailing is more theoretically coherent (the exit is from the same framework as the entry). ATR trailing is more conventional and may be easier to calibrate. **Phase 0** compared both on the same fee-inclusive sample; **neither** combination cleared project gates — see `user_data/results/donchian_phase0_sweep_*.md`.

### 10.3 Execution timeframe vs signal timeframe

The **signal** is **daily** (paper-aligned). **Orders** still fill on **1h** candles in V01. **Phase 0** compared **hybrid 1d-signal / 1h-exec** (V01) vs **pure `1d`** (V02); economics remained **below gates** on the grid tested. True “all Donchian channels on 1h out to one year” remains **infeasible** on stock Freqtrade + Binance without custom data loading.

### 10.4 Entry threshold calibration

Higher threshold (e.g., 0.9 — only enter when 8+ of 9 lookbacks agree) produces fewer, higher-confidence entries. Lower threshold (e.g., 0.3) produces more entries but with lower per-trade confidence. **Phase 0** swept thresholds **0.3–0.9**; **no** point on that frontier cleared gates **fee-inclusive** on the 2022–2026 sample exercised in the sweep.

---

## Part 11: Lessons From Prior Projects (Applied Here)

| Lesson | What It Means | Application in J |
|--------|---------------|------------------|
| **#2:** Entry quality > exit optimization (RAME) | If the base signal has no edge, no exit tuning will fix it. | **Phase 0 outcome:** entry / regime economics **did not** clear gates — candidate **PARKED**; no further exit hyperopt until a **new entry hypothesis** is chartered. |
| **#3:** Structural alpha > statistical alpha (RAME→LiqCascade) | Prefer signals with a clear *why*. | Trend-following has 40+ years of *why*: serial correlation, behavioral momentum, reflexive feedback loops. Structural, not statistical. |
| **#4:** Short-term indicators lie in macro trends (RAME) | Any short-term signal needs a macro filter. | V02 adds Candidate K's multi-timeframe macro filter. V01 relies on the ensemble's long lookbacks as implicit macro context. |
| **#7:** Fee economics before infrastructure (LOB) | Validate fee-inclusive profitability before scaling effort. | Phase 0: fee-inclusive sweeps and regime splits **before** hyperopt / live. |
| **#8:** Paper results don't transfer to our fee tier (LOB) | Always compute P&L at our actual fees. | All backtests use `--fee 0.0005` (our Binance retail tier). |
| **#9:** Half-life must match trading frequency (CointPairs) | Don't build a strategy whose natural timescale doesn't match your trading frequency. | Donchian votes are **daily**; execution is **1h** — **Phase 0 tested** hybrid vs pure **`1d`**; result **NO-GO** on project gates (reopen only under a new hypothesis). |
| **#10:** Bull-market bias (CointPairs) | Don't validate only on bull periods. | Regime splits (2022 bear, 2023 range, 2024–2025 bull) mandatory at every gate. |
| **#11:** Time-stop rate as diagnostic (LiqCascade) | If > 50% of trades exit via time stop, the entry signal is too loose. | Time stop is a backup safety net; **if reopened**, use time-stop share as a diagnostic alongside the Phase 0 sweep style grids. |
| **#12:** Unhedged directional alt exposure is dangerous (Candidate E) | Don't bet big on single alts without risk controls. | Long-only across **14** pairs with inverse-vol sizing diversifies single-asset concentration. |
| **G's parking lesson:** Single formation period is regime-fragile | One lookback = one point of failure. | Ensemble over 9 lookbacks hedges regime sensitivity. This is J's raison d'être. |

---

## Part 12: Risk Factors and What Could Go Wrong

### 12.1 Hybrid daily signal + hourly execution (PRIMARY RISK)

V01 updates Donchian votes **once per day** while reacting to stops/fills **every hour**. That can **help** (finer exits) or **hurt** (more fee churn vs a pure daily system). **Phase 0** ran regime-split + threshold + trailing + `max_open_trades` grids; economics stayed **below gates**. If the candidate is **reopened**, separate **hypotheses** (new universe, different fee/stake model, macro filter / Candidate K overlay) need explicit charters — not more of the same grid without a theory change.

**Historical mitigation explored:** Regime splits; threshold sweep; `EnsembleDonchianStrategy_V01_ATR`; **`timeframe = 1d`** (V02); lookback ablation.

### 12.2 Momentum crash

A sudden, violent reversal wipes out weeks of gains in a day. This is the canonical risk of all trend-following strategies. Grobys (2025) documents severe momentum crashes in crypto specifically.

**Mitigation:** Inverse-vol position sizing (underweights the most crash-prone assets), Donchian trailing stop (exits when trend breaks), **14-pair** diversification (single crash doesn't dominate), 2x leverage cap (limits tail risk).

### 12.3 Donchian is too well-known

Donchian channels have been used since the 1950s. If too many participants use the same breakout signals, the edge may be arbitraged away — breakouts get front-run, false breakouts get more common.

**Mitigation:** The edge in Zarattini's paper persists through 2025 net-of-fees (Sharpe > 1.5), suggesting the edge is not fully arbitraged yet, at least in crypto. The ensemble (9 lookbacks, not just one) also differentiates from simple Donchian users. And crypto markets remain retail-dominated with less systematic capital than equities. But monitor for alpha decay in forward testing.

### 12.4 Crowded exits

If many trend-followers use similar trailing stops, a trend break could trigger cascading exits — worsening the reversal and increasing slippage. This is less of a concern at our scale (small retail) but worth noting.

**Mitigation:** Inverse-vol sizing naturally sizes down the most volatile (and most crowded) assets.

---

## Part 13: Version History (This Document)

| Date | Change |
|------|--------|
| 2026-03-31 | v1.0 — Initial Deep Dive: full layman + technical coverage. Architecture, Donchian channel explanation, ensemble mechanics, exit mechanism, position sizing, G relationship analysis, phase history, technical decisions for Phase 0, risk factors. Pre-development — no implementation yet. |
| 2026-04-06 | v1.1 — Phase 1 MVP: `EnsembleDonchianStrategy_V01` / `_V01_ATR`, `config_donchian.json`. Doc file table + status updated. |
| 2026-04-06 | v1.2 — **Full paper lookbacks on `1d`** merged to **`1h`**; **14-pair** whitelist (common history from 2022-01-01); Binance **startup / 8640×1h** limitation documented; Phase 0/8/9/10/12 refreshed; V02 informative note clarified. |
| 2026-04-06 | v1.3 — **`donchian_phase0_sweep.py`**, **`EnsembleDonchianStrategy_V02`** (pure `1d`), threshold + lookback-ablation subclasses on V01; Dev Plan aligned. Sweep artifacts under `user_data/results/donchian_phase0_sweep_*.md`. |
| 2026-04-06 | v1.4 — **PARKED**: Phase 0 NO-GO; Quick-Start + file table + footer aligned; no forward phases. |
| 2026-04-06 | v1.5 — Archival pass: Part 10–12 and Lessons table use **closed Phase 0** language; Research Log row in file table clarifies **7/7 ≠ GO**; pointers to sweep artifacts. |

---

*Technical reference for **PARKED** Candidate J. Registry and priority: `AlgoTrading_Research_Log.md`. Historical gates: `EnsembleDonchianTrend_Dev_Plan.md`.*
