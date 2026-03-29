# Cross-Sectional Momentum (Candidate G) — Phase 0 Summary

**Project:** freqtrade-strategy-lab  
**Phase:** 0 (data + exploration) — complete  
**Date:** 2026-03-29  

**Follow-on:** Phase 1 baseline backtests are in **`CrossSectionalMomentum_Phase1_Summary.md`**. **Candidate G is PARKED (2026-03-29)** — **empirically weak**; see **`AlgoTrading_Research_Log.md`**.

---

## What we’re building (plain English)

**Cross-sectional momentum** means: look at many crypto futures at once, see which ones have gone up or down the most over a chosen lookback window, then bet that **relative** strength (or weakness) will continue for a while.

- **Winners:** the coins that rose the most versus the rest of the pack → candidate **longs**.
- **Losers:** the coins that fell the most → candidate **shorts** (or we may skip shorts later if data says losers bounce too often).
- You **rebalance** on a schedule (for example every few hours or days): re-rank everyone, adjust who you’re long and short.

This is **not** the same as Liquidation Cascade (which reacts to a specific market event). It’s a **systematic, always-on** strategy that tries to profit from **differences in performance across a basket** of assets, using only ordinary price candles (OHLCV). No sidecar, no special feeds.

**Why we’re doing Phase 0 first:** before writing the full trading bot, we check whether there is enough **spread** between winners and losers to matter after fees, and whether rankings aren’t pure noise at the timeframes we care about.

---

## What Phase 0 actually did

1. **Configuration** — Defined a **universe of 22 liquid Binance USDT perpetual futures** (major alts + majors), stored in `config/config_xsmom.json`.

2. **Data** — Downloaded **1-hour** historical candles from 2022 through early 2026 for all those pairs (standard Freqtrade `download-data` flow).

3. **Exploration script** — `user_data/scripts/xsmom_phase0_exploration.py` measures, for several lookback lengths:
   - **Dispersion:** “How far apart are the coins’ returns?” — think of it as the **gap** between the best and worst performers in the group, summarized as a typical (median) spread in **basis points** (1 bp = 0.01%; 100 bps = 1%).
   - **Rank churn (1-hour snapshot):** “If we rank coins by their recent return, how similar is that ranking to the ranking one hour earlier?” A **positive** number means leaders tend to stay leaders; a **negative** number means the leaderboard **reshuffles** a lot hour to hour.

**Fees in the back of our mind:** retail round-trip cost is often talked about as **~10 bps** (0.10%) total. If typical cross-coin “spread” in returns is **smaller** than that, the strategy has little room to breathe after paying the exchange.

---

## Results (layman readout)

All numbers come from the exploration run on the downloaded 1h data (22 pairs where files exist).

### Coverage

- **22 / 22** pairs loaded successfully.
- There are **many thousands** of hours where at least **15** coins have valid data (enough to rank a meaningful basket).
- **About 19,000** hourly bars have **all 22** coins present at once; earlier dates can show **fewer** coins because some contracts **listed later** on Binance.

### Dispersion (typical gap between coins’ returns, in bps)

| Lookback (what “recent performance” means) | Median dispersion | Plain-English takeaway |
|--------------------------------------------|-------------------|-------------------------|
| **1 hour** (last single hour) | **~45 bps** | Slightly **below** the “~50 bps” sanity check from the dev plan. **Not** catastrophic, but tight vs fees. |
| **4 hours** | **~91 bps** | **Comfortable** headroom vs ~10 bps fees. |
| **1 day** | **~236 bps** | Plenty of room. |
| **1 week** | **~640 bps** | Very wide spread. |
| **30 days** | **~1,380 bps** | Very wide spread. |

**Layman summary:** When we only look at **the last hour**, the pack doesn’t separate **quite** as much on average as our strict Phase 0 rule hoped. When we look at **four hours or more**, the differences between winners and losers are **clearly** larger than trading costs, so a momentum-style ranking has **economic air to breathe**.

### Rank stability at 1 hour

- **Lag-1 rank correlation (1h formation):** roughly **−0.04** (slightly **negative**).
- **Layman summary:** The **hourly leaderboard shuffles** quite a bit. That’s not shocking for crypto: short-term leadership rotates fast. It does **not** by itself kill the idea; it mainly says **“don’t assume 1-hour-only signals are stable.”**

*(Note: For longer lookbacks, measured rank correlation across **consecutive hours** gets very high partly because those return windows **overlap** heavily—like comparing two sliding windows that share most of the same days. So those big positive numbers are **mechanical overlap**, not a separate “discovery.” The 1h case is the cleanest quick read on hourly churn.)*

---

## Go / no-go in simple terms

| Check | Outcome |
|--------|---------|
| **Strict Phase 0** (1h dispersion **and** positive 1h rank persistence) | **No** — 1h median dispersion is just under 50 bps; 1h persistence is slightly negative. |
| **Practical read** (from dev plan: if 1h is weak, look at **longer** formations) | **Yes** — **4h and longer** lookbacks show **strong** dispersion vs fees. |

**Bottom line for the next step:** Phase 1 (building the strategy and backtests) is reasonable **if we treat “formation period” of **at least ~4 hours** as a first-class setting**, and use **1 hour** as a sensitivity check rather than the only design. That matches the written escape hatch in `CrossSectionalMomentum_Dev_Plan.md` when the 1h bar is borderline.

---

## Files touched in Phase 0

| File | Role |
|------|------|
| `config/config_xsmom.json` | Universe, futures settings, Docker-friendly config path |
| `user_data/scripts/xsmom_phase0_exploration.py` | Metrics and go/no-go text |
| `user_data/data/binance/futures/*.feather` | Downloaded 1h OHLCV (via Freqtrade) |

---

## Where to read more

- **Full development plan:** `user_data/info/CrossSectionalMomentum_Dev_Plan.md`
- **Project context and candidate status:** `user_data/info/AlgoTrading_Research_Log.md` (Candidate G)

---

*This summary is for humans; implementation details stay in the dev plan and the exploration script.*
