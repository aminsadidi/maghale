"""Print the GitHub Actions matrix (JSON) of pending tasks: one entry per independent FDTD run."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from cases import STAGES
OUT = 'isi/results/ci'
stages = sys.argv[1] if len(sys.argv) > 1 else 'AB'
inc = []
for st in stages:
    for name, p in STAGES[st]:
        if os.path.exists(f'{OUT}/{name}.csv'):
            continue
        for b in range(3):
            for t in ('struct', 'free'):
                inc.append({'case': name, 'band': b, 'tag': t})
print(json.dumps({'include': inc}))
