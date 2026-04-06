# Ensemble Donchian Trend-Following (Candidate J) — Deep Dive
## Version 1.0 | Started: 2026-03-31 | Status: **PRE-DEVELOPMENT** — Phase 0 not yet started.

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every Cursor session** for this project.
> Pair with `AlgoTrading_Research_Log.md` for registry, roles, and lessons.
> Original phase checklist and go/no-go gates: `EnsembleDonchianTrend_Dev_Plan.md`.

### Current Status (high level)

| Item | State |
|------|--------|
| **Phase 0** | **Not started** — data download + hourly timeframe validation + fee-inclusive parameter sweep |
| **Phase 1** | Pending Phase 0 GO — Freqtrade MVP implementation |
| **Phase 2** | Pending Phase 1 GO — Enhancement (K-filter), hyperopt, OOS validation |
| **Phase 3** | Pending Phase 2 GO — Dry-run deployment |

### Primary Risk

The source paper (Zarattini et al., SSRN 2025) uses **daily** data. Our frequency objective requires **hourly**. Phase 0 must explicitly validate that the ensemble signal retains predictive power at 1h resolution before any Freqtrade code is written. If 1h fails, test 4h as a fallback. If both fail, STOP.

### Key Commands (PowerShell-friendly, single lines)

```text
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_donchian.json --timerange 20220101-20260401 --timeframes 1h
```

```text
docker compose run --rm --entrypoint python freqtrade user_data/scripts/donchian_phase0_sweep.py
```

```text
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_donchian.json --strategy EnsembleDonchianStrategy_V01 --timerange 20220101-20260101 --timeframe 1h --fee 0.0005 --export trades
```

### File Locations

| File | Status | Purpose |
|------|--------|---------|
| `user_data/info/EnsembleDonchianTrend_Deep_Dive.md` | **THIS FILE** | Authoritative technical + layman reference for Candidate J |
| `user_data/info/EnsembleDonchianTrend_Dev_Plan.md` | Active | Phase gates, go/no-go criteria, anti-pattern table |
| `user_data/strategies/EnsembleDonchianStrategy_V01.py` | To build (Phase 1) | Long-only ensemble Donchian MVP |
| `config/config_donchian.json` | To build (Phase 0) | 20-pair futures whitelist, fees, leverage |
| `user_data/scripts/donchian_phase0_sweep.py` | To build (Phase 0) | Signal validation + fee-inclusive parameter sweep |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Candidate J evaluation (7/7), priority ranking, sweep log |

**Reusable from Candidate G:**

| File | Reuse How |
|------|-----------|
| `user_data/strategies/XSMomentumStrategy_V01.py` | Reference for `DataProvider` cross-pair pattern, `custom_info` storage, `custom_stake_amount()` vol-scaling |
| `config/config_xsmom.json` | Reference for 22-pair StaticPairList structure, fee settings, leverage config |
| `user_data/scripts/xsmom_phase0_exploration.py` | Reference for Phase 0 sweep script structure |

---

## Part 1: Why This Project Exists (Layman + Context)

### 1.1 One-sentence idea

**Buy any crypto that is hitting new highs across multiple time horizons at once, and ride the trend until it breaks — using a basket of ~20 coins so there's always something trending somewhere.**

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

Imagine watching **20 runners** on a track. Every hour:

