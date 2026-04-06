"""
Phase 0 grid: run `freqtrade backtesting` in Docker for Donchian variants.

Usage:

    # Inside Freqtrade container (recommended — calls `freqtrade backtesting` directly):
    docker compose run --rm --entrypoint python freqtrade user_data/scripts/donchian_phase0_sweep.py

    # On host (requires `docker` on PATH; uses compose to spawn each run):
    python user_data/scripts/donchian_phase0_sweep.py

Outputs:
    user_data/results/donchian_phase0_sweep_<UTCstamp>.json
    user_data/results/donchian_phase0_sweep_<UTCstamp>.md

Requires: Docker, compose file at repo root, downloaded 1h+1d futures data.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve()
REPO_ROOT = SCRIPT.parents[2]
IN_DOCKER = Path("/.dockerenv").exists()
FREQ_ROOT = Path("/freqtrade") if IN_DOCKER else REPO_ROOT
RESULTS = FREQ_ROOT / "user_data" / "results"
COMPOSE = REPO_ROOT / "docker-compose.yml"
FEE = "0.0005"
FT_USERDIR = str(FREQ_ROOT / "user_data")


@dataclass
class SweepRow:
    label: str
    strategy: str
    timerange: str
    timeframe: str
    max_open_trades: int
    total_trades: str | None
    total_profit_pct: str | None
    sharpe: str | None
    profit_factor: str | None
    abs_drawdown: str | None
    market_change: str | None
    exit_code: int
    error: str | None


def _parse_summary(text: str) -> dict[str, str | None]:
    """Extract SUMMARY METRICS rows from freqtrade backtesting output (stdout+stderr)."""
    out: dict[str, str | None] = {
        "total_trades": None,
        "total_profit_pct": None,
        "sharpe": None,
        "profit_factor": None,
        "abs_drawdown": None,
        "market_change": None,
    }
    clean = re.sub(r"\x1b\[[0-9;]*m", "", text)
    want = {
        "Total/Daily Avg Trades": "total_trades",
        "Total profit %": "total_profit_pct",
        "Sharpe": "sharpe",
        "Profit factor": "profit_factor",
        "Absolute drawdown": "abs_drawdown",
        "Market change": "market_change",
    }
    for line in clean.splitlines():
        line_st = line.strip()
        if not any(c in line_st for c in "│┃|"):
            continue
        parts = [p.strip() for p in re.split(r"\s*[│┃]\s*", line_st) if p.strip()]
        if len(parts) < 2:
            continue
        key, val = parts[0], parts[1]
        for prefix, k in want.items():
            if key.startswith(prefix):
                out[k] = val
                break
    # No "SUMMARY METRICS" block when there are zero trades — use STRATEGY SUMMARY row.
    if out["total_profit_pct"] is None:
        for line in clean.splitlines():
            line_st = line.strip()
            if not line_st.startswith("│") or "EnsembleDonchianStrategy_" not in line_st:
                continue
            parts = [p.strip() for p in re.split(r"\s*[│┃]\s*", line_st) if p.strip()]
            if len(parts) >= 5 and parts[0].startswith("EnsembleDonchian"):
                out["total_trades"] = parts[1]
                out["total_profit_pct"] = parts[4] if "%" in parts[4] else f"{parts[4]}%"
                if len(parts) >= 8:
                    out["abs_drawdown"] = parts[-1]
                break
    return out


def run_one(
    label: str,
    strategy: str,
    timerange: str,
    timeframe: str,
    max_open_trades: int,
    cache: str = "day",
) -> SweepRow:
    err_msg = None
    if IN_DOCKER:
        cmd = [
            "freqtrade",
            "backtesting",
            "--userdir",
            FT_USERDIR,
            "--config",
            "/freqtrade/config/config_donchian.json",
            "--strategy",
            strategy,
            "--timerange",
            timerange,
            "--timeframe",
            timeframe,
            "--fee",
            FEE,
            "--cache",
            cache,
            "--max-open-trades",
            str(max_open_trades),
        ]
        popen_cwd = str(FREQ_ROOT)
    else:
        cmd = [
            "docker",
            "compose",
            "-f",
            str(COMPOSE),
            "run",
            "--rm",
            "freqtrade",
            "backtesting",
            "--config",
            "/freqtrade/config/config_donchian.json",
            "--strategy",
            strategy,
            "--timerange",
            timerange,
            "--timeframe",
            timeframe,
            "--fee",
            FEE,
            "--cache",
            cache,
            "--max-open-trades",
            str(max_open_trades),
        ]
        popen_cwd = str(REPO_ROOT)

    try:
        proc = subprocess.run(
            cmd,
            cwd=popen_cwd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        out = proc.stdout + "\n" + proc.stderr
        parsed = _parse_summary(out)
        if proc.returncode != 0:
            err_msg = (proc.stderr or proc.stdout or "")[-2000:]
        return SweepRow(
            label=label,
            strategy=strategy,
            timerange=timerange,
            timeframe=timeframe,
            max_open_trades=max_open_trades,
            total_trades=parsed.get("total_trades"),
            total_profit_pct=parsed.get("total_profit_pct"),
            sharpe=parsed.get("sharpe"),
            profit_factor=parsed.get("profit_factor"),
            abs_drawdown=parsed.get("abs_drawdown"),
            market_change=parsed.get("market_change"),
            exit_code=proc.returncode,
            error=err_msg,
        )
    except Exception as e:
        return SweepRow(
            label=label,
            strategy=strategy,
            timerange=timerange,
            timeframe=timeframe,
            max_open_trades=max_open_trades,
            total_trades=None,
            total_profit_pct=None,
            sharpe=None,
            profit_factor=None,
            abs_drawdown=None,
            market_change=None,
            exit_code=-1,
            error=str(e),
        )


def build_grid() -> list[tuple[str, str, str, str, int]]:
    """List of (label, strategy, timerange, timeframe, max_open_trades)."""
    regimes = [
        ("2022_bear", "20220101-20221231"),
        ("2023", "20230101-20231231"),
        ("2024", "20240101-20241231"),
        ("2022_2025", "20220101-20250101"),
    ]
    core_strategies = [
        ("V01_dc", "EnsembleDonchianStrategy_V01"),
        ("V01_atr", "EnsembleDonchianStrategy_V01_ATR"),
        ("V02_dc", "EnsembleDonchianStrategy_V02"),
        ("V02_atr", "EnsembleDonchianStrategy_V02_ATR"),
    ]
    rows: list[tuple[str, str, str, str, int]] = []
    for reg_lbl, tr in regimes:
        for st_lbl, strat in core_strategies:
            tf = "1h" if strat.startswith("EnsembleDonchianStrategy_V01") else "1d"
            rows.append((f"{reg_lbl}__{st_lbl}", strat, tr, tf, 5))

    tr_full = "20220101-20250101"
    thr_strategies = [
        ("thr030", "EnsembleDonchianStrategy_V01_Entry030"),
        ("thr070", "EnsembleDonchianStrategy_V01_Entry070"),
        ("thr090", "EnsembleDonchianStrategy_V01_Entry090"),
    ]
    for sl, strat in thr_strategies:
        rows.append((f"2022_2025__{sl}", strat, tr_full, "1h", 5))

    rows.append(("2022_2025__V01_ablate_dc", "EnsembleDonchianStrategy_V01_LookbackAblated", tr_full, "1h", 5))
    rows.append(("2022_2025__V01_ablate_atr", "EnsembleDonchianStrategy_V01_LookbackAblated_ATR", tr_full, "1h", 5))

    for mot in (8, 10):
        rows.append((f"2022_2025__V01_dc_m{mot}", "EnsembleDonchianStrategy_V01", tr_full, "1h", mot))

    return rows


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_json = RESULTS / f"donchian_phase0_sweep_{stamp}.json"
    out_md = RESULTS / f"donchian_phase0_sweep_{stamp}.md"

    grid = build_grid()
    results: list[SweepRow] = []
    print(f"Running {len(grid)} backtests ({'freqtrade CLI' if IN_DOCKER else 'docker compose'})...", flush=True)
    for i, (label, strat, tr, tf, mot) in enumerate(grid, 1):
        print(f"  [{i}/{len(grid)}] {label} ...", flush=True)
        row = run_one(label, strat, tr, tf, mot)
        results.append(row)
        if row.error and row.exit_code != 0:
            print(f"    FAILED rc={row.exit_code}", flush=True)

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "fee_per_side": FEE,
        "rows": [asdict(r) for r in results],
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Donchian Phase 0 sweep",
        "",
        f"Generated: `{payload['generated_utc']}` | fee/side: `{FEE}` | cache: `day`",
        "",
        "| label | strategy | range | TF | mot | trades | profit % | Sharpe | PF | drawdown | rc |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.label} | {r.strategy} | {r.timerange} | {r.timeframe} | {r.max_open_trades} | "
            f"{r.total_trades or ''} | {r.total_profit_pct or ''} | {r.sharpe or ''} | {r.profit_factor or ''} | "
            f"{r.abs_drawdown or ''} | {r.exit_code} |"
        )
    lines.append("")
    try:
        rel_json = out_json.relative_to(REPO_ROOT)
    except ValueError:
        rel_json = out_json
    lines.append(f"Full JSON: `{rel_json}`")
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_json} and {out_md}", flush=True)
    return 0 if all(r.exit_code == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
