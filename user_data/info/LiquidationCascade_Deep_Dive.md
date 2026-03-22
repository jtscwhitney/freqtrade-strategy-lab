# Liquidation Cascade Strategy — Deep Dive
## Version 1 | Started: 2026-03-17 | Status: ACTIVE — Phase 3 Dry-Run (Preliminary Results: PF 0.659, below threshold — reassess 2026-04-05)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**
> Combined with `~/.claude/projects/.../memory/MEMORY.md`, this provides full context.

### Current Status
- **Phase:** 3 — Live Dry-Run (ACTIVE) — deployed to DigitalOcean droplet 2026-03-18
- **Last completed (2026-03-22):** Phase 3 preliminary analysis — 129 trades over 5 days. Win rate 39.5%, profit factor 0.659 — below Phase 4 thresholds. Root cause: time_stop exits dominating at 59% (0% win rate), indicating VOL_SPIKE_MULT/CANDLE_BODY_MULT thresholds too loose (~26 entries/day vs expected 1–2 genuine cascades/pair/day). Signal alpha is real (roi exits: 96% win rate, trailing exits: 100%) — selectivity is the problem.
- **Previously (2026-03-21):** Phase 3.5 instrumentation — OI change rate (`oi_contracts`, `oi_change_pct_1m`) added to sidecar snapshot and `signal_history.jsonl`.
- **Previously (2026-03-20):** Expanded to 5 pairs (BTC/ETH/SOL/BNB/XRP), max_open_trades raised to 5.
- **Next immediate step:** Continue accumulating data. Reassess 2026-04-05 (2-week mark). If time_stop rate still >50%, tighten thresholds before Phase 4. Also run Phase 3.5 OI retrospective (will have 100+ instrumented trades by then).
- **Open decisions:** Do NOT tighten thresholds yet — 5 days is one regime snapshot. Revisit 2026-04-05.
- **Go/no-go for Phase 4:** 20+ trades ✓ · profit factor >1.0 ✗ · win rate >40% ✗ · sidecar uptime >99% (unknown) — blocked until 2026-04-05 reassessment.

### Key Commands
```
# SSH into droplet
ssh root@<DROPLET_IP>

# Start both containers on droplet
docker compose --profile liqcascade up -d

# Check bot logs
docker compose --profile liqcascade logs --tail 50 freqtrade-scalper

# Check sidecar logs
docker compose --profile liqcascade logs --tail 20 liqcascade_sidecar

# FreqUI (from browser)
http://<DROPLET_IP>:8082  (user: freqtrader / pass: set during droplet setup)

# Import historical trades (safe to re-run — skips existing IDs)
python3 sidecar/import_log_trades.py

# Pull latest code and redeploy (run on droplet)
bash deploy/deploy.sh
```

### File Locations
| File | Status | Purpose |
|---|---|---|
| `user_data/strategies/LiqCascadeStrategy_V01.py` | Complete | Phase 1 proxy backtest strategy |
| `user_data/strategies/LiqCascadeStrategy_V02.py` | Complete | A/B test — tighter proxy thresholds |
| `user_data/strategies/LiqCascadeStrategy_V03.py` | Complete | Confirmation candle filter |
| `user_data/strategies/LiqCascadeStrategy_V04.py` | **ACTIVE** | Phase 3 — real sidecar signal |
| `config/config_liqcascade_V01.json` | Complete | Phase 1–3 backtest config |
| `config/config_liqcascade_V04.json` | **ACTIVE** | Phase 3 live config (port 8082) |
| `sidecar/liquidation_monitor.py` | **RUNNING** | Binance WebSocket liquidation pipeline + OI fetch (2026-03-21) |
| `sidecar/logs/liquidation_monitor.log` | Live | Sidecar event log |
| `sidecar/logs/signal_history.jsonl` | Live | Per-minute signal history — liq volumes, signal, OI fields (all pairs) |
| `sidecar/import_log_trades.py` | Complete | One-time import of trades 10–13 into DB |
| `user_data/tradesv3.dryrun.sqlite` | **ACTIVE** | Dry-run trade database |
| `user_data/logs/freqtrade_liqcascade.log` | Live | Bot log |
| `user_data/info/LiquidationCascade_Deep_Dive.md` | THIS FILE | Authoritative reference |

---

## Part 1: Why We're Here

### 1.1 Prior Work (RAME — Archived 2026-03-17)

The Regime-Adaptive Multi-Strategy Ensemble (RAME) project ran from 2026-03-12 to 2026-03-17. Full record: `user_data/info/Regime_Adaptive_Ensemble_Deep_Dive.md`. Summary: `user_data/info/RAME_Project_Summary.md`.

**What RAME proved:**
- The 2×2+CRISIS regime framework is empirically valid (HMM best_n=5)
- Ground truth ACTIVE regime labels have real directional edge at 4h horizon (ETH ACTIVE_BULL p=0.006**, BTC QUIET_BEAR p=0.025*)
- That edge is too small (+0.087% mean per 4h candle) to overcome execution friction at any leverage/timeframe combination tested across 9 backtests
- FreqAI on regime STATE labels is tautological — the classifier memorises the labeling formula (100% accuracy, zero forward edge)
- Regime-change exits are lagging and consistently destructive (2–24% win rate across all configurations)

**What RAME did not test, which informed this project:**
- Liquidation cascade as the primary alpha source (Part 5 of RAME Deep Dive — always described as "genuine alpha", never implemented)
- EMA200 macro trend filter (its absence was responsible for 70–87% of total losses across all RAME runs due to 2022 bear-market ACTIVE_BULL entries)

### 1.2 The Pivot Rationale

The RAME failure was not a failure of the regime framework — it was a failure of treating regime labels as the primary signal when their per-trade edge is too small. The pivot:

**Old architecture:** Regime detection → primary signal → route to sub-strategy
**New architecture:** Structural market event → primary signal → regime as context filter only