1. For each runner, draw **9 "highest point" lines** — one for the last 5 days, one for the last 10 days, one for the last 20 days, and so on up to the last 360 days. Each line represents the highest point that runner reached during that lookback window.
2. Check: **is the runner currently above each line?** If yes, that's a "breakout vote" for that time horizon. If no, no vote.
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
│  Inputs: Binance USDT-M futures OHLCV, 1h candles                    │
│  Universe: ~20 liquid pairs (StaticPairList in config_donchian)      │
│                                                                      │
│  For each pair's dataframe (Freqtrade calls populate_indicators):    │
│    • Compute Donchian upper/lower at 9 lookback periods              │
│    • Binary breakout signal per lookback: close > upper ? 1 : 0      │
│    • Ensemble score = mean of 9 binary signals (0.0 to 1.0)         │
│    • Trailing stop level = Donchian lower band (shortest active)     │
│    • Asset volatility = rolling std for position sizing              │
│                                                                      │
│  Entries: enter_long when ensemble_score > threshold                 │
│           (threshold is a hyperparameter, default 0.5)               │
│  Exits: custom_stoploss trailing at Donchian lower band              │
│         OR ATR-based trailing stop (test both in Phase 0)            │
│         Time stop as backup safety net                               │
│                                                                      │
│  Position sizing: custom_stake_amount with inverse-vol scaling       │
│  Direction: LONG ONLY. No short entries.                             │
│                                                                      │
│  No sidecar. No FreqAI. No ML. Pure price channels.                 │
│  Reuses G's DataProvider cross-pair pattern + vol-scaling logic.     │
└──────────────────────────────────────────────────────────────────────┘
```

**Caching consideration:** Unlike G which needed cross-sectional ranking (all pairs compared each candle), J computes signals per-pair independently. No cross-pair comparison is needed for the core signal — each pair's ensemble score depends only on its own price history. The `DataProvider` pattern from G is still useful for loading universe data and computing cross-sectional volatility for position sizing, but the signal logic itself is simpler.

**Startup candles:** The longest Donchian lookback is 8640 hours (360 days). For a 1h backtest, this means the first 8640 candles cannot compute the full ensemble. Options: (a) set `startup_candle_count = 8640` — wastes almost a year of data, (b) use a partial ensemble (only the lookbacks that have enough data) during the warmup period, (c) **reduce the longest lookback** if Phase 0 shows it adds minimal value at hourly resolution. Option (c) is likely the right answer — Phase 0 should test whether a 5-lookback subset (up to 2160h = 90 days) is sufficient.

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

where `K` is the number of lookback periods (9 in the paper, possibly fewer at hourly resolution). The result is a value between 0.0 and 1.0.

### 4.4 Lookback period mapping (paper daily → our hourly)

The Zarattini paper uses daily bars with these lookback periods:

| Paper (daily bars) | Hourly Equivalent (×24) | Approximate Calendar Duration | Notes |
|---|---|---|---|
| 5d | 120h | ~1 week | Fastest — catches short-term breakouts but most prone to noise |
| 10d | 240h | ~2 weeks | |
| 20d | 480h | ~1 month | Classic "Turtle" lookback |
| 30d | 720h | ~1 month | |
| 60d | 1440h | ~2 months | |
| 90d | 2160h | ~3 months | Quarter boundary |
| 150d | 3600h | ~6 months | Requires 6 months of data to compute |
| 250d | 6000h | ~10 months | Requires 10 months — **may not add value at hourly resolution** |
| 360d | 8640h | ~1 year | Requires 1 year — **likely redundant at hourly; test in Phase 0** |

**Phase 0 must determine:** Do all 9 lookbacks add value at hourly resolution, or does a subset (e.g., 120h through 2160h — the first 6) perform equally well? Longer lookbacks require more startup data and are computationally heavier, so eliminating the longest ones without performance loss is desirable.

### 4.5 Why the ensemble is more robust than a single lookback

This is the **core insight** of the Zarattini paper and the reason J is expected to handle regime changes better than G.

A single lookback period creates a fragile dependency: if you use a 20-day Donchian channel and the market shifts from a slow grind to a fast impulse, the 20-day window may be too slow to catch the new trend. Conversely, if you use a 5-day channel, you'll catch fast moves but also get whipsawed by noise in slow trends.

The ensemble eliminates this fragility by letting the *data* decide which lookback is relevant. In a fast-moving market, the short lookbacks fire first and pull the ensemble score up. In a slow trend, the long lookbacks provide the persistent signal while short lookbacks may flip back and forth. The ensemble score naturally adapts to the character of the current trend without any explicit regime detection or parameter switching.

This is why G failed and J may succeed: G used a single formation period (4h or 1d) to rank assets. If that formation period happened to be wrong for the current regime, the entire signal broke down. J hedges across 9 formation-equivalent windows simultaneously.

---

## Part 5: Exit Mechanism — Trailing Stop at Donchian Lower Band

### 5.1 Plain English

Once we're in a trade, we draw a "floor" under the price — the lowest point the asset has reached recently (over the shortest lookback period that triggered our entry). As the trend continues and the price makes new highs, the floor rises with it (because the recent low point keeps getting higher). But the floor **never drops** — it only moves up or stays flat.

If the price falls and touches this rising floor, we exit. The trend is over.

This is called a **trailing stop** because it "trails" behind the price as it rises. It locks in profit during a strong trend and cuts losses quickly when the trend reverses.

### 5.2 Technical detail

Two trailing stop approaches to test in Phase 0:

**Approach A — Donchian lower band trailing:**
```
trailing_stop_level(t) = DC_lower(t, N_shortest_active)
```
where `N_shortest_active` is the shortest lookback period whose breakout signal was active at entry. This gives the tightest trailing stop — exits quickly when the short-term trend breaks.

Exit when: `close(t) < trailing_stop_level(t)`

**Approach B — ATR-based trailing:**
```
trailing_stop_level(t) = highest_close_since_entry - (ATR_multiplier × ATR(t, 14))
```
This trails at a fixed distance (in volatility terms) below the peak price since entry. More conventional, not tied to the Donchian framework.

In Freqtrade, both are implemented via `custom_stoploss()`:
```python
def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
    # Look up trailing stop level from self.custom_info
    # Return negative distance from current_rate
    stop_level = self.custom_info[pair]['trailing_stop_level']
    return (stop_level - current_rate) / current_rate  # negative value = distance below current price
