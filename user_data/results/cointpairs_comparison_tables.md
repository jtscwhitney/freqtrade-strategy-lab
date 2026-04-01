# Candidate L — backtest comparison (same data / config)

Linked from `user_data/info/EnhancedCointPairs_Dev_Plan.md` (Current Phase → backtest recap).

Sources: `cointpairs_walk_forward.csv`, `cointpairs_walk_forward_v02.csv`, `cointpairs_walk_forward_v01_default_vs_hyperopt.csv`, `cointpairs_beta_churn_sweep.csv`.

**Setup:** `config_cointpairs_l_phase1.json`, BTC/ETH @ 4h, `--cache none`, Docker backtests. V01/V02 “default” = no sidecar JSON (strategy `DecimalParameter` defaults). V02 uses `beta_churn_max=0.0085`, `beta_churn_window=12` unless noted.

---

## 1. Calendar windows — V01 vs V02 vs V01 hyperopt

| Window | Timerange | V01 default<br>Total % | V01 default<br>PF / Sharpe | V02 default<br>Total % | V02 default<br>PF / Sharpe | V01 hyperopt<br>Total % | V01 hyperopt<br>PF / Sharpe |
|--------|-----------|-------------------------:|---------------------------:|-------------------------:|---------------------------:|-------------------------:|---------------------------:|
| 2022 | 20220101–20221231 | 8.39 | 1.18 / 0.08 | −0.47 | 0.99 / −0.01 | −13.98 | 0.71 / −0.17 |
| 2023 | 20230101–20231231 | −0.58 | 0.98 / −0.01 | 3.61 | 1.15 / 0.05 | 2.55 | 1.11 / 0.04 |
| 2024 | 20240101–20241231 | 10.90 | 1.20 / 0.13 | 18.30 | 1.38 / 0.20 | 3.79 | 1.12 / 0.05 |
| 2025–26 Q1 | 20250101–20260331 | 4.49 | 1.07 / 0.05 | 4.54 | 1.07 / 0.05 | 4.54 | 1.11 / 0.05 |
| **Full** | 20220101–20260331 | **25.73** | 1.12 / 0.07 | **27.67** | 1.14 / 0.08 | **−4.31** | 0.97 / −0.01 |

Trades (same order of columns: V01 def / V02 def / V01 ho): 2022: 24 / 24 / 24 · 2023: 32 / 22 / 22 · 2024: 34 / 30 / 20 · 2025–26: 46 / 46 / 30 · full: 134 / 122 / 96.

---

## 2. 2024 & 2025–26 Q1 — β-churn sweep (V02 sidecar JSON) vs baselines

Fixed `beta_churn_window=12`. Same timeranges as §1 for those rows.

| Run | 2024 Total % | 2024 PF | 2024 trades | 2025–26 Q1 Total % | 2025–26 Q1 PF | 2025–26 Q1 trades |
|-----|-------------:|--------:|------------:|-------------------:|--------------:|-----------------:|
| **V01 default** | 10.90 | 1.20 | 34 | 4.49 | 1.07 | 46 |
| **V02 default** (0.0085) | 18.30 | 1.38 | 30 | 4.54 | 1.07 | 46 |
| V02 churn **0.006** | 18.27 | 1.45 | 26 | **−0.81** | 0.98 | 40 |
| V02 churn **0.0075** | 15.81 | 1.34 | 26 | 4.52 | 1.07 | 46 |
| V02 churn **0.0085** | 18.30 | 1.38 | 30 | 4.54 | 1.07 | 46 |
| V02 churn **0.010** | **21.36** | 1.44 | 32 | 4.49 | 1.07 | 46 |
| V02 churn **0.012** | 17.99 | 1.36 | 34 | 4.49 | 1.07 | 46 |

---

## 3. File reference

| File | Contents |
|------|----------|
| `cointpairs_walk_forward.csv` | V01 defaults, all windows |
| `cointpairs_walk_forward_v02.csv` | V02 defaults, all windows |
| `cointpairs_walk_forward_v01_default_vs_hyperopt.csv` | V01 default + hyperopt |
| `cointpairs_beta_churn_sweep.csv` | Churn grid (quick windows: 2024 + 2025–26 Q1) |
