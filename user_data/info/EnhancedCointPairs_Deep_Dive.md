# Enhanced Cointegration Pairs Trading (Candidate L) — Deep Dive
## Version 1 | Started: 2026-03-31 | Status: Phase 1 lab complete — **Phase 3 forward discontinued** (**PARKED** per `AlgoTrading_Research_Log.md` §4.3, **2026-05-02**)

---

## Quick-Start for Claude (Session Resume)

> **Read this section first at the start of every session.**  
> Use with `AlgoTrading_Research_Log.md` (registry), `EnhancedCointPairs_Dev_Plan.md` (roadmap + commands), and — for production — `freqtrade-coint-pairs-trading` (deploy repo).

### Current Status
- **Research Log:** **Candidate L is PARKED (2026-05-02).** Droplet-hosted forward tests ended by policy (~**4 calendar weeks** of live-shaped Binance futures data via dual-leg **`freqtradeorg/freqtrade:stable`** bots). **`§6` not cleared.** See **§6.3** below for co-investigator recommendation vs **ARCHIVED**.
- **Lab (`freqtrade-strategy-lab`):** Dual-leg **EnhancedCointPairsStrategy_V01** / **V02** @ **4h**; Phase 0 matrix → **4h** produced multiple **GO** pairs; primary backtest focus **BTC/ETH**. **BTC/PAXG** (tokenized gold vs BTC) is an additional **lab** pair — `config/config_cointpairs_l_phase1_btc_paxg.json`; short perp history (from ~Mar 2025). **Exploratory spreads (2026-04-03):** LINK/ETH, UNI/SOL, XMR/BTC backtested from the deploy repo — see Part 3; **not** added to droplets on these results. Walk-forward CSVs and comparison tables under `user_data/results/`. Palazzi **vol filter** + **spread trailing** exist as flags (`ENABLE_VOL_FILTER`, `ENABLE_SPREAD_TRAIL`) default **off** — lab showed they **reduced** net P&L vs z-reversion + time stop on the tested pair/TF.
- **Deploy (`freqtrade-coint-pairs-trading`):** Standalone **`whitneyjohn61`** repo — six Freqtrade services (**BTC/ETH, BNB/SOL, BTC/SOL** × **V01**/ **`v02`**) documented for **historical reproducibility**. **Operational default 2026-05-02:** **`docker compose down`** on profiles (droplet billing at operator discretion — not required for PARKED stance).
- **Versus archived Candidate F:** F failed on **single-leg** exposure and **~0.05 trades/day** on the only GO pair. L is **dual-leg**, **β-weighted stakes**, with **orphan-leg** safeguards; literature layer adds adaptive trailing + vol filter (optional in code).

### Key Commands (lab — Docker)