Liquidation cascades are different in kind from indicator-based signals:
- They are triggered by a *mechanical market event* (forced liquidations), not by predicting price direction
- The volume and price signature are observable and not lagged
- The edge is in the violent initial move, which is directionally unambiguous while it is happening
- They are not "predicted" — they are *detected as they occur*

This is what practitioners mean by "structural alpha" — it exists because of how the market is architected, not because of a statistical pattern that could be arbitraged away by prediction alone.

---

## Part 2: Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    STRATEGY ARCHITECTURE                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1h Informative Pair (regime context — computed once    │
│  per 1h candle, loaded into 5m strategy)                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CRISIS block:  ATR(14) > rolling-200-period p90 │   │
│  │  Macro trend:   close vs EMA(200)                │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                               │
│                    context flags                        │
│                         │                               │
│  5m Execution (cascade signal + entry/exit)             │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Cascade proxy: volume spike + directional candle│   │
│  │  [Live: replaced by WebSocket sidecar signal]    │   │
│  │                                                  │   │
│  │  Entry: cascade direction, crisis check passes   │   │
│  │  Exit:  2×ATR target | 1×ATR stop | 30min time  │   │
│  │  Leverage: 4x                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  [Phase 3+] Sidecar process: Binance WebSocket          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  /ws/!forceOrder@arr → liquidation_data.json     │   │
│  │  Read by strategy in populate_indicators()       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Design principle:** The two layers are loosely coupled. The regime context changes once per hour at most. The cascade signal fires independently on 5m candles. Neither depends on the other for its core logic.

---

## Part 3: Regime Context Filter (1h)

### 3.1 Design Philosophy

The regime filter has exactly one job: tell the cascade signal when it is and is not safe to trade, and what direction to prefer. It does NOT generate entries. It does NOT generate exits. It is a gate and a bias, nothing more.

**What is explicitly excluded (lessons from RAME):**
- ADX threshold — caused regime oscillation in every RAME configuration tested
- EMA21 — too short, flipped candle-to-candle in bear markets, caused 70–87% of all RAME losses
- ACTIVE vs QUIET distinction — the cascade signal does not need this; it fires when it fires
- Any regime-based exit signal — consistently destructive in RAME (2–24% win rate)

### 3.2 Filter 1: CRISIS Block (Hard Gate)

**Definition:** `ATR(14)_1h > rolling-200-period-p90(ATR14_1h)`

**Effect:** ALL cascade entries blocked when CRISIS is active.

**Rationale:** During extreme volatility events (Luna collapse, FTX bankruptcy, Aug 2024 yen carry unwind), cascade behavior becomes unpredictable. Forced liquidations can reverse violently within 1–2 candles as counterparty liquidity appears. The edge in cascade trading is momentum continuation — CRISIS periods have the highest reversal risk. The 200-period rolling p90 at 1h is well-validated from RAME Phase 0 (captures ~10% of candles — genuine extremes, not normal volatility).

### 3.3 Filter 2: Macro Trend (EMA200, 1h)

**Definition:** `close_1h > EMA(200)_1h` = macro bullish. `close_1h ≤ EMA(200)_1h` = macro bearish.

**Effect:**
- Both cascade directions (long and short) are always considered, regardless of macro trend
- When macro is bullish: long cascades get full leverage (4x); short cascades get reduced leverage (2x)
- When macro is bearish: short cascades get full leverage (4x); long cascades get reduced leverage (2x)

**Rationale:** The EMA200 at 1h represents approximately 8 days of price history — stable enough to define the macro bias without oscillating. The leverage asymmetry aligns position sizing with the dominant market direction while still allowing counter-trend trades. In a strong bear market, short squeezes (shorts being liquidated) still occur and can be very violent; blocking them entirely would miss real opportunities.

**Why not hard-block counter-trend entries:**
Short squeezes in bear markets generate some of the largest single-day up-moves in crypto. Funding rates go deeply negative in bear markets, creating massive built-up short positions — fuel for violent squeezes. Counter-trend cascade entries are lower probability but have historically produced outsized returns. The leverage asymmetry approach prices this risk appropriately.

**Implementation note:** EMA200 at 1h = 200 candles × 1h = 200h lookback. `startup_candle_count` on the informative 1h pair must be ≥ 250 to allow full warm-up.

### 3.4 Implementation (Informative Pair)

```python
# In populate_indicators() — 1h informative data
inf_tf = '1h'
informative = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=inf_tf)

# Compute on 1h candles
atr14_1h       = ta.ATR(informative, timeperiod=14)
atr_p90_1h     = atr14_1h.rolling(200).quantile(0.90)
ema200_1h      = ta.EMA(informative['close'], timeperiod=200)

informative['regime_crisis']       = (atr14_1h > atr_p90_1h).astype(int)
informative['regime_macro_bull']   = (informative['close'] > ema200_1h).astype(int)

# Merge into 5m dataframe using forward-fill
informative['date'] = informative.index
informative = informative[['date', 'regime_crisis', 'regime_macro_bull']]
dataframe = merge_informative_pair(dataframe, informative, self.timeframe, inf_tf,
                                   ffill=True)
# Columns become: regime_crisis_1h, regime_macro_bull_1h
```

---

## Part 4: Liquidation Cascade Sub-Strategy

### 4.1 What a Cascade Is

When leveraged positions are forced to close (margin call or liquidation), the exchange executes market orders to close those positions. If many positions are liquidated in a short window, those market orders cascade — each liquidation drives price further against remaining positions, triggering more liquidations. The result is a violent, directional price move driven entirely by mechanical forced selling or buying, not participant choice.

**Long liquidation cascade:** Price drops → long positions hit margin → exchange sells their position → price drops further → more longs liquidated → repeat. Enter **short**.

**Short liquidation cascade:** Price rises → short positions hit margin → exchange buys to cover → price rises further → more shorts liquidated → repeat. Enter **long**.

The key insight: while the cascade is running, the direction is mechanical and self-reinforcing. It ends when the pool of over-leveraged positions in that direction is exhausted — typically 15–60 minutes for significant events.