```

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
| `DataProvider` cross-pair loading | `bot_loop_start()` loads all 22 pairs, computes returns, ranks | Same loading pattern; compute Donchian channels instead of returns |
| `custom_info` storage | Stores cross-sectional ranks per pair per candle | Stores ensemble score + trailing stop level per pair per candle |
| `custom_stake_amount()` | Inverse-vol scaling with floor at 50% | Identical — reuse directly |
| `config_xsmom.json` structure | 22-pair StaticPairList, futures mode, fee settings | Copy and rename; update pair list if needed |
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
| **0** | "Does the Donchian ensemble signal work at hourly resolution? Is there a profitable operating point after fees?" | **Not started.** The paper uses daily data — hourly is untested. This is the critical gate. |
| **1** | "Does the signal survive implementation in Freqtrade? Do regime splits confirm robustness?" | Pending Phase 0 GO. |
| **2** | "Can we improve it with a macro trend filter (Candidate K)? Do optimized parameters hold out-of-sample?" | Pending Phase 1 GO. |
| **3** | "Does it work in live market conditions alongside LiqCascade?" | Pending Phase 2 GO. |

Exact numeric gates for each phase are in `EnsembleDonchianTrend_Dev_Plan.md`.

---

## Part 9: Strategy Variants (Planned)

**Module (to build):** `user_data/strategies/EnsembleDonchianStrategy_V01.py`

### V01 — MVP (Phase 1)

| Parameter | Default | Range to Test |
|---|---|---|
| `LOOKBACK_PERIODS` | `[120, 240, 480, 720, 1440, 2160, 3600, 6000, 8640]` | Phase 0 will determine if subset is sufficient |
| `ENTRY_THRESHOLD` | 0.5 | 0.3, 0.5, 0.7, 0.9 (Phase 0 sweep) |
| `TRAILING_STOP_METHOD` | `'donchian_lower'` | `'donchian_lower'` vs `'atr'` (Phase 0 comparison) |
| `TRAILING_STOP_LOOKBACK` | shortest active | shortest vs median active lookback |
| `ATR_MULTIPLIER` (if ATR method) | 3.0 | 2.0, 3.0, 4.0 |
| `VOL_SCALING_WINDOW` | 168 (7d) | Fixed for V01 |
| `VOL_SCALING_FLOOR` | 0.5 | Fixed for V01 |
| `MAX_OPEN_TRADES` | 5 | 5–8 depending on how many pairs are in breakout simultaneously |
| `LEVERAGE` | 2 | Fixed for V01 |
| `TIME_STOP_HOURS` | 720 (30d) | Safety net; should rarely fire |
| `stoploss` | -0.12 | Fixed hard stop as catastrophic protection |

**Backtest fee:** `--fee 0.0005` (5 bps per side; ~10 bps round trip).

### V02 — K-Filter Enhancement (Phase 2, if V01 validates)

Same as V01 plus a **multi-timeframe trend confirmation filter** (from Candidate K):
- Require a higher-timeframe indicator (e.g., daily MACD or 4h EMA200 direction) to confirm the trend direction before entry
- This addresses Lesson #4 (short-term indicators lie in macro trends) — prevents entering Donchian breakouts that are counter to the larger trend
- If V01 shows excessive entries during counter-trend periods (identifiable via regime-split analysis), V02 adds this filter
- Implementation: `informative_pairs()` adds daily timeframe for the macro indicator; `populate_entry_trend()` requires both ensemble score > threshold AND macro trend confirmation

---

## Part 10: Key Technical Decisions to Resolve in Phase 0

These are open questions that Phase 0 must answer before any Freqtrade code is written:

### 10.1 How many lookback periods at hourly resolution?

The paper uses 9 lookbacks (5d to 360d). At hourly resolution, the longest (8640h) requires a year of data just to start computing. Phase 0 should test:
- Full 9-lookback ensemble at 1h
- 6-lookback subset (120h to 2160h — drops the three longest)
- 5-lookback subset (120h to 1440h — drops the four longest)

If performance is similar with fewer lookbacks, use fewer. Less data required, less startup waste, simpler computation.

### 10.2 Donchian trailing stop vs ATR trailing stop?

Donchian lower band trailing is more theoretically coherent (the exit is from the same framework as the entry). ATR trailing is more conventional and may be easier to calibrate. Phase 0 should test both on the same dataset and compare profit factor, average hold duration, and max drawdown.

### 10.3 Does the signal work at 1h at all?

The hardest question. Trend-following systems typically use daily or weekly data. Hourly data has more noise. The ensemble may smooth out enough noise to work, or it may not. If the Phase 0 sweep shows no profitable operating point at 1h, try 4h before abandoning. If 4h also fails, the strategy may be fundamentally a slow-frequency one — in which case it conflicts with our active-trading objective and should not be pursued.

### 10.4 Entry threshold calibration

Higher threshold (e.g., 0.9 — only enter when 8+ of 9 lookbacks agree) produces fewer, higher-confidence entries. Lower threshold (e.g., 0.3) produces more entries but with lower per-trade confidence. Phase 0 should sweep this and plot the tradeoff between trade frequency and per-trade profitability. Our objective wants **both** high frequency and high per-trade edge — the sweep will show where the frontier is.

---

## Part 11: Lessons From Prior Projects (Applied Here)

| Lesson | What It Means | Application in J |
|--------|---------------|------------------|
| **#2:** Entry quality > exit optimization (RAME) | If the base signal has no edge, no exit tuning will fix it. | Phase 0 validates signal quality before building exits. |
| **#3:** Structural alpha > statistical alpha (RAME→LiqCascade) | Prefer signals with a clear *why*. | Trend-following has 40+ years of *why*: serial correlation, behavioral momentum, reflexive feedback loops. Structural, not statistical. |
| **#4:** Short-term indicators lie in macro trends (RAME) | Any short-term signal needs a macro filter. | V02 adds Candidate K's multi-timeframe macro filter. V01 relies on the ensemble's long lookbacks as implicit macro context. |
| **#7:** Fee economics before infrastructure (LOB) | Validate fee-inclusive profitability before building. | Phase 0 Day 2 is a fee-inclusive sweep. No Freqtrade code until sweep passes. |
| **#8:** Paper results don't transfer to our fee tier (LOB) | Always compute P&L at our actual fees. | All backtests use `--fee 0.0005` (our Binance retail tier). |
| **#9:** Half-life must match trading frequency (CointPairs) | Don't build a strategy whose natural timescale doesn't match your trading frequency. | Phase 0 explicitly checks whether the signal works at 1h. If it only works at daily, we don't force it. |
| **#10:** Bull-market bias (CointPairs) | Don't validate only on bull periods. | Regime splits (2022 bear, 2023 range, 2024–2025 bull) mandatory at every gate. |
| **#11:** Time-stop rate as diagnostic (LiqCascade) | If > 50% of trades exit via time stop, the entry signal is too loose. | Time stop is a backup safety net. If it fires > 30%, raise the entry threshold. |
| **#12:** Unhedged directional alt exposure is dangerous (Candidate E) | Don't bet big on single alts without risk controls. | Long-only across 20 pairs with inverse-vol sizing diversifies away single-asset concentration. |
| **G's parking lesson:** Single formation period is regime-fragile | One lookback = one point of failure. | Ensemble over 9 lookbacks hedges regime sensitivity. This is J's raison d'être. |

---

## Part 12: Risk Factors and What Could Go Wrong

### 12.1 The signal doesn't compress to hourly (PRIMARY RISK)

Trend-following is traditionally a slow-frequency strategy (daily/weekly). The Zarattini paper uses daily data. If the Donchian breakout signal is too noisy at hourly resolution, the ensemble may generate false breakouts that get stopped out before the trend develops. Phase 0 is designed to catch this early.

**Mitigation:** Test 4h as a fallback. If even 4h fails, accept that this is a daily-frequency strategy and evaluate whether the trade frequency (with 20 pairs) is sufficient at daily to meet our objectives.

### 12.2 Momentum crash

A sudden, violent reversal wipes out weeks of gains in a day. This is the canonical risk of all trend-following strategies. Grobys (2025) documents severe momentum crashes in crypto specifically.

**Mitigation:** Inverse-vol position sizing (underweights the most crash-prone assets), Donchian trailing stop (exits when trend breaks), 20-pair diversification (single crash doesn't dominate), 2x leverage cap (limits tail risk).

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

---

*Authoritative technical reference for Candidate J. For phase gates and go/no-go criteria, see `EnsembleDonchianTrend_Dev_Plan.md`. For project-wide context, see `AlgoTrading_Research_Log.md`.*
