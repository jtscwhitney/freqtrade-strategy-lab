# Path Signatures / Lead-Lag (Candidate E) — Deep Dive
## Version 1 | Started: 2026-03-23 | Status: ARCHIVED — Backtest FAIL (2026-03-23)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**  
> Use with `AlgoTrading_Research_Log.md` for registry context.

### Current Status
- **Phase:** ARCHIVED — implementation + backtest **FAIL** (2026-03-23)
- **Reason:** Long-sample Binance futures backtests on `PathSignatureLeadLag_V01` showed **large negative total return** and **profit factor &lt; 1**, dominated by **stop_loss** exits while smaller gains came from **exit_signal** / **time_stop**. The theoretical lead–lag / signature story did not translate into a profitable rule set at 1h with this MVP parameterization.
- **Next step:** Do **not** forward-test this build. **Candidate G** (Cross-Sectional Momentum) remains the recommended next build per the Research Log. **Candidate I** (signature-enhanced momentum) is **deferred** until a viable signature or ranking layer is demonstrated independently.

### Key Commands
```
# Build lab image (extends freqtradeorg/freqtrade:stable + iisignature)
docker compose build freqtrade

# Full-range data (adjust end date to run day). VPN may be required if Binance returns 451.
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_pathsignatures_V01.json --timerange 20220101-20260323 --timeframes 1h --erase

# Backtest (same timerange as data)
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_pathsignatures_V01.json --strategy PathSignatureLeadLag_V01 --timerange 20220101-20260323 --cache none
```

### File Locations
| File | Status | Purpose |
|---|---|---|
| `user_data/strategies/PathSignatureLeadLag_V01.py` | ARCHIVED | Hub BTC → followers ETH/SOL; depth-2 Lévy antisymmetry score (numpy Chen integrals; same piecewise-linear math as `iisignature` at depth 2) |
| `config/config_pathsignatures_V01.json` | ACTIVE template | Futures, StaticPairList, **no FreqAI block** (omit `freqai` entirely — a minimal `{ "enabled": false }` block fails schema validation in 2026.2) |
| `Dockerfile.freqtrade` | ACTIVE | `FROM freqtradeorg/freqtrade:stable` + `iisignature==0.24` (numpy + setuptools + `--no-build-isolation`) |
| `docker-compose.yml` | ACTIVE | Builds from `Dockerfile.freqtrade` |
| `docker-compose.pathsignatures.yml` | OPTIONAL | Overrides `command` to Path Signatures strategy + separate sqlite/log paths |
| `user_data/scripts/generate_synthetic_ohlcv_pathsig_smoke.py` | OPTIONAL | Synthetic feather OHLCV when `download-data` is blocked (e.g. geo-restriction) |
| `user_data/info/PathSignatureLeadLag_Deep_Dive.md` | THIS FILE | Authoritative reference |
| `user_data/info/AlgoTrading_Research_Log.md` | Active | Candidate E archived in Section 4.1 |

---

## Part 1: Research Context (Candidate E)

### 1.1 Idea
- **Rough paths / signatures:** Summarize multi-asset price paths (e.g. log prices) and use **cross-terms** (Lévy-area / antisymmetric part of the level-2 signature) as a **lead–lag** proxy between a **leader** (BTC/USDT:USDT) and **followers** (e.g. ETH, SOL).
- **Literature (see Research Log):** Gyurkó et al.; Futter et al. “Signature Trading”; Rahimi lead-lag portfolios; segmented signatures (2025).

### 1.2 MVP implementation (V01)
- **Hub-and-spoke:** One leader pair; do **not** open trades on the leader row (BTC has no follower informative above it in this design).
- **Score:** For each candle, on a rolling window of **48** 1h bars, build increments of log BTC and log follower; compute **S^{1,2} − S^{2,1}** via Chen iterated sums, **normalized** by `std(dx)*std(dy)*window`.
- **Direction:** Leader cumulative return over **4** hours must exceed **3 bps** in the trade direction.
- **Entries:** Long follower if score &gt; `ENTRY_SCORE` (0.08) and leader up; short if score &lt; −0.08 and leader down.
- **Exits:** Long exits when score &lt; `EXIT_SCORE` (0.02); short when score &gt; −0.02; **time_stop** at 72h; **stoploss** −12%.