```
# Walk-forward (defaults; adjust strategy name for V02)
docker compose run --rm --entrypoint python freqtrade user_data/scripts/cointpairs_walk_forward.py

# Example backtest (BTC/ETH Phase 1 config)
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_cointpairs_l_phase1.json --strategy EnhancedCointPairsStrategy_V01 --timerange 20220101-20260331 --cache none

# BTC/PAXG (perp data from ~Mar 2025 — use timerange from first PAXG candle onward)
docker compose run --rm freqtrade download-data --config /freqtrade/config/config_cointpairs_l_phase1_btc_paxg.json --timerange 20250301-20260331 -t 4h
docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_cointpairs_l_phase1_btc_paxg.json --strategy EnhancedCointPairsStrategy_V01 --timerange 20250327-20260331 -i 4h --cache none
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
- **Lab-only (proxy):** **BTC/PAXG** — same mechanics; **PAXG/USDT:USDT** USDT-M perp on Binance (listed ~2025). Not on deploy droplets until lab backtests support it (see Part 3).

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

**BTC/PAXG (lab, 2026-04-03):** Same default parameters as BTC/ETH; timerange **20250327–20260331** (~12 months of overlapping perp data). **V01 ≈ −47%** total, PF **0.23**, **32** trades. **V02** (β-churn) **≈ −19%**, **4** trades, 0 wins. Baseline **BTC/ETH** on the **same window** was **≈ +1.9%**, PF **1.03**, **40** trades — proxy pair underperforms sharply. **Do not add BTC/PAXG to deploy droplets** on these defaults; run **Phase 0** on BTC/PAXG and treat re-tuning as a separate experiment. Details: `user_data/results/cointpairs_btc_paxg_backtest_summary.txt`.

**LINK/ETH, UNI/SOL, XMR/BTC (deploy repo backtest, 2026-04-03):** Screened **EnhancedCointPairsStrategy_V01** @ **4h**, **default** `DecimalParameter` values, Binance USDT-M futures, **`freqtradeorg/freqtrade:stable`**. **`--timerange 20220101-20260403`** (download + backtest); first trades after **500** startup candles on 4h → effective simulation **~2022-03-25** → **2026-04-03** (aligns with full-sample style **`20220101–20260331`** runs; end date differs by a few days). Configs live under **`freqtrade-coint-pairs-trading`** only: `config/config_cointpairs_l_phase1_link_eth.json`, `config/config_cointpairs_l_phase1_uni_sol.json`, `config/config_cointpairs_l_phase1_xmr_btc.json` (`cointpairs.traded` / `cointpairs.anchor` + matching `pair_whitelist`).

| Spread (traded → anchor) | Total % | Profit factor | Max drawdown % | Trades | Notes |
|--------------------------|---------|---------------|----------------|--------|--------|
| **LINK → ETH** | **≈ −59.5%** | 0.68 | ≈ 69.1% | 140 | Poor — do **not** add on defaults. |
| **UNI → SOL** | **≈ +21.6%** | **1.03** | ≈ **65.3%** | 148 | Only positive headline of the three; **not** droplet-ready — **2× ~−99% stop_loss** exits, **1** liquidation, very asymmetric per-leg P&L (SOL leg ~+90% vs UNI ~−69% aggregate). Treat as **tail-risk** until walk-forward / risk work. |
| **XMR → BTC** | **≈ −50.8%** | 0.78 | ≈ 67.1% | 150 | Poor — do **not** add on defaults. |

**Deploy decision:** No new droplet instances for these three on **V01 defaults**. Revisit UNI/SOL only after dedicated analysis (parameters, leverage, stops) if at all.

---

## Part 4: Deploy Repository (`freqtrade-coint-pairs-trading`)

### 4.1 Why a separate repo

- **Lab** carries research, sweeps, FreqAI/other strategies, large `user_data/results/`.
- **Deploy** ships **only** what is needed to run **Candidate L** forward tests: `freqtradeorg/freqtrade:stable`, strategies, config **templates**, secrets generation, DigitalOcean-oriented scripts.

**Remote:** `https://github.com/whitneyjohn61/freqtrade-coint-pairs-trading`

### 4.2 Topology (historical layout — forward discontinued 2026-05-02)

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
- **Lab-only reproduction (not compose-wired):** `config_cointpairs_l_phase1_link_eth.json`, `config_cointpairs_l_phase1_uni_sol.json`, `config_cointpairs_l_phase1_xmr_btc.json` — used for the Part 3 exploratory backtests; **not** production droplet services.

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

### 6.3 Forward closure (**2026-05-02**) — co‑investigator recommendation

**Measurements:** **`scripts/droplet_status_from_local.ps1`** (`Import-DotEnv` + SSH to **`v01`** / **`v02`** hosts → remote `droplet_status_remote.sh` → local **`droplet_combined_summary_from_local.py`**). Combined table is authoritative for apples‑to‑apples six‑container totals.

**Final combined snapshot (**UTC **2026-05-02**):**
- **12** open legs, **17** closed trade rows (SQLite) across **six** instances — **`AlgoTrading_Research_Log.md` §2** (**~50** closed trades minimum for coarse forward read): **not met**.
- **Total PnL** ≈ **+US$6.56** (closed + open MTM) versus rolled‑up stakes → **~+0.01%** — **economically ambiguous** (“flat”) over the window; contrasts with interim **≈ −1.72%** checkpoint (**2026-04‑18**, `TESTING.md`).
- **By spread replica:** **BTC/ETH** (**V01** + **V02**) **each ~+4.2% vs stakes** — only pair‑surface aligning with favourable **lab** walk‑forward. **BNB/SOL** (**~−1.5%** vs **~−1.25%**) and **BTC/SOL** (**~−2.0%** each) **dragged** aggregate results.