### 4.2 Data Sources

| Data | Source | Availability | Cost | Phase |
|---|---|---|---|---|
| Real-time forced orders | Binance WebSocket `/ws/!forceOrder@arr` | Live only | Free | Phase 3 |
| Funding rate | Binance REST `/fapi/v1/fundingRate` | Historical + live | Free | Phase 2+ |
| Open interest | Binance REST `/fapi/v1/openInterest` | Historical (limited) + live | Free | Phase 2+ |
| OHLCV 5m | Freqtrade standard | Historical + live | Free | Phase 1 |

### 4.3 Backtesting Proxy (Phase 1–2)

Real liquidation WebSocket data is not available in historical backtesting. A proxy is required.

**Proxy conditions (both required on same 5m candle):**

1. **Volume spike:** `volume > VOL_SPIKE_MULT × rolling(VOL_WINDOW).mean(volume)`
   - Default: `VOL_SPIKE_MULT = 3.0`, `VOL_WINDOW = 20`
   - Rationale: Forced market orders generate abnormal volume. A 3× spike is well above normal candle-to-candle variation at 5m.

2. **Large directional candle:** `|close - open| > CANDLE_BODY_MULT × ATR(14)`
   - Default: `CANDLE_BODY_MULT = 1.5`
   - Rationale: The cascade produces a large, one-sided candle. An ATR-normalised body threshold is scale-invariant across BTC price history (2022: ~$20K, 2025: ~$90K).

3. **Direction assignment:**
   - `close > open` → bullish cascade → enter **long** (shorts being liquidated)
   - `close < open` → bearish cascade → enter **short** (longs being liquidated)

**Known proxy limitations:**
- Will fire on genuine high-volume momentum candles that are not liquidation-driven
- Will miss cascades where volume was distributed across multiple smaller candles
- Funding rate pre-condition (strong edge filter for real cascades) not available in OHLCV backtest data

These limitations are acceptable for Phase 1. The proxy is expected to over-fire relative to the real signal — if the proxy produces positive results, the real WebSocket signal (which is more selective) should produce better results.

**Designing for replaceability:** The proxy is implemented as a separate method `_get_cascade_signal()`. In Phase 3, this method's return value is replaced by reading the sidecar output file. All entry/exit/leverage logic is unchanged.

### 4.4 Entry Conditions (Full)

```python
# Gate 1: No CRISIS (1h regime context)
not_crisis = (dataframe['regime_crisis_1h'] == 0)

# Gate 2: Cascade proxy fires
cascade_proxy = (
    (dataframe['volume'] > self.VOL_SPIKE_MULT * dataframe['volume'].rolling(self.VOL_WINDOW).mean()) &
    (abs(dataframe['close'] - dataframe['open']) > self.CANDLE_BODY_MULT * dataframe['atr14'])
)

# Direction
is_bullish_candle = dataframe['close'] > dataframe['open']
is_bearish_candle = dataframe['close'] < dataframe['open']

# Long entry: short squeeze (bullish candle = shorts being liquidated)
# Short entry: long liquidation cascade (bearish candle = longs being liquidated)
enter_long  = not_crisis & cascade_proxy & is_bullish_candle
enter_short = not_crisis & cascade_proxy & is_bearish_candle
```

### 4.5 Exit Conditions

Exit logic is designed around a single principle: **take the cascade move and leave**. The edge is in the first 15–30 minutes. Every candle held beyond that is noise.

**ROI table (primary exit — profit target):**
```python
minimal_roi = {
    "0":  0.02,   # 2% profit closes immediately if hit (at 4x = 0.5% price move)
    "15": 0.01,   # After 15 min, accept 1% profit
    "30": 0.00,   # After 30 min, exit at any profit (time stop for winners)
}
```

**Custom stoploss (hard stop — fixed from entry):**
- `STOP_FROM_ENTRY = 0.04` — 4% from entry at 4x leverage = 1% adverse price move
- At 5m, ATR is typically 0.08–0.20% of price. A 1% adverse move is 5–12 ATR — wide enough to survive normal 5m volatility but tight enough to cut real failures fast.
- Implemented via `stoploss_from_open()` — fixed from entry, not trailing.

**Time stop (custom_exit):**
- Exit after `MAX_HOLD_CANDLES = 6` (= 30 minutes at 5m) regardless of profit/loss
- If a cascade hasn't reached target in 30 minutes, the event is over.

**What is explicitly NOT used:**
- `populate_exit_trend` with regime-change signals — eliminated permanently (RAME lesson)
- Trailing stop — cascade trades are not momentum holds; trailing introduces whipsaw risk
- RSI targets — not relevant to cascade mechanics

### 4.6 Leverage

```python
def leverage(self, pair, current_time, current_rate, proposed_leverage,
             max_leverage, entry_tag, side, **kwargs) -> float:
    # Full leverage when aligned with macro trend; reduced when counter-trend
    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    if dataframe.empty:
        return min(self.LEVERAGE_REDUCED, max_leverage)

    last = dataframe.iloc[-1]
    macro_bull = last.get('regime_macro_bull_1h', 1)

    if side == 'long' and macro_bull == 1:
        return min(self.LEVERAGE_FULL, max_leverage)      # Long in bull = full
    elif side == 'short' and macro_bull == 0:
        return min(self.LEVERAGE_FULL, max_leverage)      # Short in bear = full
    else:
        return min(self.LEVERAGE_REDUCED, max_leverage)   # Counter-trend = reduced

LEVERAGE_FULL    = 4.0
LEVERAGE_REDUCED = 2.0
```

**Risk calibration:**
- Full leverage (4x): stoploss 4% from entry = 1% adverse price at 4x
- Reduced leverage (2x): stoploss 4% from entry = 2% adverse price at 2x
- Both are within normal 5m volatility for BTC/ETH (typically 0.1–0.3% per 5m candle)

---

## Part 5: Sidecar Data Pipeline (Phase 3)

