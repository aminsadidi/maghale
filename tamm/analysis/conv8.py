"""Round 8: grid convergence of the full device (P = 0.4 um) without / with the 40 nm AgCl interlayer, grid 5 nm (res 200) vs 3.3 nm (res 300).
usage: python tamm/analysis/conv8.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import device3d_full as D, mechanisms3d as M  # noqa: E402
lam = D.lam
out = {}
for r in (200, 300):
    sp = {}
    for tag in ('base', 'g207_40'):
        rs = [D.load(f'CV_{tag}_r{r}_s{s}_x') for s in (1, 2)]; rs = [x for x in rs if x]
        if rs: sp[tag] = (np.mean([x[0] for x in rs], 0), len(rs))
    if len(sp) < 2: continue
    (l0, R0), (l1, R1) = M.dip(lam, sp['base'][0], 590, 845), M.dip(lam, sp['g207_40'][0], 590, 845)
    out[r] = dict(n=[sp['base'][1], sp['g207_40'][1]], dip0=l0, R0=100*R0, dip1=l1, R1=100*R1, dlam=l1-l0, dR=100*(R1-R0),
                  rise_old=100*float(np.interp(l0, lam, sp['g207_40'][0]) - R0))
    print(r, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in out[r].items()})
if 200 in out and 300 in out:
    a, b = M_ = out[200], out[300]
    print('difference r300-r200: dip0 %+.1f nm, dlam %+.1f nm, dR %+.1f %%, rise %+.1f %%' % (b['dip0']-a['dip0'], b['dlam']-a['dlam'], b['dR']-a['dR'], b['rise_old']-a['rise_old']))
    R2 = {}
    for r in (200, 300):
        R2[r] = np.mean([D.load(f'CV_base_r{r}_s{s}_x')[0] for s in (1, 2) if D.load(f'CV_base_r{r}_s{s}_x')], 0)
    m = (lam >= 450) & (lam <= 850); d = np.abs(R2[300] - R2[200])[m]
    print('base spectrum |dR| mean %.3f max %.3f' % (d.mean(), d.max()))
json.dump(out, open(os.path.join(ROOT, 'results', 'conv8.json'), 'w'), indent=1, default=float)