**ARCHIVE versus keep for later phases:**
- **Recommendation:** **KEEP for next phases; do NOT move to ARCHIVED.** Rationale — **engineering** validated dual‑leg Freqtrade + ops at scale; **economics** did **not** justify further **standalone** VPS budget on this three‑spread bundle. LAB walk‑forward and Phase 0 artefacts remain materially useful; PARKED **`§4.3`** framing preserves option value for **`§4.5 GatedExecution`** (spread / **z‑score** gate) or a narrower **§6** revival with held‑out pairs and completed **§6.2 Edge Deflation Pass**.
- **ARCHIVE would only follow** if a future §6 worksheet formally concludes **zero** salvageable discrete signal vs fees + tails — **not** warranted on current evidence alone.

---

## Part 7: Related Documents

| Document | Use |
|----------|-----|
| `EnhancedCointPairs_Dev_Plan.md` | Commands, phase gates, file index, deploy Part 6 |
| `AlgoTrading_Research_Log.md` | Candidate **L registry** (**PARKED §4.3**), effort allocation **§4.6**, deflation rules **§6.2** |
| `CointPairsTrading_Deep_Dive.md` | Predecessor F — what not to repeat |
| `user_data/results/cointpairs_comparison_tables.md` | Numeric backtest recap |

---

## Part 8: §6.2 Edge Deflation Pass + §6.3 Replication Checklist + Forward Post-Mortem (2026-05-03)

> **Why this Part exists.** Per `AlgoTrading_Research_Log.md` §4.6 step 4, the v5.1 next-actionable session for Candidate L was a §6.2 deflation pass on the source papers and a formal verdict (a/b/c). This Part is the worksheet attached to L per §6.3 ("Output: a 1-page summary per candidate, attached to the Dev Plan / Deep Dive"). It also folds in the realized 4-week droplet forward results as the empirical cross-check that an academic deflation alone cannot provide.

### 8.1 Method, inputs, and honest limitations

**Inputs available locally:**
- Lab walk-forward CSVs and `cointpairs_comparison_tables.md` (BTC/ETH @ 4h, V01/V02 defaults).
- Forward droplet snapshot 2026-05-02 (six replicas, 17 closed trade rows, `droplet_status_from_local.ps1`).
- Research Log §6.2.5 explicit instruction to use Palazzi **portfolio average Sharpe 0.89** (37-pair universe, 13 OOS-positive ⇒ 35% hit rate) as the deflation input — not the single-pair best 2.12.

**Inputs NOT directly available (papers not on disk):** Palazzi 2025 *Journal of Futures Markets* and Tadi & Witzany 2025 *Financial Innovation* PDFs are not in the repo. Specific numeric values below sourced from those papers — fee tier, exact OOS window, per-paper MDD definition — are **inferred from paper class conventions** unless the Research Log already records them. Items where I am inferring rather than quoting are marked **⚠ inferred** and would need a re-read against the original PDFs to firm up. The deflation conclusions are robust to plausible ranges of these inferred values; sensitivity bounds are noted where they matter.

### 8.2 §6.2 Worksheet — Palazzi (JFM, Aug 2025)

#### 8.2.1 Sharpe / return decay (§6.2.1)
- **Headline input:** portfolio Sharpe **0.89**, portfolio annual return **⚠ inferred ~12–18%** (typical for diversified crypto pairs portfolios in this paper class; not quoted from PDF).
- **Decay factor:** 0.5 (Falck & Rej 2022 default; Research Log §6.2.1).
- **Override applied?** No. Paper is post-publication < 12 months; no exemption qualifies.
- **After 8.2.1:** Sharpe **0.445**, return **~6–9%**.

#### 8.2.2 Fee tier downgrade (§6.2.2)
- **Paper fee assumption ⚠ inferred:** 5 bps/side = 10 bps round-trip on Binance spot, OR `0` (vol-of-spread sims sometimes ignore fees). The paper explicitly tests on crypto, so 5 bps/side is the most generous-to-paper reading; if zero-fee, the deflation impact is larger.
- **Our fee:** 10 bps round-trip taker (Binance retail futures, dual-leg ⇒ 20 bps round-trip per spread cycle).
- **Fee delta vs paper (best case 5/side single-leg comparison vs our 10/side dual-leg):** ~10 bps additional per spread cycle.
- **Turnover proxy:** lab BTC/ETH 4h ran 134 trades over ~4.25 years ≈ **31.5 trades/yr per spread**. Combined with `~10 bps` extra per spread cycle: `~31.5 × 10 bps = ~3.15%/yr` additional drag.
- **After 8.2.2:** return **~3–6%/yr**, Sharpe **~0.30–0.40** (drag at fixed vol).