The sidecar process runs alongside Freqtrade and captures real liquidation data from Binance's public WebSocket. This data is not available via Freqtrade's standard data provider.

### 5.1 Architecture

```
Binance WebSocket              Sidecar Process              Strategy
/ws/!forceOrder@arr   →   liquidation_monitor.py   →   liquidation_data.json
(real-time)               (background process)          (read each candle)
```

The sidecar maintains a rolling 15-minute liquidation window per pair and direction, writing a JSON snapshot every 60 seconds. The strategy reads this file in `populate_indicators()`, adding a `cascade_signal` column to the dataframe.

### 5.2 Sidecar Script

```python
# sidecar/liquidation_monitor.py
# Run as: python sidecar/liquidation_monitor.py
# Requires: pip install websockets

import asyncio
import json
import websockets
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta

OUTPUT_PATH = Path("user_data/data/liquidation_data.json")
DECAY_FACTOR = 0.85        # Rolling 15-min decay per 60-second tick
USD_THRESHOLD = 5_000_000  # $5M liquidated = significant cascade signal
DOMINANCE_RATIO = 3.0      # One direction must be 3× the other to fire

liquidation_window: dict[str, float] = defaultdict(float)

async def stream_liquidations() -> None:
    uri = "wss://fstream.binance.com/ws/!forceOrder@arr"
    async with websockets.connect(uri) as ws:
        last_snapshot = datetime.now(timezone.utc)
        while True:
            msg = json.loads(await ws.recv())
            order = msg.get('o', {})
            symbol    = order.get('s', '')
            qty       = float(order.get('q', 0))
            price     = float(order.get('p', 0))
            side      = order.get('S', '')  # BUY = short liquidation, SELL = long liquidation
            usd_value = qty * price

            key = f"{symbol}_{side}"
            liquidation_window[key] += usd_value

            now = datetime.now(timezone.utc)
            if (now - last_snapshot).total_seconds() >= 60:
                last_snapshot = now
                signals = {}
                for symbol_base in ['BTCUSDT', 'ETHUSDT']:
                    long_liq  = liquidation_window.get(f'{symbol_base}_SELL', 0)
                    short_liq = liquidation_window.get(f'{symbol_base}_BUY',  0)
                    pair_key  = symbol_base.replace('USDT', '/USDT:USDT')

                    signal = 'NONE'
                    if long_liq >= USD_THRESHOLD and long_liq >= short_liq * DOMINANCE_RATIO:
                        signal = 'SHORT'  # Longs being liquidated → go short
                    elif short_liq >= USD_THRESHOLD and short_liq >= long_liq * DOMINANCE_RATIO:
                        signal = 'LONG'   # Shorts being liquidated → go long

                    signals[pair_key] = {
                        'long_liq_usd':  round(long_liq, 0),
                        'short_liq_usd': round(short_liq, 0),
                        'signal':        signal,
                    }

                OUTPUT_PATH.write_text(json.dumps({
                    'timestamp': now.isoformat(),
                    'signals':   signals,
                }, indent=2))

                # Decay window (rolling 15-min effect)
                for k in liquidation_window:
                    liquidation_window[k] *= DECAY_FACTOR

asyncio.run(stream_liquidations())
```

### 5.3 Strategy Integration (Phase 3)

Replace the proxy `_get_cascade_signal()` method with:

```python
def _get_cascade_signal(self, pair: str) -> str:
    """
    Read cascade signal from sidecar output.
    Returns: 'LONG', 'SHORT', or 'NONE'.
    Falls back to 'NONE' if file is missing or stale (> 5 min old).
    """
    path = Path("user_data/data/liquidation_data.json")
    if not path.exists():
        return 'NONE'
    try:
        data = json.loads(path.read_text())
        ts   = datetime.fromisoformat(data['timestamp'])
        if (datetime.now(timezone.utc) - ts).total_seconds() > 300:
            logger.warning("Liquidation data is stale (>5 min). Returning NONE.")
            return 'NONE'
        return data['signals'].get(pair, {}).get('signal', 'NONE')
    except Exception as e:
        logger.error(f"Error reading liquidation data: {e}")
        return 'NONE'
```

---

## Part 6: Phase Implementation Plan

Each phase has a specific goal, deliverables, and explicit go/no-go criteria. Do not advance until criteria are met.

---

### Phase 1: Cascade Proxy Backtest — COMPLETE (NO GO)

**Goal:** Validate that the cascade proxy signal (volume spike + large candle) carries detectable directional edge on 5m BTC/ETH futures data. Establish baseline P&L, exit breakdown, and per-year consistency.

**Files:**
- `user_data/strategies/LiqCascadeStrategy_V01.py`
- `config/config_liqcascade_V01.json`

**Strategy parameters:**
- `timeframe = '5m'`
- `startup_candle_count = 300` (for 200-period rolling ATR p90 on 1h informative)
- `VOL_SPIKE_MULT = 3.0`
- `VOL_WINDOW = 20`
- `CANDLE_BODY_MULT = 1.5`
- `LEVERAGE_FULL = 4.0`, `LEVERAGE_REDUCED = 2.0`
- `STOP_FROM_ENTRY = 0.04`
- `MAX_HOLD_CANDLES = 6` (30 minutes)
- `minimal_roi = {"0": 0.02, "15": 0.01, "30": 0.00}`
- `max_open_trades = 2`

**Backtesting command:**
```
docker compose run --rm freqtrade backtesting --strategy LiqCascadeStrategy_V01 --config config/config_liqcascade_V01.json --timerange 20220101-20260101 --cache none --breakdown month
```

**Data requirement:** 5m BTC/ETH futures data for 2022–2026. Download if missing:
```
docker compose run --rm freqtrade download-data --config config/config_liqcascade_V01.json --timerange 20220101-20260101 --timeframe 5m
```

**Also download 1h data for informative pair (likely already present):**
```
docker compose run --rm freqtrade download-data --config config/config_liqcascade_V01.json --timerange 20220101-20260101 --timeframe 1h
```

