# Enhanced Cointegration Pairs Trading (Candidate L) — Deep Dive
## Version 1 | Started: 2026-03-31 | Status: Phase 1 lab complete — forward-test deploy ACTIVE

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**  
> Use with `AlgoTrading_Research_Log.md` (registry), `EnhancedCointPairs_Dev_Plan.md` (roadmap + commands), and — for production — `freqtrade-coint-pairs-trading` (deploy repo).

### Current Status
- **Lab (`freqtrade-strategy-lab`):** Dual-leg **EnhancedCointPairsStrategy_V01** / **V02** @ **4h**; Phase 0 matrix → **4h** produced multiple **GO** pairs; primary backtest focus **BTC/ETH**. Walk-forward CSVs and comparison tables under `user_data/results/`. Palazzi **vol filter** + **spread trailing** exist as flags (`ENABLE_VOL_FILTER`, `ENABLE_SPREAD_TRAIL`) default **off** — lab showed they **reduced** net P&L vs z-reversion + time stop on the tested pair/TF.
- **Deploy (`freqtrade-coint-pairs-trading`):** Standalone repo on **whitneyjohn61** — **six** Freqtrade processes: **three spreads** (BTC/ETH, BNB/SOL, BTC/SOL) × **V01** (compose profile `v01`) on one DigitalOcean droplet and **V02** (`v02`) on a second. `dry_run` default true in templates; see repo `README.md` and `deploy/README.md`.
- **Versus archived Candidate F:** F failed on **single-leg** exposure and **~0.05 trades/day** on the only GO pair. L is **dual-leg**, **β-weighted stakes**, with **orphan-leg** safeguards; literature layer adds adaptive trailing + vol filter (optional in code).

### Key Commands (lab — Docker)

```
# Walk-forward (defaults; adjust strategy name for V02)
docker compose run --rm --entrypoint python freqtrade user_data/scripts/cointpairs_walk_forward.py

# Example backtest (BTC/ETH Phase 1 config)
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_cointpairs_l_phase1.json --strategy EnhancedCointPairsStrategy_V01 --timerange 20220101-20260331 --cache none
```

### File Locations

| File | Repo | Purpose |
|------|------|---------|
| `user_data/info/EnhancedCointPairs_Deep_Dive.md` | **Lab** (canonical) | THIS FILE — narrative + results summary |
| `user_data/info/EnhancedCointPairs_Deep_Dive.md` | **Deploy** (mirror) | Same content for operators cloning deploy repo only |
| `user_data/info/EnhancedCointPairs_Dev_Plan.md` | Lab | Development plan, Quick-Start, Part 6 deploy topology |
| `user_data/info/CointPairsTrading_Deep_Dive.md` | Lab | Archived **F** — single-leg failure modes |
| `user_data/results/cointpairs_comparison_tables.md` | Lab | Aggregated V01/V02/hyperopt/churn tables |
| `user_data/strategies/EnhancedCointPairsStrategy_V01.py` | Lab | Strategy source (may differ slightly from deploy V01 if deploy adds config-driven pairs) |
| `user_data/strategies/EnhancedCointPairsStrategy_V02.py` | Lab | V01 + β-churn filter |
| `freqtrade-coint-pairs-trading/` | Deploy | `docker-compose.yml`, `config/templates/`, strategies, `deploy/README.md` |

---

## Part 1: Research Context (Candidate L)

### 1.1 Registry summary (from `AlgoTrading_Research_Log.md`)

- **Sweep #4 (2026-03-31):** L surfaced with **J** (Ensemble Donchian) and **K** (MTF filter). **J** promoted to #1 build priority; **L** held as **second-priority** — concurrent diversification vs J, not formally scored 7/7.
- **Sources:** Palazzi (*Journal of Futures Markets*, Aug 2025) — adaptive trailing stop + vol filter + grid-search lookbacks + walk-forward; Tadi & Witzany (*Financial Innovation*, 2025) — copula pairs on **Binance USDT-M**; IEEE-style finding that **higher frequency** pairs trading dominates daily.
- **Why L for this lab:** Reuses **`cointpairs_phase0_validation.py` (v4)**; addresses **F**’s structural failures (dual-leg; target higher frequency via universe + TF choices).
- **Stated risks in log:** Dual-leg coordination in Freqtrade (same conditional concern as F §3); capital intensity; Palazzi uses **daily** — we validated on **4h** after Phase 0; execution/slippage at very high frequency not attempted in MVP.