### 1.3 What we did **not** ship
- Dedicated **fee economics sweep** (Technique 7.3) as a separate script.
- **Walk-forward** train/test splits.
- **`iisignature` inside the strategy:** Docker image includes the library for optional checks; runtime signal uses **numpy** for depth-2 cross-terms.

---

## Part 2: Architecture (Hub-and-Spoke)

```
Leader: BTC/USDT:USDT (informative for every non-BTC pair)
Followers: ETH/USDT:USDT, SOL/USDT:USDT (executed)
```

`informative_pairs()` returns BTC at the strategy timeframe; `merge_informative_pair` + `get_pair_dataframe` align leader closes. Indicator column: `btc_close_1h` (when `timeframe == "1h"`).

---

## Part 3: Backtest Results (Authoritative Long Run)

**Environment:** Freqtrade **2026.2**, Binance **USDT-M futures**, **isolated**, **dry_run** wallet 1000 USDT, **max_open_trades 3**, fee from exchange **~0.05% / side** (worst tier in log). **Timerange:** `20220101`–`20260323` (data **erase** + full re-download). **Backtest effective:** 2022-01-06 → 2026-03-23 (startup 120 candles).

| Metric | Value |
|---|---|
| Total trades | 3354 |
| Total profit % | ~**−98.8%** |
| Profit factor | ~**0.89** |
| Max drawdown | ~**99.2%** |
| Stop_loss exits | 315 (avg ~−12.3% on those trades) |
| exit_signal exits | 2953 (aggregate positive $ contribution in report) |
| time_stop exits | 85 |

**Pairs:** BTC **0** trades (by design). ETH and SOL traded heavily; SOL contributed most of the dollar loss in the summary table.

**Interpretation:** The MVP is **not** viable as-is. The dominant failure mode is **fixed stoploss** hitting on **directional follower** bets that move against the position — not a small “edge minus fees” problem. Any revival needs **different risk** (tighter structural thesis, different horizons, regime filter, or non-directional / hedged construction closer to literature’s market-neutral portfolios).

---

## Part 4: Operational Notes

### 4.1 Binance geo-restriction (451)
If `download-data` fails with HTTP **451**, requests are blocked by **region**. Use a **VPN** to an eligible region or run download on a **VPS** where Binance API is available.

### 4.2 `freqai` in config
Do **not** add `"freqai": { "enabled": false }` alone — Freqtrade 2026.2 still validates required nested keys. **Omit** the `freqai` key entirely for non-FreqAI strategies.

### 4.3 Docker image build (`iisignature`)
`iisignature` may build from source; the Dockerfile installs **build-essential**, **numpy**, **setuptools**, then `pip install --no-build-isolation iisignature==0.24`.

---

## Part 5: Deployment (DigitalOcean)

Not executed for this candidate (backtest failure). When a **future** strategy passes backtests, use the same pattern as other repos: Ubuntu LTS, Docker + Compose, mount `user_data` + `config`, **no API keys in git**, restrict firewall if exposing API port. See [`deploy/digitalocean.md`](../../deploy/digitalocean.md) in this repo.

---

## Part 6: Conversation & Decision Record

- **2026-03-23:** Plan executed: strategy + config + Docker + compose override; data downloaded (VPN after 451); backtests run for **2022–2024**, **2022–2025**, and **2022–2026-03-23** with clean `--erase` where requested.
- **Decision:** Archive **Candidate E** as a standalone directional MVP; **no forward test** on this build. **Next registry focus:** **Candidate G** (and **Candidate I** deferred as signature layer until a new validated approach exists).

---

## Changelog

| Date | Change |
|---|---|
| 2026-03-23 | v1 — Deep Dive created. Status ARCHIVED. Full-range backtest results recorded. |
