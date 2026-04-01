# BNB/SOL @ 4h — preserved backtest bundle (Candidate L)

**Purpose:** Keep a reproducible snapshot of the high P&L BNB/SOL run for deeper analysis (not discarded after review).

| Field | Value |
|-------|--------|
| Pair (spread) | `traded` = BNB/USDT:USDT, `anchor` = SOL/USDT:USDT |
| Timeframe | 4h |
| Timerange | `20220101-20260331` |
| Strategy | `EnhancedCointPairsStrategy_V02` |
| Params | `strategy_params_snapshot.json` (same as `user_data/strategy_params/EnhancedCointPairsStrategy_V02_defaults.json`) |
| Config | `config_snapshot.json` (BNB+SOL whitelist + `cointpairs` block) |

## Reproduce (Docker)

From repo root, ensure `strategy_params_snapshot.json` is copied beside the strategy if you want identical param loading:

`copy user_data\\results\\cointpairs_bnb_sol_4h_analysis\\strategy_params_snapshot.json user_data\\strategies\\EnhancedCointPairsStrategy_V02.json`

Then:

`docker compose run --rm freqtrade backtesting --config /freqtrade/config/config_cointpairs_lever_sweep_tmp.json --strategy EnhancedCointPairsStrategy_V02 --timerange 20220101-20260331 --cache none --export trades --export-directory=user_data/results/cointpairs_bnb_sol_4h_analysis`

(`config_cointpairs_lever_sweep_tmp.json` should match `config_snapshot.json` in this folder.)

## Files in this folder

| File | Purpose |
|------|---------|
| `strategy_params_snapshot.json` | Copy to `user_data/strategies/EnhancedCointPairsStrategy_V02.json` to reload same params |
| `config_snapshot.json` | Copy to `config/config_cointpairs_lever_sweep_tmp.json` (or merge `cointpairs` + whitelist) |
| `backtest-result-2026-04-01_11-49-21.zip` | Freqtrade export (trades list, full result) |
| `backtest-result-2026-04-01_11-49-21.meta.json` | Run metadata |
| `.last_result.json` | Points at latest zip |
| `SUMMARY.txt` | Headline metrics |
| `RUN_MANIFEST.md` | This file |

**Verified rerun:** total profit **143.13%**, **138** leg-trades, same order of magnitude as the original lever-sweep row.

The strategy sidecar was **removed** from `user_data/strategies/` after copying params here so routine V02 backtests use code defaults; this folder is the **source of truth** for this analysis run.
