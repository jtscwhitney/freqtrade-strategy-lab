"""Summarize Candidate J backtest trades by regime (exit date). Run from repo root or anywhere."""
from __future__ import annotations

import json
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Exit-date buckets (UTC), aligned with Deep Dive regime narrative
REGIMES: list[tuple[str, datetime, datetime]] = [
    ("2022_Bear", datetime(2022, 1, 1, tzinfo=timezone.utc), datetime(2023, 1, 1, tzinfo=timezone.utc)),
    ("2023_Range", datetime(2023, 1, 1, tzinfo=timezone.utc), datetime(2024, 1, 1, tzinfo=timezone.utc)),
    ("2024_2025_Bull", datetime(2024, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ("2026_YTD", datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 4, 6, tzinfo=timezone.utc)),
]


def load_trades(zip_path: Path) -> tuple[str, list[dict]]:
    with zipfile.ZipFile(zip_path) as zf:
        name = [n for n in zf.namelist() if n.endswith(".json") and "_config" not in n][0]
        data = json.loads(zf.read(name))
    strat = data["strategy"]
    key = list(strat.keys())[0]
    return key, strat[key]["trades"]


def parse_close(ts: str) -> datetime:
    # "2024-01-15 12:00:00+00:00"
    if ts.endswith("+00:00"):
        ts = ts[:-6]
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


def regime_of(t_close: datetime) -> str | None:
    for label, a, b in REGIMES:
        if a <= t_close < b:
            return label
    return None


def summarize(zip_path: Path) -> None:
    name, trades = load_trades(zip_path)
    print(f"\n=== {zip_path.name} | {name} | trades={len(trades)} ===")
    by_reg: dict[str, list[float]] = defaultdict(list)
    by_exit: dict[str, int] = defaultdict(int)
    unbucket = 0
    for t in trades:
        cd = parse_close(t["close_date"])
        r = regime_of(cd)
        p = float(t["profit_abs"])
        er = t.get("exit_reason", "")
        by_exit[er] += 1
        if r:
            by_reg[r].append(p)
        else:
            unbucket += 1
            by_reg["_unbucketed"].append(p)

    total_all = sum(sum(v) for k, v in by_reg.items() if k != "_unbucketed")
    print(f"{'Regime':<18} {'Trades':>7} {'Profit USDT':>14} {'Win%':>7} {'Avg USDT':>10}")
    for label, _, _ in REGIMES:
        pls = by_reg.get(label, [])
        if not pls:
            print(f"{label:<18} {0:>7} {0:>14.2f} {'n/a':>7} {'n/a':>10}")
            continue
        w = sum(1 for x in pls if x > 0)
        print(
            f"{label:<18} {len(pls):>7} {sum(pls):>14.2f} {100 * w / len(pls):>6.1f}% {sum(pls) / len(pls):>10.2f}"
        )
    ub = by_reg.get("_unbucketed", [])
    if ub:
        print(f"{'_unbucketed':<18} {len(ub):>7} {sum(ub):>14.2f}")
    print(f"{'ALL (sum regs)':<18} {sum(len(by_reg[l]) for l, _, _ in REGIMES):>7} {total_all:>14.2f}")

    # Time-stop diagnostic (Lesson #11)
    ts_n = sum(1 for t in trades if t.get("exit_reason") == "time_stop_donchian")
    print(f"time_stop_donchian: {ts_n} / {len(trades)} ({100 * ts_n / max(1, len(trades)):.1f}%)")
    print("exit mix:", dict(sorted(by_exit.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    for fn in (
        "backtest-result-2026-04-06_09-54-32.zip",
        "backtest-result-2026-04-06_09-55-46.zip",
    ):
        zp = base.parent / "backtest_results" / fn
        if zp.exists():
            summarize(zp)