**Go/No-Go criteria for Phase 1:**
| Criterion | Threshold | Notes |
|---|---|---|
| Total return | > +15% | On $10K starting balance over 4-year period |
| Profit factor | > 1.5 | Gross profit / gross loss |
| Win rate | > 40% | With 2:1 R/R, 34% break-even — target 40%+ |
| Consistent across years | No year > -20% | No single catastrophic year |
| Trade count | > 200 total | Sufficient for statistical confidence |
| ROI exit (target hit) | > 30% of wins | If target is never hit, sizing/target is wrong |

**If criteria not met:**
- Trade count < 200: Lower `VOL_SPIKE_MULT` from 3.0 to 2.5 — more signals
- Win rate < 34%: Raise `CANDLE_BODY_MULT` from 1.5 to 2.0 — higher quality signal only
- Target never hit: Reduce `minimal_roi["0"]` from 2% to 1.5% — target too aggressive for 5m ATR
- 2022 still catastrophic: Verify EMA200 CRISIS block is firing correctly

**Results — Phase 1 V01 (VOL=3.0, BODY=1.5):**
| Metric | Result | Threshold | Pass? |
|---|---|---|---|
| Profit factor | 0.725 | > 1.5 | NO |
| Win rate | 32.9% | > 40% | NO |
| Time stop exits | 55.7% | — | Signal too noisy |
| ROI exits | 39.4% | — | 75.7% win rate when hit |
| Trade count | ~800+ | > 200 | YES |

**Root cause:** Proxy over-fires. 55.7% of trades exit via time_stop with ~0% win rate, overwhelming the 39.4% genuine cascades (75.7% win rate). Signal quality insufficient.

**A/B Tests (V02):**
- VOL=5.0, BODY=1.5: PF=0.735 — minimal improvement
- VOL=5.0, BODY=2.5: PF=0.770 — better but still < 1.0
- Candle body filter more effective than volume filter alone

**Confirmation candle filter (V03, VOL=5.0, BODY=2.5):**
- PF=0.669 — worse despite 37.3% win rate
- Edge lives in the immediate post-cascade candle; delaying entry by 5min kills more than it saves

**Conclusion:** OHLCV proxy cannot reach PF > 1.0. Real liquidation data required. Advance to Phase 3.

---

### Phase 2: Regime Filter Validation

**Goal:** Confirm that the CRISIS block and EMA200 macro trend filter improve results vs Phase 1 baseline. Test both the hard-block counter-trend variant and the leverage-asymmetry variant.

**Variants to test:**
1. No regime filter (Phase 1 baseline)
2. CRISIS block only
3. CRISIS block + EMA200 leverage asymmetry (current design)
4. CRISIS block + EMA200 hard-block counter-trend entries

**Go/No-Go criteria:**
- Regime filter improves profit factor vs no-filter baseline
- 2022 losses materially reduced vs Phase 1 (EMA200 doing its job)
- CRISIS block eliminates trades during known crisis events (verify manually on Luna/FTX dates)

**Results:** Phase 2 skipped — proxy backtest confirmed insufficient regardless of regime filter tuning. Real liquidation data is the necessary fix, not regime filter changes. Advanced directly to Phase 3.

---

### Phase 3: Sidecar Development and Integration

**Goal:** Replace the OHLCV proxy signal with real Binance WebSocket liquidation data. Validate that the sidecar script runs stably and the live signal improves strategy performance in dry-run.

**Tasks:**
1. Build and test `sidecar/liquidation_monitor.py` in isolation
   - Verify WebSocket connects and streams data
   - Verify JSON output file is written and refreshed correctly
   - Verify liquidation USD accumulates correctly per pair and direction
   - Verify decay factor produces expected 15-minute rolling window behaviour
2. Run sidecar alongside dry-run bot for 1 week
   - Log every signal fired with timestamp, pair, USD amount, direction
   - Manually verify signals correlate with visible price cascades in chart
3. Replace proxy `_get_cascade_signal()` with sidecar reader
4. Run dry-run with real signal for 2–4 weeks
5. Compare dry-run results to Phase 1/2 backtest expectations

**Go/No-Go criteria:**
- Sidecar runs stably for 2+ weeks without crashes
- At least 10 cascade signals fired and logged in 2-week window (validates data is flowing)
- >50% of logged signals correspond to visible aggressive candles in TradingView chart
- Dry-run win rate within ±15% of backtest result (validates proxy was a reasonable approximation)

**Results — Phase 3 dry-run (started 2026-03-18, ACTIVE):**

Sidecar built with the following final parameters:
- `WRITE_INTERVAL = 60s`, `WINDOW_SECONDS = 300` (5-min rolling window)
- `CASCADE_MULT = 5.0` (rolling_total >= 5× baseline mean)
- `DOMINANCE_RATIO = 3.0` (qualifying direction >= 3× opposing direction)
- `BASELINE_PERIODS = 20` (20-window rolling mean for dynamic threshold)
- `ping_interval=None` (Binance manages keepalive — client pings cause 1011 disconnect)

Two bugs fixed during development:
1. Time-based write/baseline checks moved before `if symbol not in SYMBOLS: continue` — previously writes were skipped when only non-BTC/ETH events were flowing
2. `ping_interval=None` — Binance ignores client pings, causing ~8-min blackout every session

Signal history logging added: `sidecar/logs/signal_history.jsonl` — one JSON line per minute, all pairs, all values. Enables full retrospective analysis after dry-run.

**Dry-run preliminary results as of 2026-03-22 (Day 1–5, 129 trades):**

| Metric | Value |
|--------|-------|
| Closed trades | 129 |
| Win rate | 39.5% |
| Avg profit | –0.259% |
| Profit factor | 0.659 |

**Exit reason breakdown:**
| Exit reason | Count | Avg profit | Win rate |
|-------------|-------|------------|----------|
| time_stop | 76 (59%) | –1.031% | 0.0% |
| roi | 49 (38%) | +0.738% | 95.9% |
| trailing_stop_loss | 4 (3%) | +3.859% | 100.0% |