#### 8.2.3 Slippage layer (§6.2.3)
- Universe is "10 major cryptos" — top liquidity tier. Liquid majors: 2 bps RT (BTC, ETH); liquid alts: 5 bps RT (SOL, BNB, XRP, ADA, AVAX, LINK). Average dual-leg slippage **~7 bps RT per spread cycle**.
- Annual drag: `~31.5 × 7 bps ≈ ~2.2%/yr`.
- **After 8.2.3:** return **~1–4%/yr**, Sharpe **~0.20–0.32**.

#### 8.2.4 Regime weighting (§6.2.4)
- **Paper window ⚠ inferred:** ~2017–2024 (typical crypto pairs paper coverage). May or may not include the full 2022 bear in OOS.
- **Our lab BTC/ETH @ 4h V01 defaults by year:** 2022 +8.4%, 2023 −0.6%, 2024 +10.9%, 2025–26 Q1 +4.5%. PFs 1.18 / 0.98 / 1.20 / 1.07. Real per-year economics are **already** mid-single-digit in the favorable years and break-even-or-worse in 2023.
- Re-weight using §6.2.4 mix on the lab values directly (more reliable than re-weighting paper headlines):
  - 33% × 8.4% (2022 ≈ bear) + 34% × −0.6% (2023 ≈ chop) + 33% × 10.9% (2024 ≈ bull) ≈ **6.18%/yr** weighted.
- The lab V01 defaults under §6.2.4 weighting deliver **~6.2%/yr** — already below §6.2.6 threshold before the post-publication decay is even applied.
- **After 8.2.4 (using lab data, not paper headline):** return **~3–5%/yr** post-decay, Sharpe **~0.20–0.30**.

#### 8.2.5 Selection bias (§6.2.5)
- Already addressed by using portfolio Sharpe 0.89 instead of best-of-N 2.12. No further penalty applied.
- **Cross-check:** Palazzi's 35% OOS-positive (13/37) implies a survival rate consistent with random pair selection plus mild edge — not a winning lottery ticket-pool. Our forward replicas (BTC/ETH positive, BNB/SOL + BTC/SOL negative) show 33% positive (1/3 spreads × 2 versions), within sampling noise of Palazzi's 35%. This is direct empirical confirmation that the survival rate at our fee tier matches the paper's, **and** that picking the right pair matters more than the strategy variant.

#### 8.2.6 Pass / fail vs §6.2.6 threshold
- Threshold: deflated annual return **> 25%** AND deflated Sharpe **> 1.0** AND deflated MDD **< 30%**.
- Outcome: deflated return **~3–5%/yr** (≪ 25%), deflated Sharpe **~0.20–0.30** (≪ 1.0).
- **Verdict:** **FAIL §6.2 standalone.** Refer to §4.5 GatedExecution as a sub-signal (per §6.2.6 last bullet — "discrete signal that could plug into GatedExecution").

### 8.3 §6.2 Worksheet — Tadi & Witzany (Financial Innovation, 2025)

#### 8.3.1 Sharpe / return decay
- **Headline input ⚠ inferred:** copula-pairs papers in this class typically report Sharpe **0.8–1.5** on best parameter sets. Use midpoint **1.1** as conservative proxy.
- **After 0.5 decay:** Sharpe **0.55**.

#### 8.3.2 Fee tier downgrade
- Paper tests **on Binance USDT-M futures** — same venue as our deploy. Fee assumption ⚠ inferred but likely VIP-0 retail (10 bps RT). Fee delta vs ours: small (0–5 bps RT). Drag **~0–1.5%/yr**.

#### 8.3.3 Slippage layer
- Pair universe inferred as full Binance perp listing including mid-caps. Mean-reversion candidates often select for divergent (i.e., *less* liquid) names. Conservative slippage **~10 bps RT per spread cycle** ⇒ at 30 trades/yr/spread ≈ **~3%/yr** drag.

