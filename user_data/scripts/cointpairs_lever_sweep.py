#!/usr/bin/env python3
"""
Candidate L — lever sweep backtests (Docker).

Runs one-at-a-time (OAT) parameter grids on EnhancedCointPairsStrategy_V02, plus:
  - baseline V02 (defaults, BTC/ETH)
  - V01 (no β-churn)
  - V02 @ 1h
  - Phase 0 “GO” pairs @ 4h (same V02 logic, config-driven pair)

Output: user_data/results/cointpairs_lever_sweep.csv

Usage (repo root):
  python user_data/scripts/cointpairs_lever_sweep.py --quick
  python user_data/scripts/cointpairs_lever_sweep.py

Requires: data for pairs/timeframes (run download-data if missing).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from contextlib import contextmanager, nullcontext
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_walk_forward_module(repo: Path):
    path = repo / "user_data" / "scripts" / "cointpairs_walk_forward.py"
    name = "cointpairs_walk_forward"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


DEFAULT_BUY = {
    "entry_zscore": 2.0,
    "ols_window": 180,
    "zscore_window": 84,
    "beta_churn_window": 12,
    "beta_churn_max": 0.0085,
}
DEFAULT_SELL = {
    "exit_zscore": 0.5,
    "max_hold_candles": 360,
}

# Phase 0 CSV @4h overall == GO (from cointpairs_phase0_summary.csv)
GO_PAIRS_4H: list[tuple[str, str, str]] = [
    ("BTC/ETH", "BTC/USDT:USDT", "ETH/USDT:USDT"),
    ("BTC/SOL", "BTC/USDT:USDT", "SOL/USDT:USDT"),
    ("BTC/DOGE", "BTC/USDT:USDT", "DOGE/USDT:USDT"),
    ("BNB/SOL", "BNB/USDT:USDT", "SOL/USDT:USDT"),
    ("SOL/DOGE", "SOL/USDT:USDT", "DOGE/USDT:USDT"),
    ("XRP/DOGE", "XRP/USDT:USDT", "DOGE/USDT:USDT"),
]


def build_v02_json(buy: dict, sell: dict, strategy_name: str) -> dict:
    return {
        "strategy_name": strategy_name,
        "params": {
            "roi": {"0": 100},
            "stoploss": {"stoploss": -0.99},
            "trailing": {
                "trailing_stop": False,
                "trailing_stop_positive": None,
                "trailing_stop_positive_offset": 0.0,
                "trailing_only_offset_is_reached": False,
            },
            "max_open_trades": {"max_open_trades": 2},
            "buy": buy,
            "sell": sell,
        },
        "ft_stratparam_v": 1,
    }


@contextmanager
def temp_phase1_config(repo: Path, traded: str, anchor: str, tf: str):
    """Write config/cointpairs_lever_sweep_tmp.json; restore or delete after."""
    src = repo / "config" / "config_cointpairs_l_phase1.json"
    dst = repo / "config" / "config_cointpairs_lever_sweep_tmp.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    data["exchange"]["pair_whitelist"] = [traded, anchor]
    data["cointpairs"] = {"traded": traded, "anchor": anchor}
    if "freqai" in data and "feature_parameters" in data["freqai"]:
        data["freqai"]["feature_parameters"]["include_timeframes"] = [tf]
    backup = dst.read_bytes() if dst.exists() else None
    try:
        dst.write_text(json.dumps(data, indent=2), encoding="utf-8")
        yield "/freqtrade/config/config_cointpairs_lever_sweep_tmp.json"
    finally:
        if backup is not None:
            dst.write_bytes(backup)
        elif dst.exists():
            dst.unlink()


@contextmanager
def strategy_json_sidecar(repo: Path, strategy_name: str, data: dict):
    dst = repo / "user_data" / "strategies" / f"{strategy_name}.json"
    backup = dst.read_bytes() if dst.exists() else None
    try:
        dst.write_text(json.dumps(data, indent=2), encoding="utf-8")
        yield
    finally:
        if backup is not None:
            dst.write_bytes(backup)
        elif dst.exists():
            dst.unlink()


def iter_oat_runs() -> list[dict]:
    """OAT: vary one buy/sell group at a time; others at default."""
    runs: list[dict] = []
    b0, s0 = dict(DEFAULT_BUY), dict(DEFAULT_SELL)

    runs.append(
        {
            "lever_id": "baseline_v02_btc_eth",
            "description": "V02 defaults BTC/ETH 4h",
            "strategy": "EnhancedCointPairsStrategy_V02",
            "timeframe": None,
            "pair_label": "BTC/ETH",
            "json_strategy": "EnhancedCointPairsStrategy_V02",
            "buy": dict(b0),
            "sell": dict(s0),
        }
    )

    for v in [1.65, 2.0, 2.4]:
        runs.append(
            {
                "lever_id": f"entry_z_{v}",
                "description": f"entry_zscore={v}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": "BTC/ETH",
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": {**b0, "entry_zscore": v},
                "sell": dict(s0),
            }
        )
    for v in [0.35, 0.5, 0.65]:
        runs.append(
            {
                "lever_id": f"exit_z_{v}",
                "description": f"exit_zscore={v}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": "BTC/ETH",
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": dict(b0),
                "sell": {**s0, "exit_zscore": v},
            }
        )
    for v in [60, 84, 120]:
        runs.append(
            {
                "lever_id": f"zscore_w_{v}",
                "description": f"zscore_window={v}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": "BTC/ETH",
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": {**b0, "zscore_window": v},
                "sell": dict(s0),
            }
        )
    for v in [150, 180, 210]:
        runs.append(
            {
                "lever_id": f"ols_w_{v}",
                "description": f"ols_window={v}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": "BTC/ETH",
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": {**b0, "ols_window": v},
                "sell": dict(s0),
            }
        )
    for v in [0.0075, 0.0085, 0.011]:
        runs.append(
            {
                "lever_id": f"beta_churn_max_{v}",
                "description": f"beta_churn_max={v}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": "BTC/ETH",
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": {**b0, "beta_churn_max": v},
                "sell": dict(s0),
            }
        )

    runs.append(
        {
            "lever_id": "v01_no_churn",
            "description": "V01 baseline (no beta churn)",
            "strategy": "EnhancedCointPairsStrategy_V01",
            "timeframe": None,
            "pair_label": "BTC/ETH",
            "json_strategy": None,
            "buy": None,
            "sell": None,
        }
    )
    runs.append(
        {
            "lever_id": "v02_1h_btc_eth",
            "description": "V02 defaults BTC/ETH 1h",
            "strategy": "EnhancedCointPairsStrategy_V02_1h",
            "timeframe": "1h",
            "pair_label": "BTC/ETH",
            "json_strategy": "EnhancedCointPairsStrategy_V02_1h",
            "buy": dict(b0),
            "sell": dict(s0),
        }
    )

    for label, traded, anchor in GO_PAIRS_4H[1:]:
        runs.append(
            {
                "lever_id": f"pair_{label.replace('/', '_')}",
                "description": f"V02 defaults 4h {label}",
                "strategy": "EnhancedCointPairsStrategy_V02",
                "timeframe": None,
                "pair_label": label,
                "traded": traded,
                "anchor": anchor,
                "json_strategy": "EnhancedCointPairsStrategy_V02",
                "buy": dict(b0),
                "sell": dict(s0),
            }
        )
    return runs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--timerange",
        default="20220101-20260331",
        help="Backtest timerange (default full lab window)",
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="Use 2024 only (faster smoke)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--output",
        default="user_data/results/cointpairs_lever_sweep.csv",
    )
    args = ap.parse_args()

    tr = "20240101-20241231" if args.quick else args.timerange
    repo = _repo_root()
    wf = _load_walk_forward_module(repo)

    rows: list[dict[str, str]] = []
    runs = iter_oat_runs()

    for spec in runs:
        lever_id = spec["lever_id"]
        strategy = spec["strategy"]
        tf = spec.get("timeframe")
        traded = spec.get("traded", "BTC/USDT:USDT")
        anchor = spec.get("anchor", "ETH/USDT:USDT")
        jname = spec.get("json_strategy")
        jdata = None
        if spec.get("buy") is not None and jname:
            jdata = build_v02_json(spec["buy"], spec["sell"], jname)

        if args.dry_run:
            print(lever_id, strategy, tr, traded, anchor, tf or "4h")
            rows.append({"lever_id": lever_id, "exit_code": "dry-run"})
            continue

        json_ctx = (
            strategy_json_sidecar(repo, jname, jdata)
            if jdata is not None and jname
            else nullcontext()
        )
        with temp_phase1_config(repo, traded, anchor, tf or "4h"):
            with json_ctx:
                code, text = wf.run_backtest(
                    repo,
                    "/freqtrade/config/config_cointpairs_lever_sweep_tmp.json",
                    strategy,
                    tr,
                    "none",
                    False,
                    timeframe=tf,
                )

        m = wf.parse_backtest_stdout(text, strategy) if code == 0 else None
        row: dict[str, str] = {
            "lever_id": lever_id,
            "description": spec.get("description", ""),
            "pair": spec.get("pair_label", ""),
            "timerange": tr,
            "strategy": strategy,
            "timeframe": tf or "4h",
            "exit_code": str(code),
            "total_trades": m.total_trades if m else "",
            "total_profit_pct": m.total_profit_pct if m else "",
            "profit_factor": m.profit_factor if m else "",
            "sharpe": m.sharpe if m else "",
            "max_dd_pct": m.max_dd_pct if m else "",
            "long_profit_pct": m.long_profit_pct if m else "",
            "short_profit_pct": m.short_profit_pct if m else "",
        }
        if code != 0:
            row["error_tail"] = (text[-1200:] if text else "").replace("\n", " ")[:400]
        rows.append(row)
        print(
            f"[{lever_id}] exit={code} profit%={row.get('total_profit_pct', '')} "
            f"trades={row.get('total_trades', '')} PF={row.get('profit_factor', '')}"
        )

    if not args.dry_run and rows:
        out = repo / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        fn: list[str] = []
        for r in rows:
            for k in r:
                if k not in fn:
                    fn.append(k)
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fn)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {out}")

    ok = all(r.get("exit_code") in ("0", "dry-run") for r in rows)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
