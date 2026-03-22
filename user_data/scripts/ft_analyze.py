"""
LiqCascade dry-run trade analysis.
Run via: docker cp ft_analyze.py freqtrade_liqcascade:/tmp/ft_analyze.py && docker exec freqtrade_liqcascade python /tmp/ft_analyze.py
"""
from freqtrade.persistence import Trade, init_db
from collections import defaultdict

init_db('sqlite:////freqtrade/user_data/tradesv3.dryrun.sqlite')

trades = Trade.get_trades_proxy(is_open=False)

if not trades:
    print('No closed trades found.')
    exit()

exit_counts = defaultdict(lambda: {'n': 0, 'profit': 0.0, 'wins': 0})
pair_counts  = defaultdict(lambda: {'n': 0, 'profit': 0.0})
dir_counts   = defaultdict(lambda: {'n': 0, 'profit': 0.0, 'wins': 0})

for t in trades:
    r = t.exit_reason or 'unknown'
    p = t.close_profit or 0.0
    d = 'short' if t.is_short else 'long'
    w = 1 if p > 0 else 0
    exit_counts[r]['n'] += 1
    exit_counts[r]['profit'] += p
    exit_counts[r]['wins'] += w
    pair_counts[t.pair]['n'] += 1
    pair_counts[t.pair]['profit'] += p
    dir_counts[d]['n'] += 1
    dir_counts[d]['profit'] += p
    dir_counts[d]['wins'] += w

wins       = sum(1 for t in trades if (t.close_profit or 0) > 0)
total_p    = sum(t.close_profit or 0 for t in trades)
gross_wins = sum(t.close_profit for t in trades if (t.close_profit or 0) > 0)
gross_loss = abs(sum(t.close_profit for t in trades if (t.close_profit or 0) < 0))

print(f'Closed trades: {len(trades)}')
print(f'Win rate:      {wins / len(trades) * 100:.1f}%')
print(f'Avg profit:    {total_p / len(trades) * 100:.3f}%')
print(f'Profit factor: {gross_wins / gross_loss:.3f}' if gross_loss else 'Profit factor: inf')

print()
print('EXIT REASON BREAKDOWN:')
for r, v in sorted(exit_counts.items(), key=lambda x: -x[1]['n']):
    avg = v['profit'] / v['n'] * 100
    wr  = v['wins']   / v['n'] * 100
    print(f'  {r:<22}  n={v["n"]:>4}  avg={avg:>+7.3f}%  win%={wr:>5.1f}%')

print()
print('BY DIRECTION:')
for d, v in sorted(dir_counts.items()):
    avg = v['profit'] / v['n'] * 100
    wr  = v['wins']   / v['n'] * 100
    print(f'  {d:<6}  n={v["n"]:>4}  avg={avg:>+7.3f}%  win%={wr:>5.1f}%')

print()
print('BY PAIR:')
for pair, v in sorted(pair_counts.items(), key=lambda x: -x[1]['n']):
    avg = v['profit'] / v['n'] * 100
    print(f'  {pair:<22}  n={v["n"]:>4}  avg={avg:>+7.3f}%')
