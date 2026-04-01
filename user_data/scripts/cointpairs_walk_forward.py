#!/usr/bin/env python3
"""
Walk-forward backtest helper for EnhancedCointPairsStrategy_V01 / V02.

Runs `docker compose run --rm freqtrade backtesting` for each timerange window,
parses summary metrics from stdout, writes CSV to user_data/results/.

Usage (from repo root):
  python user_data/scripts/cointpairs_walk_forward.py --strategy EnhancedCointPairsStrategy_V02
  python user_data/scripts/cointpairs_walk_forward.py --compare --params-json user_data/hyperopt_results/EnhancedCointPairsStrategy_V01_best_params_2026-03-31.json --strategy EnhancedCointPairsStrategy_V01

`--params-json` copies JSON beside the strategy (patched `strategy_name`), restores any prior file after each run.

Requires: Docker, ../Freqtrade build context (see docker-compose.yml).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WINDOWS: list[tuple[str, str]] = [
    ("2022", "20220101-20221231"),
    ("2023", "20230101-20231231"),
    ("2024", "20240101-20241231"),
    ("2025-2026Q1", "20250101-20260331"),
    ("full_2022_2026", "20220101-20260331"),
]


@dataclass
class ParsedMetrics:
    total_trades: str
    total_profit_pct: str
    profit_factor: str
    sharpe: str
    max_dd_pct: str
    long_profit_pct: str
    short_profit_pct: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_backtest_stdout(text: str, strategy: str) -> ParsedMetrics | None:
    """Extract key metrics from freqtrade backtesting text output."""
    pf = re.search(r"Profit factor\s*│\s*([\d.]+)", text)
    sh = re.search(r"Sharpe\s*│\s*([\d.-]+)", text)
    dd = re.search(r"Absolute drawdown\s*│\s*[\d.]+ USDT \(([\d.]+)%\)", text)

    ls = re.search(r"Long / Short profit %\s*│\s*([\d.-]+)%\s*/\s*([\d.-]+)%", text)

    strat_lines = [ln for ln in text.splitlines() if strategy in ln and "│" in ln]
    if strat_lines:
        parts = [p.strip() for p in strat_lines[-1].split("│")]
        parts = [p for p in parts if p]
        if len(parts) >= 5:
            return ParsedMetrics(
                total_trades=parts[1],
                total_profit_pct=parts[4].rstrip("%"),
                profit_factor=pf.group(1) if pf else "",
                sharpe=sh.group(1) if sh else "",
                max_dd_pct=dd.group(1) if dd else "",
                long_profit_pct=ls.group(1) if ls else "",
                short_profit_pct=ls.group(2) if ls else "",
            )

    tp = re.search(r"│\s*Total profit %\s*│\s*([\d.]+)%\s*│", text)
    tr = re.search(r"│\s*Total/Daily Avg Trades\s*│\s*(\d+)\s*/", text)
    if tp:
        return ParsedMetrics(
            total_trades=tr.group(1) if tr else "",
            total_profit_pct=tp.group(1),
            profit_factor=pf.group(1) if pf else "",
            sharpe=sh.group(1) if sh else "",
            max_dd_pct=dd.group(1) if dd else "",
            long_profit_pct=ls.group(1) if ls else "",
            short_profit_pct=ls.group(2) if ls else "",
        )
    return None


def run_backtest(
    repo: Path,
    config_container: str,
    strategy: str,
    timerange: str,
    cache: str,
    dry_run: bool,
    timeframe: str | None = None,
) -> tuple[int, str]:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(repo / "docker-compose.yml"),
        "run",
        "--rm",
        "freqtrade",
        "backtesting",
        "--config",
        config_container,
        "--strategy",
        strategy,
        "--timerange",
        timerange,
        "--cache",
        cache,
        "--export",
        "none",
    ]
    if timeframe:
        cmd.extend(["-i", timeframe])
    if dry_run:
        print(" ".join(cmd))
        return 0, ""

    proc = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return proc.returncode, out


@contextmanager
def strategy_json_sidecar(repo: Path, strategy: str, params_src: Path | None):
    """
    If params_src is set, write user_data/strategies/{strategy}.json from it (patch strategy_name).
    On exit, restore previous file contents or remove if we created it.
    """
    dst = repo / "user_data" / "strategies" / f"{strategy}.json"
    backup: bytes | None = None
    had_file = dst.exists()
    if had_file:
        backup = dst.read_bytes()
    try:
        if params_src is not None:
            data = json.loads(params_src.read_text(encoding="utf-8"))
            data["strategy_name"] = strategy
            dst.write_text(json.dumps(data, indent=2), encoding="utf-8")
        yield
    finally:
        if params_src is not None:
            if backup is not None:
                dst.write_bytes(backup)
            elif dst.exists():
                dst.unlink()


def metrics_to_row(
    window: str,
    timerange: str,
    strategy: str,
    param_set: str,
    code: int,
    text: str,
    m: ParsedMetrics | None,
) -> dict[str, str]:
    row: dict[str, str] = {
        "window": window,
        "timerange": timerange,
        "strategy": strategy,
        "param_set": param_set,
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
        tail = text[-2000:] if text else ""
        row["error_tail"] = tail.replace("\n", " ")[:500]
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Walk-forward backtests for Candidate L Phase 1.")
    ap.add_argument(
        "--config",
        default="/freqtrade/config/config_cointpairs_l_phase1.json",
        help="Config path inside container",
    )
    ap.add_argument("--strategy", default="EnhancedCointPairsStrategy_V01")
    ap.add_argument(
        "--cache",
        default="none",
        help="Backtest cache policy (use none for clean comparisons)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print docker commands only")
    ap.add_argument(
        "--output",
        default="user_data/results/cointpairs_walk_forward.csv",
        help="CSV path relative to repo root",
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="Only run 2024 and 2025-2026Q1 (faster smoke test)",
    )
    ap.add_argument(
        "--params-json",
        type=Path,
        default=None,
        help="Hyperopt/strategy JSON (host path); installed beside strategy for the run(s)",
    )
    ap.add_argument(
        "--param-set",
        default="default",
        help="Label for CSV column when not using --compare (e.g. hyperopt)",
    )
    ap.add_argument(
        "--compare",
        action="store_true",
        help="Run each window twice: without sidecar JSON, then with --params-json (requires --params-json)",
    )
    args = ap.parse_args()

    if args.compare and args.params_json is None:
        print("--compare requires --params-json", file=sys.stderr)
        return 2

    repo = _repo_root()
    out_path = repo / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    windows = (
        [("2024", "20240101-20241231"), ("2025-2026Q1", "20250101-20260331")]
        if args.quick
        else DEFAULT_WINDOWS
    )

    param_runs: list[tuple[str, Path | None]] = []
    if args.compare:
        param_runs = [("default", None), ("hyperopt", args.params_json)]
    else:
        param_runs = [(args.param_set, args.params_json)]

    rows: list[dict[str, str]] = []
    for param_set, pjson in param_runs:
        if pjson is not None and not pjson.is_absolute():
            pjson = repo / pjson
        with strategy_json_sidecar(repo, args.strategy, pjson if not args.dry_run else None):
            for label, tr in windows:
                code, text = run_backtest(
                    repo, args.config, args.strategy, tr, args.cache, args.dry_run
                )
                if args.dry_run:
                    rows.append(
                        {
                            "window": label,
                            "timerange": tr,
                            "strategy": args.strategy,
                            "param_set": param_set,
                            "exit_code": "dry-run",
                        }
                    )
                    continue
                m = parse_backtest_stdout(text, args.strategy) if code == 0 else None
                row = metrics_to_row(label, tr, args.strategy, param_set, code, text, m)
                rows.append(row)
                print(
                    f"[{param_set}][{label}] exit={code} profit%={row.get('total_profit_pct', '')} "
                    f"trades={row.get('total_trades', '')} L/S%={row.get('long_profit_pct', '')}/"
                    f"{row.get('short_profit_pct', '')}"
                )

    if not args.dry_run and rows:
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