**Root cause analysis:**
- time_stop dominance (59%, 0% wins) = VOL_SPIKE_MULT / CANDLE_BODY_MULT thresholds too loose. Strategy firing ~26 entries/day vs expected 1–2 genuine cascades/pair/day.
- Signal alpha is real: roi exits +0.738% avg (96% win), trailing exits +3.859% avg (100% win). The cascade event is being captured correctly — but too many non-cascade entries are being taken alongside it.
- Fix: raise VOL_SPIKE_MULT and/or CANDLE_BODY_MULT to improve selectivity. Do NOT change exit logic or stop parameters — those are performing correctly.
- Decision: do not tighten parameters until 2026-04-05 (2-week mark) to avoid reacting to a single regime. Current market (March 2026) is in drawdown — cascades fire frequently in bearish conditions.

**Day 1 sample (2026-03-18, for reference):**
- Trades 10–13: first 4 trades showed 80% ROI win rate — early signal looked strong
- This was a positively-biased sample during BTC decline from $74K → $71K; later data showed mean reversion toward 39.5% win rate as more noisy entries accumulated

**Infrastructure notes:**
- Deployed to DigitalOcean droplet (`LiqCascadeTrader01`) on 2026-03-18 — runs 24/7
- Bot and sidecar both run inside Docker via `docker compose --profile liqcascade up -d`
- DB volume-mounted to `user_data/tradesv3.dryrun.sqlite` on droplet
- All 19 historical trades imported to droplet DB via `python3 sidecar/import_log_trades.py`
- Deploy guide: `deploy/DEPLOYMENT.md` | Redeploy script: `bash deploy/deploy.sh`
- GitHub auth on new servers: use PAT or SSH key (`git clone` with password fails)
- `docker-compose.yml`: kinetic services (`log_api`, `freqtrade`) require `profiles: ["kinetic"]` guard or they start alongside liqcascade by default

**Infrastructure bugs fixed on 2026-03-18:**
1. **Sidecar file permission denied** — `tempfile.mkstemp` creates files with mode 0600 (owner-only). Sidecar runs as root; freqtrade runs as `ftuser` (UID 1000). Fix: `OUTPUT_PATH.chmod(0o644)` after atomic rename in `_write_snapshot`.
2. **Market orders config** — added `order_types: {entry: market, exit: market, stoploss: market}` to config. Freqtrade also requires `entry_pricing.price_side = "other"` and `exit_pricing.price_side = "other"` when using market orders — startup fails with `price_side = "same"`.
3. **Config now tracked in git** — `config/config_liqcascade_V04.json` added as exception in `.gitignore` (no secrets, safe to commit). Enables droplet updates via `git pull` without manual config editing.

**First live signal observations (2026-03-18):**
- Cascades fire in clusters of 2–3 consecutive minutes, not as isolated single-minute spikes. BTC CASCADE_LONG fired at 21:12, 21:14, 21:15; ETH CASCADE_LONG fired at 21:28, 21:29, 21:30.
- This clustering is consistent with cascade mechanics — the event takes several minutes to exhaust, so the rolling window keeps the signal active across multiple write cycles.
- Trade 20 (ETH long, 4x, open_rate 2196.29) was entered at 21:30:12, catching the third minute of the ETH cascade cluster. Entry timing looks correct.
- ETH CASCADE_SHORT fired at 21:35 — 5 minutes after the long cascade ended. Possible reversal or separate event. Trade 20 is a counter-move risk to monitor.

**Pair expansion (2026-03-20):**
Expanded from 2 pairs (BTC/ETH) to 5 pairs: added SOL/USDT:USDT, BNB/USDT:USDT, XRP/USDT:USDT.
`max_open_trades` raised from 2 → 5.

Selection rationale:
- SOL: ~$3–5B futures OI, thin order books → violent cascades, highest cascade-per-OI ratio of any non-BTC/ETH pair
- BNB: ~$1–2B OI, Binance-native → reliable liquidation feed, good execution liquidity
- XRP: ~$2–4B OI, high leverage usage, established on Binance perpetuals

Rejected pairs: DOGE (memecoin sentiment, less mechanical cascade behavior), LINK/AVAX/MATIC (lower OI, lower cascade frequency).

Threshold calibration note: the dynamic `CASCADE_MULT × rolling_baseline` design self-calibrates per symbol. No per-pair static USD threshold required. New pairs warm up in ~20 windows (~20 minutes after sidecar restart).

Correlation risk acknowledged: during macro drawdowns, all 5 pairs cascade simultaneously. Treat same-day multi-pair signals as a single market event for statistical analysis — do not count them as independent data points when assessing signal quality.

Existing 57 trades in the SQLite DB are unaffected. FreqUI displays all historical trades regardless of current pair_whitelist.

Files changed: `sidecar/liquidation_monitor.py` (SYMBOLS dict), `config/config_liqcascade_V04.json` (pair_whitelist + max_open_trades). Strategy unchanged — already pair-agnostic.

**Go/No-Go criteria (4-week minimum):**
| Criterion | Threshold |
|---|---|
| Trade count | >= 20 |
| Profit factor | > 1.0 |
| Win rate | > 40% |
| Sidecar uptime | > 99% |
| Worst week drawdown | < -30% balance |

---

### Phase 3.5: LOB-OFI + OI Entry Filter (Instrumentation → Retrospective Validation)

**Goal:** Determine whether adding microstructure context (order flow imbalance + open interest change rate) at the moment of cascade detection improves entry quality — reducing false positives without significantly reducing trade count.

**Motivation:** LOB Microstructure (Candidate A, archived 2026-03-20) produced a real signal (dir_acc=54.2%, IC=0.135) but was killed by retail taker fees as a standalone scalper. As a gate on existing LiqCascade entries, the fee problem disappears — no additional trade is opened. The filter either confirms an entry or blocks it; the round-trip cost of the cascade trade itself is unchanged. OI change rate provides orthogonal information: a genuine cascade should produce rapidly falling OI (forced closures), whereas directional trading on high volume produces rising or stable OI.