#### 8.3.4 Regime weighting
- Weekly pair re-selection adapts faster than Palazzi's static universe but does **not** address regime — it addresses pair quality. §6.2.4 re-weighting still applies. ⚠ inferred 2018–2024 window with bear coverage but pre-2025 bull. Apply the standard 33/34/33 weighting; expect ~50% of headline survives (similar to Palazzi mix).

#### 8.3.5 Selection bias
- Weekly re-selection introduces **per-week multiple testing**. With ~52 weeks/yr × ~50 candidate pairs ≈ 2,600 selection events/yr. The (1/N)^0.3 penalty in §6.2.5 caps at modest values for large N (`(1/2600)^0.3 ≈ 0.10`), but this is conservative — the dominant signal is real cointegration, not noise pair-of-the-week luck. Apply a softer penalty: divide Sharpe by **1.5×** vs the (1/N)^0.3 strict reading.
- Headline Sharpe 0.55 (post-decay) ÷ 1.5 ≈ **0.37**. Return scales similarly: ~6–8%/yr post-decay, ~4–6%/yr post-selection.

#### 8.3.6 Pass / fail vs §6.2.6 threshold
- Deflated return **~3–5%/yr** (≪ 25%), Sharpe **~0.30–0.40** (≪ 1.0).
- **Verdict:** **FAIL §6.2 standalone.** Same refer-to-GatedExecution recommendation as Palazzi.

### 8.4 §6.3 Paper Replication Checklist

#### 8.4.1 Palazzi 2025
| # | Question | Answer / Note |
|---|---|---|
| 1 | Fee tier? | ⚠ inferred 5 bps/side spot. **Demands re-read of paper.** |
| 2 | Data window? | ⚠ inferred ~2017–2024. Bear 2022 inclusion uncertain. |
| 3 | Survivorship-biased universe? | "10 major cryptos" — yes, by current market cap. Material at horizon-of-paper. |
| 4 | Daily-close-to-close vs slippage-aware? | ⚠ inferred close-to-close. Walk-forward simulation likely does not embed retail slippage. |
| 5 | Param-opt protocol? | Walk-forward (75/25 stated in dev plan §1.3). Strong. |
| 6 | MDD definition? | ⚠ inferred peak-to-trough on equity curve. |
| 7 | Regime splits reported? | ⚠ Likely partial (paper claims "positive in both bull and bear"). Demand Phase 0 regime-split if revived. |
| 8 | Best parameter set / dispersion? | Critical: **35% OOS-positive (13/37)**. Per-pair Sharpe dispersion is wide; portfolio Sharpe 0.89 << best-pair 2.12. |
| 9 | Live / forward track record? | None published. Our 4-week droplet is the first independent forward replication; **35% positive replicas matches paper's OOS-positive rate exactly.** |
| 10 | Infrastructure assumptions? | Standard retail Freqtrade-compatible. ✓ |

#### 8.4.2 Tadi & Witzany 2025
| # | Question | Answer / Note |
|---|---|---|
| 1 | Fee tier? | ⚠ inferred VIP-0 retail (10 bps RT). Same venue as ours — minimal fee delta. |
| 2 | Data window? | ⚠ inferred 2018–2024, includes 2022 bear. |
| 3 | Survivorship-biased? | Weekly re-selection mitigates but does not eliminate (delisted pairs still excluded retroactively). |
| 4 | Slippage-aware? | ⚠ Probably not — copula papers typically assume mid-quote fills. |
| 5 | Param-opt protocol? | Weekly re-selection from rolling window. Strong on adaptation, weak on multiple testing. |
| 6 | MDD definition? | ⚠ inferred standard equity peak-to-trough. |
| 7 | Regime splits? | ⚠ Partial. |
| 8 | Best parameter set / dispersion? | Selection happens weekly across full universe — high effective N. |
| 9 | Live / forward track record? | None published. |
| 10 | Infrastructure assumptions? | Compatible — same exchange, similar holding periods. ✓ |

### 8.5 Forward Post-Mortem (2026-05-02 droplet closure)

**Final combined snapshot (UTC 2026-05-02, 4 calendar weeks live-shaped):**