### 1.2 Relationship to archived Candidate F

| Topic | F (archived) | L |
|-------|----------------|-----|
| Legs | Single-leg (ETH-only Phase 1) | **Dual-leg** long/short per spread side |
| Stoploss story | Fixed % failed | Structural stop at -99% ROE; exits via **z**, **time stop**, optional **spread trail** |
| Pair count | Effectively one GO @ 4h | Phase 0 screened many pairs; lab + deploy use **GO**-backed spreads |
| Evidence | Hurst ~0.25, fee sweep without stop | Same diagnostics reusable; L adds **paired** P&L |

Full F post-mortem: `user_data/info/CointPairsTrading_Deep_Dive.md`.

---

## Part 2: Strategy & Lab Implementation

### 2.1 Core mechanics

1. **Spread:** \(S_t = \log P_Y - \beta \log P_X\) with **rolling OLS** hedge ratio \(\beta\) (`ols_window`).
2. **Z-score:** Rolling mean/std of \(S\) over `zscore_window`.
3. **Entries:** \(\lvert z\rvert >\) `entry_zscore` — dual-leg: short rich leg / long cheap leg per sign.
4. **Exits:** Reversion to `exit_zscore` band, **`max_hold_candles`**, optional Palazzi **spread trailing** and **vol filter** (defaults **false** in lab).
5. **V02:** **β-churn** gate — skip entries when rolling mean \(\lvert\Delta\beta\rvert\) exceeds `beta_churn_max` over `beta_churn_window` (hyperoptable `buy` space).

### 2.2 Engineering: dual-leg in Freqtrade

- `informative_pairs` loads both legs; `merge_informative_pair` aligns prices.
- `confirm_trade_entry` / `custom_exit` / orphan watchdog (`ORPHAN_MAX_CANDLES`) enforce **paired** behavior (see dev plan §1.4).

### 2.3 Timeframe and pair selection

- **Implemented TF:** **4h** (Phase 0 showed **1h** matrix marginal; **4h** multiple GO — aligns dev plan “Primary Phase 1 pair: BTC/ETH @ 4h”).
- **Deploy spreads:** BTC/ETH, BNB/SOL, BTC/SOL — each **one process** (`cointpairs.traded` / `cointpairs.anchor` + whitelist), not multi-pair in one process.

---

## Part 3: Lab Backtest Results (Summary)

**Authoritative tables:** `user_data/results/cointpairs_comparison_tables.md` (sourced from walk-forward CSVs).

**Headline (BTC/ETH @ 4h, defaults, full sample 20220101–20260331):**

| Variant | Total % (approx.) | Notes |
|---------|-------------------|--------|
| **V01 default** | **~25.7%** | Baseline |
| **V02 default** (β-churn) | **~27.7%** | Improves full sample vs V01; **2023** flips positive; **2022** weaker than V01 — explicit trade-off |
| **V01 hyperopt** (in-sample JSON) | **~−4.3%** full sample | **Not robust** OOS — dev plan warns against global use of sidecar |

**β-churn sweep:** See comparison tables §2; tightening churn can change 2024 vs 2025–26 behavior — interpret before changing production defaults.

**OOS note:** Dev plan records short OOS sanity window positive but **below** in-sample hype — treat hyperopt as exploratory.

---

## Part 4: Deploy Repository (`freqtrade-coint-pairs-trading`)

### 4.1 Why a separate repo

- **Lab** carries research, sweeps, FreqAI/other strategies, large `user_data/results/`.
- **Deploy** ships **only** what is needed to run **Candidate L** forward tests: `freqtradeorg/freqtrade:stable`, strategies, config **templates**, secrets generation, DigitalOcean-oriented scripts.

**Remote:** `https://github.com/whitneyjohn61/freqtrade-coint-pairs-trading`

