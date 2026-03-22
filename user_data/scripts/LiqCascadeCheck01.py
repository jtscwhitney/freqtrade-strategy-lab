import json, sys
  from collections import defaultdict

  data = json.load(sys.stdin)
  trades = [t for t in data['trades'] if not t['is_open']]
  print(f'Closed trades: {len(trades)}')

  exit_counts = defaultdict(lambda: {'n':0,'profit':0.0,'wins':0})
  pair_counts  = defaultdict(lambda: {'n':0,'profit':0.0})
  dir_counts   = defaultdict(lambda: {'n':0,'profit':0.0,'wins':0})

  for t in trades:
      r = t.get('exit_reason') or 'unknown'
      p = t.get('profit_ratio') or 0.0
      d = 'short' if t.get('is_short') else 'long'
      w = 1 if p > 0 else 0
      exit_counts[r]['n'] += 1; exit_counts[r]['profit'] += p; exit_counts[r]['wins'] += w
      pair_counts[t['pair']]['n'] += 1; pair_counts[t['pair']]['profit'] += p
      dir_counts[d]['n'] += 1; dir_counts[d]['profit'] += p; dir_counts[d]['wins'] += w

  wins = sum(1 for t in trades if (t.get('profit_ratio') or 0) > 0)
  total_profit = sum(t.get('profit_ratio') or 0 for t in trades)
  gross_wins = sum(t['profit_ratio'] for t in trades if t.get('profit_ratio',0) > 0)
  gross_loss = abs(sum(t['profit_ratio'] for t in trades if t.get('profit_ratio',0) < 0))

  print(f'Win rate:      {wins/len(trades)*100:.1f}%')
  print(f'Avg profit:    {total_profit/len(trades)*100:.3f}%')
  print(f'Profit factor: {gross_wins/gross_loss:.3f}' if gross_loss else 'PF: inf')
  print()
  print('EXIT REASON BREAKDOWN:')
  for r, v in sorted(exit_counts.items(), key=lambda x: -x[1][\"n\"]):
      print(f'  {r:<22} n={v[\"n\"]:>4}  avg={v[\"profit\"]/v[\"n\"]*100:>+7.3f}%
  win%={v[\"wins\"]/v[\"n\"]*100:>5.1f}%')
  print()
  print('BY DIRECTION:')
  for d, v in dir_counts.items():
      print(f'  {d:<6}  n={v[\"n\"]:>4}  avg={v[\"profit\"]/v[\"n\"]*100:>+7.3f}%
  win%={v[\"wins\"]/v[\"n\"]*100:>5.1f}%')
  print()
  print('BY PAIR:')
  for pair, v in sorted(pair_counts.items(), key=lambda x: -x[1][\"n\"]):
      print(f'  {pair:<22} n={v[\"n\"]:>4}  avg={v[\"profit\"]/v[\"n\"]*100:>+7.3f}%')