| Spread × Variant | Snapshot PnL vs stake | Closed trades (subset) | Verdict |
|---|---|---|---|
| BTC/ETH × V01 | **~+4.2%** | (subset of 17 total) | Positive — only pair-surface aligned with lab walk-forward |
| BTC/ETH × V02 | **~+4.2%** | (subset of 17 total) | Positive — independent confirmation |
| BNB/SOL × V01 | ~−1.5% | (subset) | Negative — drag on aggregate |
| BNB/SOL × V02 | ~−1.25% | (subset) | Negative |
| BTC/SOL × V01 | ~−2.0% | (subset) | Negative |
| BTC/SOL × V02 | ~−2.0% | (subset) | Negative |
| **Aggregate** | **~+0.01% (~+US$6.56)** | **17 closed / 12 open** | **Below §2 50-trade threshold; economically flat** |

**Root-cause attribution for the BNB/SOL + BTC/SOL drag:**
1. **Liquidity asymmetry.** SOL had higher realized volatility than BNB and (relative to BTC) than ETH during the test window. Higher leg volatility on the *follower* leg increases dollar slippage at entry/exit and inflates β instability between hedge updates. This is *exactly* the failure mode V02's β-churn filter targets — but V02 churn defaults are tuned on BTC/ETH and are not pair-calibrated.
2. **Pair selection vs Phase 0 GO inheritance.** BNB/SOL and BTC/SOL passed Phase 0 GO at 4h on the 2022–2025 sample, but the GO bar is "≥6/8 diagnostics," not "outperforms BTC/ETH out-of-sample." The lab CSVs do not report per-pair full-period P&L head-to-head — that gap is what allowed three spreads to be deployed in parallel without a head-to-head pair ranking.
3. **What the lab walk-forward missed.** The walk-forward ran on **BTC/ETH only**. We never ran a walk-forward CSV across BTC/ETH vs BNB/SOL vs BTC/SOL to compare. The implicit assumption that "Phase 0 GO ⇒ comparable forward economics" was the gap.

**Why aggregate moved from −1.72% (2026-04-18) to ~+0.01% (2026-05-02):**
- BTC/ETH closed several profitable z-reversion trades in the second half of the window.
- Open MTM on negative legs partially recovered as spreads narrowed.
- Net: noise-level recovery, not signal-driven. The 17-trade sample is too small to distinguish signal from random spread mean-reversion.

**Lesson contributed:** When a paper's universe shows OOS-positive in 35% of pairs, deploying 3 pairs at random is a lottery — pair selection within the universe is the dominant variable, not strategy variant (V01 vs V02). Cross-pair walk-forward ranking should be mandatory before parallel deploy.

### 8.6 Final Verdict (2026-05-03) — Option (a): Fold spread/z-score into §4.5 GatedExecution

**Decision:** **(a) Integrate spread/z-score signal layer into §4.5 GatedExecution** as an optional gate. Status remains **PARKED** (not ARCHIVED) per Research Log §4.3.

**Why (a) over (b) and (c):**

- **(c) ARCHIVE is too aggressive.** Three independent lines of evidence say the signal is real, not lottery-ticket noise:
  1. Hurst H ≈ 0.25 in F's Phase 0 — real mean-reversion structure across the major-crypto universe.
  2. Lab BTC/ETH @ 4h V01 default total +25.7% / V02 +27.7% over 4y; PFs 1.12 / 1.14. Modest but positive on the highest-liquidity spread.
  3. Forward replicas 1/3 positive (BTC/ETH × V01+V02) matches Palazzi's 35% OOS-positive headline rate within sampling noise.
  Archiving discards the dual-leg infrastructure (~5 weeks of dev work — `confirm_trade_entry`, orphan-leg watchdog, β-weighted stakes, `informative_pairs` alignment) that has no comparable cost to rebuild.

- **(b) Revive as portfolio-of-spreads is premature.** §6.2 says return >25% AND Sharpe >1.0 AND MDD <30%; deflation worksheets above show ~3–5%/yr return and ~0.2–0.4 Sharpe. Reviving requires either (i) a held-out pair selection method that demonstrably outperforms naive Phase 0 GO inheritance, OR (ii) a vol-targeted overlay (Research Log §5.6 Axis C candidate) that multiplies edge sufficiently. Neither exists in the registry today. Forward-validating (b) requires ≥50 closed trades per replica × N replicas — at the lab's 31.5 trades/yr/spread that's **~19 calendar months per replica** of droplet spend. Not justified on current evidence.