### 4.2 Topology (implemented)

| Droplet | Compose profile | Strategies | Host UI ports (→ container 8080) |
|---------|-----------------|------------|----------------------------------|
| **A** | `v01` | V01 | **8080** BTC/ETH, **8081** BNB/SOL, **8082** BTC/SOL |
| **B** | `v02` | V02 | **8083** BTC/ETH, **8084** BNB/SOL, **8085** BTC/SOL |

- **Six** services in `docker-compose.yml`: separate **SQLite DB** and **log file** per service.
- **V01** in deploy reads **`config["cointpairs"]`** (not hardcoded BTC/ETH only) so three JSON configs can differ by spread.

### 4.3 Configs (generated, not committed with secrets)

- `config_cointpairs_l_phase1.json` — BTC / ETH  
- `config_cointpairs_l_phase1_bnb_sol.json` — BNB / SOL  
- `config_cointpairs_l_phase1_btc_sol.json` — BTC / SOL  

Templates under `config/templates/`; `scripts/generate_api_secrets.py` for JWT/UI password.

### 4.4 Operations

- **`README.md`** — quick start, profiles, ports.  
- **`deploy/README.md`** — firewall, `droplet_setup_from_local.ps1`, `droplet_setup.sh`, **`droplet_status_from_local.ps1`** (both droplets: docker, logs, trades).  
- **`scripts/local.env.example`** — `FT_V01_HOST`, `FT_V02_HOST`, etc.

---

## Part 5: Risks, Limitations, and Monitoring

| Risk | Mitigation |
|------|------------|
| **Orphan leg** | Strategy orphan timeout + **watch logs** first 48h on any new deploy |
| **Hyperopt overfit** | Do not promote in-sample JSON to global defaults without window-matched validation |
| **Multi-spread correlation** | Three bots may stress margin — size droplets and leverage consciously |
| **β-churn / regime** | V02 improves some years, weakens others — forward-test compares V01 vs V02 on live fills |
| **Research log daily vs our 4h** | Palazzi validation is not automatically transferable — we rely on Phase 0 + walk-forward |

---

## Part 6: Conversation & Decision Record

### 6.1 From project chat history (abridged)

- **Repo creation:** **`freqtrade-coint-pairs-trading`** created under **whitneyjohn61** (standalone from `jtscwhitney/freqtrade-strategy-lab`) for **two** forward-test surfaces: **V01 droplet** vs **V02 droplet**, parallel to other DO workloads.
- **One pair per process:** Confirmed — running multiple spreads **requires** multiple Freqtrade processes (multiple configs/DBs/ports), not one process with many pairs without refactor.
- **Evolution to three spreads:** Started with BTC/ETH + BNB/SOL; **BTC/SOL** added for Phase 0 **GO** @ 4h — **six** compose services, **three** UI ports per droplet (**8080–8082** / **8083–8085**).
- **Lab push / auth:** Early push to `jtscwhitney/freqtrade-strategy-lab` required correct GitHub identity; artifacts commit **`61123a0`** eventually reached origin.
- **Documentation:** **`EnhancedCointPairs_Dev_Plan.md`** updated with **Part 6** deploy topology; mirrored under deploy repo `user_data/info/`.

### 6.2 Decisions reflected in code

- **Deploy V01** uses **config-driven** `cointpairs` (align with V02) for three spreads.
- **Palazzi options** default **off** in backtest where they hurt net P&L — optional for live risk experiments.
- **V02** β-churn **on** by default (`ENABLE_BETA_STAB_FILTER`) in strategy class.

---

## Part 7: Related Documents

| Document | Use |
|----------|-----|
| `EnhancedCointPairs_Dev_Plan.md` | Commands, phase gates, file index, deploy Part 6 |
| `AlgoTrading_Research_Log.md` | Candidate L registry, priority vs J/G |
| `CointPairsTrading_Deep_Dive.md` | Predecessor F — what not to repeat |
| `user_data/results/cointpairs_comparison_tables.md` | Numeric backtest recap |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-02 | v1 — Deep dive created: research log, dev plan, deploy repo, lab results summary, chat-derived decision notes. |