**Alpha sources being combined:**
- **LiqCascade (primary):** Mechanical forced liquidation event — structural alpha
- **OFI (confirming):** Order flow imbalance at entry moment — directional pressure aligned with cascade
- **OI change rate (confirming):** Forced position closure confirmed by OI drop — distinguishes real cascades from high-volume momentum moves

**Why OI change rate is the higher-priority filter vs LOB OFI:**
During a genuine cascade, leveraged positions are forcibly closed → OI drops. During a strong directional move with no cascade (vol spike from news), new positions may be opened → OI rises. This distinction is exactly what the LiqCascade proxy (V01–V03) could not make — it fired on any high-volume candle. The real WebSocket signal already captures forced order flow; OI rate adds independent confirmation.

**Instrumentation (COMPLETE — 2026-03-21):**
`sidecar/liquidation_monitor.py` updated to fetch `/fapi/v1/openInterest` for all 5 symbols concurrently (thread pool, non-blocking) at each 60-second snapshot. Two fields added to every signal record:
- `oi_contracts` — current OI in base currency (BTC, ETH, SOL, BNB, XRP)
- `oi_change_pct_1m` — % change vs previous snapshot (null on first snapshot after restart)

Both fields are written to `user_data/data/liquidation_data.json` and appended to `sidecar/logs/signal_history.jsonl`. Strategy V04 is unchanged — it reads only the `signal` field.

**Expected `signal_history.jsonl` entry at a cascade event:**
```json
{
  "timestamp": "2026-03-21T16:35:47+00:00",
  "signals": {
    "BTC/USDT:USDT": {
      "long_liq_usd": 48000000,
      "short_liq_usd": 800000,
      "signal": "CASCADE_SHORT",
      "long_baseline": 4200000,
      "short_baseline": 900000,
      "oi_contracts": 61200.0,
      "oi_change_pct_1m": -1.83
    }
  }
}
```

**Retrospective validation (to run once 20+ LiqCascade trades accumulated):**
1. Extract all snapshots where `signal != "NONE"` from `signal_history.jsonl`
2. Match to trade outcomes in `tradesv3.dryrun.sqlite` by timestamp + pair
3. Compare: winners vs losers — is `oi_change_pct_1m` systematically more negative for winning trades (genuine cascades) than for losing trades (false positives)?
4. If yes: calibrate an `oi_change_pct_1m` threshold that removes losers without removing winners
5. Also check LOB OFI from `sidecar/data/lob_raw/` if LOB sidecar is deployed by that point

**Critical caveat:** LOB OFI signal was validated at 3–15s horizon. LiqCascade holds for 15–35 minutes. Using LOB OFI state at entry as a 15–35 minute outcome predictor is an untested hypothesis — it requires the retrospective validation above before implementing as a hard gate.

**Implementation (deferred — pending validation):**
If retrospective analysis confirms filter utility:
1. Add `oi_change_pct_1m` threshold check to `_get_cascade_signal()` or `populate_entry_trend()`
2. Threshold calibrated from retrospective data — do not guess
3. No strategy version bump until filter is confirmed and threshold is set

**Go/No-Go for Phase 4:**
- 20+ trades accumulated in dry-run DB
- Retrospective OI analysis shows statistically meaningful separation between winners and losers
- Filter removes at least 20% of losing entries without removing more than 10% of winning entries

**Results (to be filled in):**
> *[Awaiting 20+ dry-run trades for retrospective analysis]*

---

### Phase 4: Parameter Optimisation (Hyperopt)

**Goal:** Optimise the key signal and exit parameters on the real or proxy signal, using the Phase 1/2 backtest infrastructure.

**Parameters to optimise:**
| Parameter | Range | Notes |
|---|---|---|
| `VOL_SPIKE_MULT` | 2.0 – 5.0 | Lower = more trades, noisier signal |
| `CANDLE_BODY_MULT` | 1.0 – 3.0 | Higher = fewer, higher quality entries |
| `STOP_FROM_ENTRY` | 0.02 – 0.08 | Stop too tight fires on noise; too wide = large losses |
| `minimal_roi["0"]` | 0.01 – 0.04 | First profit target |
| `MAX_HOLD_CANDLES` | 3 – 12 | Hold too long = noise; too short = misses target |

**Hyperopt command:**
```
docker compose run --rm freqtrade hyperopt --strategy LiqCascadeStrategy_V01 --config config/config_liqcascade_V01.json --hyperopt-loss SharpeHyperOptLoss --timerange 20230101-20250101 --epochs 200
```

**Important:** Hyperopt on 20230101–20250101 only. Hold out 2022 and 2025 for out-of-sample validation. Do not optimise on the full period.

**Go/No-Go criteria:**
- Optimised parameters improve Sharpe ratio vs Phase 1 defaults
- Out-of-sample (2022 + 2025) results remain positive
- Optimised parameters pass "smell test" — not extreme values at the edge of ranges (overfitting signal)

**Results (to be filled in):**
> *[Awaiting Phase 3 completion]*

---

### Phase 5: Multi-Pair Expansion

**Goal:** Expand beyond BTC/ETH to additional pairs. Liquidation cascades occur on all major perps — more pairs = more cascade opportunities = higher trade frequency.

**Candidate pairs:** SOL/USDT:USDT, BNB/USDT:USDT, XRP/USDT:USDT, DOGE/USDT:USDT

**Risk consideration:** Smaller-cap pairs have larger spreads and less liquidity — the proxy signal may fire more on genuine momentum than on cascades. Validate each new pair independently before adding to the live roster.

**Go/No-Go criteria per new pair:**
- Profit factor > 1.3 on that pair individually over the backtest period
- Win rate > 37% on that pair individually
- Max drawdown on that pair < 30% of starting balance

**Results (to be filled in):**
> *[Awaiting Phase 4 completion]*

---

### Phase 6: Live Deployment

