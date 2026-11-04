"""Choose the final trimer from the FDTD retuning sweep (fdtd_sw_L<L>_R<L3>.csv) and freeze the choice in selected.json.
Criterion at 1550 nm: largest far-field directionality ff_py60 / ff_my60 (60 deg cones, the BEM definition) among the candidates
with antenna efficiency eta >= 0.5; ties (within 2%) go to the larger T. If the far field is missing, the box-face ratio
f_py / f_my is used and the choice is marked as such. Once written, selected.json is never changed (resumable runs).
"""
import glob, json, os, re

LAM = 1550.0


def _read(path):
    rows = [l.strip() for l in open(path) if l.strip() and not l.startswith('#')]
    hdr = rows[0].split(','); data = [[float(v) for v in r.split(',')] for r in rows[1:]]
    cols = {h: [r[i] for r in data] for i, h in enumerate(hdr)}
    order = sorted(range(len(data)), key=lambda i: cols['lambda_nm'][i])
    return {h: [cols[h][i] for i in order] for h in hdr}


def _at(c, k, l=LAM):
    x, y = c['lambda_nm'], c[k]
    for i in range(len(x) - 1):
        if x[i] <= l <= x[i + 1]: return y[i] + (y[i + 1] - y[i]) * (l - x[i]) / (x[i + 1] - x[i])
    return float('nan')


def load(out_dir):
    p = os.path.join(out_dir, 'lumerical', 'selected.json')
    return json.load(open(p)) if os.path.exists(p) else None


def make(out_dir, expected):
    """expected: list of (L, L3) of the sweep. Returns the selection (and writes it) or None if no candidate is usable."""
    s = load(out_dir)
    if s: return s
    cand = []
    for L, L3 in expected:
        f = os.path.join(out_dir, 'lumerical', f'fdtd_sw_L{L}_R{L3}.csv')
        if not os.path.exists(f): continue
        try: c = _read(f)
        except Exception: continue
        ff = 'ff_py60' in c and all(v == v for v in c['ff_py60'])
        r = _at(c, 'ff_py60') / _at(c, 'ff_my60') if ff else _at(c, 'f_py') / _at(c, 'f_my')
        cand.append({'L': L, 'L3': L3, 'ratio': r, 'measure': 'far field 60 deg cones' if ff else 'box faces (far field missing)',
                     'eta': _at(c, 'eta'), 'T': _at(c, 'T'), 'Fp': _at(c, 'Fp')})
    ok = [c for c in cand if c['eta'] >= 0.5 and c['ratio'] == c['ratio']]
    if not ok: return None
    best = max(ok, key=lambda c: c['ratio'])
    close = [c for c in ok if c['ratio'] >= 0.98 * best['ratio']]
    best = max(close, key=lambda c: c['T'])
    s = {'L': best['L'], 'L3': best['L3'], 'criterion': 'max +y/-y at 1550 nm with eta >= 0.5 (ties within 2%: larger T)',
         'chosen': best, 'candidates': cand}
    json.dump(s, open(os.path.join(out_dir, 'lumerical', 'selected.json'), 'w'), indent=1)
    return s
