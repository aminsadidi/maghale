"""Pending cases (no result file yet) grouped into jobs of up to 4 (one per core of a GitHub runner), heaviest spread first."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cases import cases
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'meep')
only = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else ''
if not only and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'only.txt')):
    only = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'only.txt')).read().strip()   # restrict a push-triggered run
todo = [n for n, k in cases() if not os.path.exists(os.path.join(OUT, n + '.npz')) and (not only or n.startswith(tuple(only.split(','))))]
cost = lambda n: (3.4 if '_r300_' in n else 1) * (2.3 if 'P45' in n else 1.8 if 'P40' in n else 1) * (4 if n.startswith(('D_', 'DV_')) else 1) * (7 if n.startswith(('LG_', 'LT_')) else 1)
todo.sort(key=cost, reverse=True)
jobs = [[] for _ in range(max(1, (len(todo) + 3) // 4))]
for i, n in enumerate(todo): jobs[i % len(jobs)].append(n)                     # round robin: heavy runs in different jobs
jobs = [j for j in jobs if j]
print(json.dumps({'include': [{'job': f'j{i:02d}', 'cases': ','.join(j)} for i, j in enumerate(jobs)]}))