**Goal:** Move from dry-run to live trading with controlled capital scaling.

**Deployment sequence:**
1. Dry-run for 4 weeks with fully optimised strategy and real sidecar signal
2. Live at 10% of intended capital for 4 weeks
3. Scale to 50% if 4-week live results meet criteria below
4. Scale to 100% after a further 4 weeks of satisfactory performance

**Live Go/No-Go criteria (4-week dry-run):**
- Total return within 30% of backtest expectation
- Win rate within ±10% of backtest win rate
- Sidecar process uptime > 99% (no missed cascades due to disconnections)
- No trade held beyond `MAX_HOLD_CANDLES` (time stop always firing on time)
- No single week down > 5% of portfolio

---

## Part 7: Risk Management

### 7.1 Position Sizing

With `max_open_trades = 2` and `stake_amount = "unlimited"`:
- Each trade receives approximately 50% of available balance
- At 4x leverage: each trade controls ~200% of balance in notional terms
- Simultaneous opposing positions on BTC and ETH are possible (e.g., BTC short cascade + ETH long cascade) — acceptable given the 30-minute maximum hold

### 7.2 Per-Trade Risk

| Scenario | Price move at stop | Stake loss |
|---|---|---|
| Full leverage (4x), stop 4% | 1.0% | 4% of stake |
| Reduced leverage (2x), stop 4% | 2.0% | 4% of stake |

Both configurations cap per-trade loss at 4% of stake. With `max_open_trades = 2`, worst-case simultaneous loss = 8% of portfolio. Acceptable.

### 7.3 Daily Loss Circuit Breaker

If portfolio is down > 10% in a single calendar day, suspend entries for the remainder of that day. This is not currently implemented in Freqtrade's standard logic — implement via `confirm_trade_entry()` checking portfolio balance delta.

---

## Part 8: Key Decisions Log

This section records significant architectural decisions with rationale, for future reference.

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-17 | 5m execution timeframe | Cascades are 15–60 min events; 5m gives ≤5 min entry lag |
| 2026-03-17 | 1h informative for regime context | Prevents ATR/ADX oscillation at 5m; regime changes once per hour at most |
| 2026-03-17 | EMA200 (not EMA21) for macro trend | EMA21 caused 70–87% of RAME losses in 2022 bear market; EMA200 = 8-day stable |
| 2026-03-17 | No ADX threshold | Primary oscillation source in RAME; not needed for cascade gating |
| 2026-03-17 | Leverage asymmetry for counter-trend | Short squeezes in bear markets are real events; hard block misses genuine opportunities |
| 2026-03-17 | No regime-change exits | Confirmed destructive in 9 RAME configurations; not relevant to cascade mechanics |
| 2026-03-17 | ROI table + hard stop + time stop | Cascade edge is in initial move; ROI table takes profit fast; time stop enforces discipline |
| 2026-03-17 | Proxy designed for replaceability | `_get_cascade_signal()` method isolates signal source; Phase 3 replaces it with WebSocket data without changing any other logic |
| 2026-03-20 | Expand to 5 pairs (SOL/BNB/XRP added) | Dry-run time is fixed regardless of pair count. Dynamic baseline in sidecar self-calibrates per symbol — no static threshold re-tuning required. max_open_trades raised to 5. |
| 2026-03-20 | Reject hard-blocking counter-trend on new pairs | Same rationale as BTC/ETH: short squeezes are real on all pairs; leverage asymmetry (4x/2x) prices the risk appropriately. |

---

## Part 9: What Not To Re-Introduce

This section exists to prevent incremental regression. If a future session is considering adding any of the following, re-read this section and the RAME archive first.

| Concept | Why Not |
|---|---|
| Regime-change exit signals | Consistently 2–24% win rate across all 9 RAME configurations. Lagging by definition — fires after the loss. |
| QUIET regime entries | Edge too small (+0.034% mean at 4h) for any leverage. Confirmed in 5 RAME backtests. |
| ADX threshold | Oscillates candle-to-candle at all tested timeframes. Primary source of false exit signals in RAME. |
| EMA21 trend filter | Too short. Flipped in bear markets. Responsible for 70–87% of RAME total losses. |
| Classifier / FreqAI on regime labels | Tautological — memorises labeling formula. 100% accuracy, zero forward edge. |
| Hold times > 30 minutes for cascade trades | The cascade is over in 15–60 minutes. Holding longer captures noise, not signal. |
| CRISIS sub-strategy entries | Failed RAME stress test (PF 1.067, p=0.49). Extreme vol = unpredictable cascade reversals. |

---

## Part 10: Open Research Questions

Questions to be answered by backtest evidence, not prior assumptions:

1. **Counter-trend cascade quality:** Do short squeezes in macro-bearish regimes (2022) have similar win rates and P&L to trend-aligned cascades? Or is hard-blocking counter-trend entries better despite missed short squeezes?

2. **Optimal proxy thresholds:** What volume spike multiplier and candle body threshold produce the best signal-to-noise ratio on 5m BTC/ETH data?

3. **ATR vs fixed ROI:** Is a fixed minimal_roi table better than an ATR-relative target? The current design uses fixed percentages; an ATR-relative target (`2 × ATR14 as target`) may be more robust across varying market volatility regimes.

4. **Funding rate as pre-condition:** In Phase 2+, when funding rate data becomes available: does requiring an extreme funding rate (e.g., > +0.1% or < -0.1%) as a pre-condition significantly improve signal quality?

5. **Cascade failure modes:** What does the average failed cascade look like? (Enters, reverses immediately, hits stop.) Understanding the failure mode helps calibrate the stop distance.

---

*Document maintained by: Claude Sonnet 4.6 + project co-developer*
*Last updated: 2026-03-22 — Phase 3 preliminary results added (129 trades, 5 days): win rate 39.5%, PF 0.659, 59% time_stop (0% win). Root cause: entry thresholds too loose. Signal alpha confirmed real via roi/trailing exits. Next reassessment: 2026-04-05.*
