#!/usr/bin/env python3
"""
Grid search for EnhancedCointPairsStrategy_V02 `beta_churn_max` (and optionally `beta_churn_window`).

Writes a temporary `user_data/strategies/EnhancedCointPairsStrategy_V02.json` with fixed code-default
buy/sell params plus the churn grid point, runs Docker backtests per calendar window, restores any
prior JSON on exit.

Usage (repo root):
  python user_data/scripts/cointpairs_beta_churn_sweep.py --quick
  python user_data/scripts/cointpairs_beta_churn_sweep.py --churn-max 0.006,0.0085,0.011 --sweep-window

Requires: Docker; loads helpers from `cointpairs_walk_forward.py` in this directory.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from contextlib import contextmanager
from pathlib import Path


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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def v02_param_json(
    *,
    entry_zscore: float = 2.0,
    ols_window: int = 180,
    zscore_window: int = 84,
    beta_churn_window: int = 12,
    beta_churn_max: float = 0.0085,
    exit_zscore: float = 0.5,
    max_hold_candles: int = 360,
) -> dict:
    return {
        "strategy_name": "EnhancedCointPairsStrategy_V02",
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
            "buy": {
                "entry_zscore": entry_zscore,
                "ols_window": ols_window,
                "zscore_window": zscore_window,
                "beta_churn_window": beta_churn_window,
                "beta_churn_max": beta_churn_max,
            },
            "sell": {
                "exit_zscore": exit_zscore,
                "max_hold_candles": max_hold_candles,
            },
        },
        "ft_stratparam_v": 1,
    }


@contextmanager
def v02_json_installed(repo: Path, data: dict):
    dst = repo / "user_data" / "strategies" / "EnhancedCointPairsStrategy_V02.json"
    backup: bytes | None = None
    if dst.exists():
        backup = dst.read_bytes()
    try:
        dst.write_text(json.dumps(data, indent=2), encoding="utf-8")
        yield
    finally:
        if backup is not None:
            dst.write_bytes(backup)
        elif dst.exists():
            dst.unlink()


def main() -> int:
    ap = argparse.ArgumentParser(description="β-churn grid for EnhancedCointPairsStrategy_V02")
    ap.add_argument(
        "--churn-max",
        default="0.006,0.0075,0.0085,0.01,0.012",
        help="Comma-separated beta_churn_max values",
    )
    ap.add_argument(
        "--churn-window",
        default="12",
        help="Comma-separated beta_churn_window values (use with --sweep-window)",
    )
    ap.add_argument(
        "--sweep-window",
        action="store_true",
        help="Cartesian product of churn-max and churn-window lists",
    )
    ap.add_argument("--quick", action="store_true", help="2024 + 2025-2026Q1 windows only")
    ap.add_argument("--dry-run", action="store_true", help="Print planned runs only")
    ap.add_argument(
        "--output",
        default="user_data/results/cointpairs_beta_churn_sweep.csv",
        help="CSV path relative to repo root",
    )
    ap.add_argument(
        "--config",
        default="/freqtrade/config/config_cointpairs_l_phase1.json",
        help="Config path inside container",
    )
    args = ap.parse_args()

    repo = _repo_root()
    wf = _load_walk_forward_module(repo)
    windows = (
        [("2024", "20240101-20241231"), ("2025-2026Q1", "20250101-20260331")]
        if args.quick
        else wf.DEFAULT_WINDOWS
    )

    maxes = [float(x.strip()) for x in args.churn_max.split(",") if x.strip()]
    wins = [int(x.strip()) for x in args.churn_window.split(",") if x.strip()]
    if not args.sweep_window:
        combos = [(m, wins[0]) for m in maxes]
    else:
        combos = [(m, w) for m in maxes for w in wins]

    rows: list[dict[str, str]] = []
    strategy = "EnhancedCointPairsStrategy_V02"

    for cm, cw in combos:
        data = v02_param_json(beta_churn_max=cm, beta_churn_window=cw)
        for label, tr in windows:
            if args.dry_run:
                print(f"beta_churn_max={cm} beta_churn_window={cw} {label} {tr}")
                rows.append(
                    {
                        "beta_churn_max": str(cm),
                        "beta_churn_window": str(cw),
                        "window": label,
                        "timerange": tr,
                        "exit_code": "dry-run",
                    }
                )
                continue
            with v02_json_installed(repo, data):
                code, text = wf.run_backtest(
                    repo, args.config, strategy, tr, "none", False
                )
            m = wf.parse_backtest_stdout(text, strategy) if code == 0 else None
            row = {
                "beta_churn_max": str(cm),
                "beta_churn_window": str(cw),
                "window": label,
                "timerange": tr,
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
                row["error_tail"] = (text[-1500:] if text else "").replace("\n", " ")[:400]
            rows.append(row)
            print(
                f"[cm={cm} cw={cw}][{label}] exit={code} "
                f"profit%={row.get('total_profit_pct', '')} trades={row.get('total_trades', '')}"
            )

    if not args.dry_run and rows:
        out_path = repo / args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames: list[str] = []
        for r in rows:
            for k in r:
                if k not in fieldnames:
                    fieldnames.append(k)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {out_path}")

    ok = all(r.get("exit_code") in ("0", "dry-run") for r in rows)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
