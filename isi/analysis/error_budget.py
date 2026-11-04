"""Uncertainty budget of the final telecom design (trimer L = 285, R3 = 315 nm horizontal at y = 160 nm), x dipole at the gap centre.
Reference values: BEM at h = 4 nm (job_tri2, R3 mesh 5.6 nm). For each source the change of the key figures is listed:
  peak of T (nm), Fp(1550), T(1550), eta(1550) (percentage points), directionality f(+y)/f(-y) at 1550 nm (60 deg cones).
Sources
  numerics   : mesh h = 5 -> 4 nm (same geometry, job_tri2); mesh 4 -> 2.5 nm and the remaining extrapolation to h -> 0
               (mirror-symmetric job_meshsym runs, R3 meshed at h); mirror-symmetry approximation (dimer, h = 5 nm, full vs symmetric)
  fabrication: R3 length +-10 nm, R3 position y +-10 nm and x + 10 nm, R3 rotation 5 and 10 deg (job_tri2 at h = 5 nm, vs the h = 5 nm design)
  emitter    : displacement 5 nm along x, 10 nm along y (h = 4 nm)
  method     : FDTD (Lumerical) versus BEM, read from isi/results/fdtd_vs_bem.json when it exists (isi/analysis/fdtd_vs_bem.py)
usage: python isi/analysis/error_budget.py -> isi/results/error_budget.md (+ error_budget.json)"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2, meshconv
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); EX = os.path.join(RES, 'bem_extra')
L55 = 1550.0


def at(lam, y, l=L55):
    return float(np.interp(l, lam, y))


def figs(d, p='c'):
    """key figures from a job_tri2 spectrum (x dipole at emitter position p)"""
    lam = d['lambda_nm']; lT, _ = meshconv.peak(lam, d[f'T_x_{p}'])
    Fp, T = at(lam, d[f'Fp_x_{p}']), at(lam, d[f'T_x_{p}'])
    return {'lT': lT, 'Fp': Fp, 'T': T, 'eta': T / Fp, 'ratio': at(lam, d[f'f_py60_x_{p}']) / at(lam, d[f'f_my60_x_{p}'])}


def figs_sym(d):
    lam = d['lambda_nm']; lT, _ = meshconv.peak(lam, d['T_x']); Fp, T = at(lam, d['Fp_x']), at(lam, d['T_x'])
    return {'lT': lT, 'Fp': Fp, 'T': T, 'eta': T / Fp, 'ratio': None}


def delta(a, b):
    """change b - a in the units of the table"""
    out = {'lT': b['lT'] - a['lT'], 'Fp': 100 * (b['Fp'] / a['Fp'] - 1), 'T': 100 * (b['T'] / a['T'] - 1), 'eta': 100 * (b['eta'] - a['eta'])}
    out['ratio'] = 100 * (b['ratio'] / a['ratio'] - 1) if a.get('ratio') and b.get('ratio') else None
    return out


def fmt(v, kind):
    if v is None: return 'n/a'
    if isinstance(v, str): return v
    return {'lT': f'{v:+.0f} nm', 'eta': f'{v:+.1f} pp'}.get(kind, f'{v:+.1f}%')


def trimer_mesh():
    """mesh-study series of the trimer (R3 meshed at h): {h: spectrum}"""
    S = {h: v[0] for h, v in meshconv.spectra('T_L285_R315_Y160').items() if v[1] == 6}
    for h, v in meshconv.spectra('Q_L285_R315_Y160').items():
        if v[1] == 6 and h not in S: S[h] = v[0]
    return dict(sorted(S.items()))


def order_fit(h, y, pmin=0.5, pmax=2.0):
    """y = y0 + b h^p, p scanned in [pmin, pmax]; returns (p, y0)"""
    best = None
    for p in np.arange(pmin, pmax + 1e-9, 0.01):
        c = np.polyfit(h ** p, y, 1); r = np.sum((np.polyval(c, h ** p) - y) ** 2)
        if best is None or r < best[0]: best = (r, p, c[1])
    return best[1], best[2]


def main():
    ref, nc = tri2.series('L285_R315_A0_Y160_H4'); base5, nc5 = tri2.series('L285_R315_A0_Y160')
    if ref is None or nc < 6 or base5 is None or nc5 < 6: sys.exit('final-design spectra incomplete')
    R4, R5 = figs(ref), figs(base5)
    rows = []                                                   # (group, source, deltas)
    rows.append(('numerics', 'mesh h = 5 -> 4 nm (full geometry)', delta(R5, R4)))
    # ---- finer meshes (mirror-symmetric study) --------------------------------------------------------------------
    S = trimer_mesh(); hs = np.array(sorted(S)); F = {h: figs_sym(S[h]) for h in hs}
    hf = hs.min()
    rows.append(('numerics', f'mesh h = 4 -> {hf:g} nm (symmetric runs)', delta(F[4.0], F[hf])))
    # remaining shift to h -> 0: peak wavelength extrapolated with an h^2 law and with the fitted order (h <= 4 nm);
    # Fp, T, eta at 1550 nm propagated by shifting the finest spectrum rigidly by that amount (checked below on 3 -> 2.5 nm)
    sel = hs <= 4.0; lp = np.array([F[h]['lT'] for h in hs])
    l_h2 = np.polyfit(hs[sel] ** 2, lp[sel], 1)[1]; p_fit, l_p = order_fit(hs[sel], lp[sel])
    d_f = S[hf]; lam = d_f['lambda_nm']
    def shifted(dl):
        Fp, T = at(lam, d_f['Fp_x'], L55 - dl), at(lam, d_f['T_x'], L55 - dl)
        return {'lT': F[hf]['lT'] + dl, 'Fp': Fp, 'T': T, 'eta': T / Fp, 'ratio': None}
    lo, hi = sorted((l_h2 - F[hf]['lT'], l_p - F[hf]['lT']))
    dlo, dhi = delta(F[hf], shifted(lo)), delta(F[hf], shifted(hi))
    rows.append(('numerics', f'remaining, h = {hf:g} nm -> 0 (h^2 law ... fitted order p = {p_fit:.2f})',
                 {k: (f'{fmt(dlo[k], k)} ... {fmt(dhi[k], k)}' if dlo[k] is not None else None) for k in dlo}))
    # check of the rigid-shift propagation on the last computed mesh step
    hp = hs[1]; dl = F[hf]['lT'] - F[hp]['lT']; lamp = S[hp]['lambda_nm']
    pred = at(lamp, S[hp]['Fp_x'], L55 - dl); obs = F[hf]['Fp']
    check = (f'rigid-shift check, h = {hp:g} -> {hf:g} nm: peak moves {dl:+.1f} nm; Fp(1550) predicted {pred:.1f}, computed {obs:.1f} '
             f'({100*(pred/obs-1):+.1f}%)')
    # mirror symmetry (pure check on the dimer: same mesh, full vs symmetric)
    mfile = os.path.join(EX, 'tri2_L285_M.csv'); Ssym = meshconv.spectra('D_L285')
    if os.path.exists(mfile) and 5.0 in Ssym:
        full = meshconv.load(mfile); sym = Ssym[5.0][0]
        dev = [100 * (at(sym['lambda_nm'], sym['Fp_x'], l) / float(full['Fp_x_c'][list(full['lambda_nm']).index(l)]) - 1) for l in full['lambda_nm']]
        rows.append(('numerics', 'mirror symmetry (dimer, h = 5 nm, symmetric vs full)',
                     {'lT': 'n/a', 'Fp': f'{min(dev):+.1f} ... {max(dev):+.1f}% (1310-1660 nm)', 'T': 'n/a', 'eta': 'n/a', 'ratio': None}))
    # ---- fabrication ---------------------------------------------------------------------------------------------------------
    for stem, lab in (('L285_R305_A0_Y160', 'R3 length 315 -> 305 nm'), ('L285_R325_A0_Y160', 'R3 length 315 -> 325 nm'),
                      ('L285_R315_A0_Y150', 'R3 position y 160 -> 150 nm'), ('L285_R315_A0_Y170', 'R3 position y 160 -> 170 nm'),
                      ('L285_R315_A0_X10_Y160', 'R3 position x 0 -> 10 nm'), ('L285_R315_A5_Y160', 'R3 rotated by 5 deg'),
                      ('L285_R315_A10_Y160', 'R3 rotated by 10 deg')):
        d, n = tri2.series(stem)
        if d is not None and n == 6: rows.append(('fabrication (h = 5 nm)', lab, delta(R5, figs(d))))
    # ---- emitter -------------------------------------------------------------------------------------------------------------
    for p, lab in (('px5', 'emitter 5 nm along x'), ('py10', 'emitter 10 nm along y')):
        rows.append(('emitter (h = 4 nm)', lab, delta(R4, figs(ref, p))))
    # ---- method --------------------------------------------------------------------------------------------------------------
    fj = os.path.join(RES, 'fdtd_vs_bem.json')
    if os.path.exists(fj):
        m = json.load(open(fj)).get('trimer')
        if m: rows.append(('method', 'FDTD (Lumerical, 1 nm gap mesh) vs BEM', {k: m.get(k) for k in ('lT', 'Fp', 'T', 'eta', 'ratio')}))
    else:
        rows.append(('method', 'FDTD (Lumerical) vs BEM', {k: 'pending' for k in ('lT', 'Fp', 'T', 'eta', 'ratio')}))

    out = ['# Uncertainty budget of the final design (trimer L = 285, R3 = 315 nm horizontal at y = 160 nm)', '',
           f"Reference (BEM, h = 4 nm, x dipole at the gap centre): peak of T at {R4['lT']:.0f} nm; at 1550 nm Fp = {R4['Fp']:.0f}, "
           f"T = {R4['T']:.0f}, eta = {R4['eta']:.1%}, f(+y)/f(-y) = {R4['ratio']:.2f}.", '',
           'Entries are changes relative to the reference (fabrication rows: relative to the same design at h = 5 nm, '
           f"peak {R5['lT']:.0f} nm, Fp(1550) {R5['Fp']:.0f}, ratio {R5['ratio']:.2f}). n/a: quantity not available from that run.", '',
           '| group | source | peak of T | Fp(1550) | T(1550) | eta(1550) | f(+y)/f(-y) (1550) |', '|---|---|---|---|---|---|---|']
    for g, s, dd in rows:
        out.append(f'| {g} | {s} | ' + ' | '.join(fmt(dd.get(k), k) for k in ('lT', 'Fp', 'T', 'eta', 'ratio')) + ' |')
    out += ['', 'Notes', f'- {check}.',
            f'- Peak of T in the symmetric mesh study: h = 4 nm {F[4.0]["lT"]:.1f} nm, h = {hf:g} nm {F[hf]["lT"]:.1f} nm; extrapolated '
            f'{l_h2:.1f} nm (h^2) and {l_p:.1f} nm (fitted order p = {p_fit:.2f}).',
            '- The symmetric runs mesh R3 at h, the full runs at 1.4 h; their absolute values differ by a few per cent, so only changes are used.',
            '- The efficiency eta and the directionality are the least mesh-sensitive figures; Fp(1550) is sensitive because 1550 nm lies on the',
            '  red flank of the resonance, where a few nm of peak shift change Fp by several per cent.',
            '- Not included: gold permittivity (only Johnson-Christy computed for this design), substrate, rounding of the rod ends, nonlocality.']
    open(os.path.join(RES, 'error_budget.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
    json.dump({'reference': R4, 'rows': [{'group': g, 'source': s, **{k: v for k, v in dd.items()}} for g, s, dd in rows]},
              open(os.path.join(RES, 'error_budget.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