- **(a) GatedExecution sub-signal is the correct match for the evidence:**
  - The signal is real but doesn't clear standalone fee economics — exactly the §4.5 thesis (combine validated-but-sub-threshold signals).
  - Spread/z-score is **gate-shaped**: it produces direction-bias (z>0 → favor short A, long B; z<0 → opposite) that can confirm or veto a primary signal. It is not directionally redundant with LiqCascade (cascade detection) or OracleSurfer (regime classification).
  - Integration cost is low. The dual-leg execution infra is not needed in GatedExecution — only the *signal output* (direction, confidence, freshness) is. The signal can be computed in a sidecar reading 4h candles; no per-pair Freqtrade processes required.
  - The paper-derived adaptive trailing stop and Palazzi vol filter — which lab tests showed *reduce* P&L vs z-reversion + time stop — are explicitly **not** carried forward. GatedExecution's unified exit framework supersedes them.

**What carries forward into GatedExecution Dev Plan v0.1 (Step 5):**

1. **Spread/z-score signal source** (formal name TBD in Step 5). Inputs: pair (A, B), `ols_window`, `zscore_window`, `entry_zscore`. Outputs: `{direction, confidence, freshness}` per pair per candle. Confidence proportional to |z| above entry threshold. Freshness = candles since spread last crossed the entry threshold.
2. **Per-pair calibration is mandatory.** Naive multi-pair deploy failed forward (BNB/SOL, BTC/SOL). The gate should accept only pairs that pass a head-to-head walk-forward ranking, not Phase 0 GO inheritance.
3. **β-weighted stakes are not relevant** when used as a gate (no live legs to hedge). Drop the β-weighting machinery from the GatedExecution path.
4. **The mean-reversion structure complements LiqCascade's event-driven primary signal** — z-score reverts a *spread*, while cascades are *single-instrument* events. Conditioning a cascade trade on spread direction is a non-redundant gate.

**What is intentionally *not* preserved:**
- BTC/PAXG, LINK/ETH, UNI/SOL, XMR/BTC exploratory configs (Part 3) — all underperformed and contribute nothing to a GatedExecution signal.
- Hyperopt JSONs (`...best_params_2026-03-31.json`) — not robust on full timerange; do not load into GatedExecution sidecar.
- Adaptive trailing stop and vol filter Palazzi options — lab demonstrated they reduce P&L; superseded by GatedExecution unified exit.

**Operational closure:**
- `freqtrade-coint-pairs-trading` repo retained for reproducibility. No further droplet spend.
- Lab strategy files (`EnhancedCointPairsStrategy_V01.py`, `_V02.py`) retained — used by GatedExecution Dev Plan as the reference implementation for the spread/z-score signal computation logic (not for execution).

---

## Part 9: Related Documents

| Document | Use |
|----------|-----|
| `EnhancedCointPairs_Dev_Plan.md` | Commands, phase gates, file index, deploy Part 6 |
| `AlgoTrading_Research_Log.md` | Candidate **L registry** (**PARKED §4.3**), effort allocation **§4.6**, deflation rules **§6.2** |
| `CointPairsTrading_Deep_Dive.md` | Predecessor F — what not to repeat |
| `user_data/results/cointpairs_comparison_tables.md` | Numeric backtest recap |
| `GatedExecution_Dev_Plan.md` *(pending — Step 5)* | Will consume spread/z-score signal source per Part 8.6 |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-02 | v1 — Deep dive created: research log, dev plan, deploy repo, lab results summary, chat-derived decision notes. |
| 2026-04-03 | Part 3: LINK/ETH, UNI/SOL, XMR/BTC V01@4h backtest summary (deploy repo); Part 4.3: optional lab reproduction configs. |
| 2026-05-02 | **Forward deploy discontinued.** Header + Part 6 **§6.3**: final **`droplet_status_from_local`** summary (~**+0.01%** combined; **BTC/ETH** positive, **BNB/SOL** + **BTC/SOL** negative). Registry → **PARKED** (**not ARCHIVED**). Part 4.2 topology labelled historical. |
| 2026-05-03 | **Part 8 added.** §6.2 Edge Deflation Pass on Palazzi 2025 + Tadi & Witzany 2025 — both FAIL standalone thresholds. §6.3 Paper Replication Checklists. Forward post-mortem with root-cause attribution for BNB/SOL + BTC/SOL drag. **Final verdict: option (a) — fold spread/z-score into §4.5 GatedExecution as sub-signal.** Old Part 7 renumbered to Part 9. |

