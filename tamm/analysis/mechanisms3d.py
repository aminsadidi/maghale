"""Which change of the silver film explains the measured response? Large-cell 3D results (round 4, P = 0.8 um, 2 realisations).

(1) Ag on glass (LG_*): reflectance from the glass side (thick glass, front face incoherent) vs Fig. S3c,d (Ag film before / after PBS
    and VLP); every modification gives a change dR(lambda) to compare with the measured change.
(2) Tamm device: the specular reflection of the film seen from the TiO2 side (LT_*, r from below, reference at the film bottom) is
    terminated on the planar DBR (fit of Fig. 1) and the glass; device R and T from the glass side, Tamm dip position and depth,
    and dlambda, dR, alpha = atan(dR[%] / dlambda[nm]) for every modification, compared with the measured PBS / VLP response.
    Diffuse light scattered by the film is not returned in this specular cascade (it acts as a loss); this is stated in the report.
usage: python tamm/analysis/mechanisms3d.py"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); ROOT = os.path.join(HERE, '..')
import tmm, cascade as C  # noqa: E402
MEEP = os.path.join(ROOT, 'results', 'meep')
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
TAGS = ['base', 'agcl3', 'agcl6', 'prot5', 'cov75', 'cov65', 'shrink90', 'thin85', 'dg10', 'dg20']
LABEL = dict(base='as deposited', agcl3='AgCl shell 3 nm', agcl6='AgCl shell 6 nm', prot5='protein shell 5 nm', cov75='coverage 75 %',
             cov65='coverage 65 %', shrink90='grains -10 % (dissolution)', thin85='heights -15 %', dg10='damping +0.10 eV', dg20='damping +0.20 eV')
SEEDS = (1, 2)


def load(n):
    p = os.path.join(MEEP, n + '.npz')
    if not os.path.exists(p): return None
    o = np.load(p); lam = o['lam'] * 1000; s = np.argsort(lam)
    return dict(lam=lam[s], r=o['r'][s], t=o['t'][s], R=o['R'][s], T=o['T'][s])


def glass_side(R, ng=1.52):
    rb = ((ng - 1) / (ng + 1)) ** 2
    return rb + (1 - rb) ** 2 * R / (1 - rb * R)


def device_from_film(F, lam, B, scale):
    """light from the glass: glass | DBR (from the glass side) | TiO2 | film (r, t from below) | air"""
    d = B['dbr']; sio = tmm.porous(tmm.SiO2, tmm.AIR, d['pS'])(lam); tio = tmm.porous(tmm.TiO2, tmm.AIR, d['pT'])(lam)
    first = d['first']                                       # first layer on the glass
    pair = [(sio, d['dS'] * scale), (tio, d['dT'] * scale)] if first == 'SiO2' else [(tio, d['dT'] * scale), (sio, d['dS'] * scale)]
    ng = tmm.BK7(lam); S = []; n_prev = ng
    for n, t in pair * 5:
        S += [C.interface(n_prev, n), C.layer(n, t, lam)]; n_prev = n
    nb = np.full(len(lam), 1.93 + 0j)
    S.append(C.interface(n_prev, nb))
    r = np.interp(lam, F['lam'], F['r'].real) + 1j * np.interp(lam, F['lam'], F['r'].imag)
    t = np.interp(lam, F['lam'], F['t'].real) + 1j * np.interp(lam, F['lam'], F['t'].imag)
    z = 0 * r
    S.append((r, t, z, z, nb, np.ones(len(lam), complex)))
    Sx = C.chain(*S)
    Rc = np.abs(Sx[0]) ** 2; Tc = 1.0 / ng.real * np.abs(Sx[1]) ** 2
    rb = ((ng.real - 1) / (ng.real + 1)) ** 2
    return rb + (1 - rb) ** 2 * Rc / (1 - rb * Rc), (1 - rb) * Tc / (1 - rb * Rc)


def dip(lam, R, lo=540, hi=760):
    m = (lam > lo) & (lam < hi); i = np.argmin(np.where(m, R, 9))
    if 0 < i < len(lam) - 1:                                  # parabolic refinement
        a, b, c = R[i - 1], R[i], R[i + 1]; s = float(np.clip(0.5 * (a - c) / (a - 2 * b + c), -1, 1)) if (a - 2 * b + c) > 0 else 0.0
        return lam[i] + s * (lam[1] - lam[0]), b - 0.25 * (a - c) * s
    return lam[i], R[i]


def main():
    B = json.load(open(os.path.join(ROOT, 'results', 'baseline.json')))
    lam = np.arange(420, 851, 1.0); out = dict(glass={}, device={})
    # ---- (1) Ag on glass
    S3 = {k: np.genfromtxt(os.path.join(ROOT, 'data', f), delimiter=',', names=True) for k, f in (('PBS', 'figS3c_ag_pbs.csv'), ('VLP10', 'figS3d_ag_vlp10.csv'))}
    G = {}
    for tag in TAGS:
        rs = [load(f'LG_{tag}_s{s}_bottom_x') for s in SEEDS]; rs = [r for r in rs if r]
        if rs: G[tag] = np.mean([glass_side(np.interp(lam, r['lam'], r['R'])) for r in rs], 0)
    if 'base' in G:
        for tag in G:
            out['glass'][tag] = {f'R{l}': float(np.interp(l, lam, G[tag])) for l in (450, 550, 650, 750)}
            out['glass'][tag].update({f'dR{l}': float(np.interp(l, lam, G[tag] - G['base'])) for l in (450, 550, 650, 750)})
        for k, d in S3.items():
            d = d[np.argsort(d['lambda_nm'])]
            out['glass']['meas_' + k] = {f'R{l}': float(np.interp(l, d['lambda_nm'], d['R_before'])) / 100 for l in (450, 550, 650, 750)}
            out['glass']['meas_' + k].update({f'dR{l}': float(np.interp(l, d['lambda_nm'], d['R_after'] - d['R_before'])) / 100 for l in (450, 550, 650, 750)})
    # ---- (2) device
    D = {}
    for tag in TAGS:
        per = []
        for s in SEEDS:
            F = load(f'LT_{tag}_s{s}_bottom_x')
            if F: per.append(device_from_film(F, lam, B, 1.0))
        if per: D[tag] = (np.mean([p[0] for p in per], 0), np.mean([p[1] for p in per], 0), per)
    if 'base' in D:
        # DBR thickness scale so that the as-deposited film puts the dip where the Fig. 1 device has it (635 nm)
        F_base = [load(f'LT_base_s{s}_bottom_x') for s in SEEDS]
        best = min(np.arange(0.9, 1.1, 0.0025), key=lambda sc: abs(dip(lam, np.mean([device_from_film(F, lam, B, sc)[0] for F in F_base if F], 0))[0] - 635))
        out['scale'] = float(best)
        D = {}
        for tag in TAGS:
            per = [device_from_film(F, lam, B, best) for F in [load(f'LT_{tag}_s{s}_bottom_x') for s in SEEDS] if F]
            if per: D[tag] = (np.mean([p[0] for p in per], 0), np.mean([p[1] for p in per], 0), per)
        l0, R0 = dip(lam, D['base'][0])
        for tag, (R, T, per) in D.items():
            l1, R1 = dip(lam, R)
            seeds = [dip(lam, p[0]) for p in per]
            dl, dR = l1 - l0, 100 * (R1 - R0)
            out['device'][tag] = dict(dip=l1, Rdip=R1, dlam=dl, dR_pct=dR, alpha_deg=float(np.degrees(np.arctan2(dR, dl))) if tag != 'base' else 0.0,
                                      seeds=[dict(dip=a, Rdip=b) for a, b in seeds])
        print(f"DBR scale {best:.4f}; as deposited: dip {l0:.1f} nm, R {100*R0:.1f} %")
        for tag, v in out['device'].items():
            print(f"{LABEL[tag]:28s} dip {v['dip']:6.1f} nm  R {100*v['Rdip']:5.1f} %  dlam {v['dlam']:+6.1f} nm  dR {v['dR_pct']:+5.1f} %  alpha {v['alpha_deg']:+6.1f} deg")
        meas = dict(PBS=dict(dlam=92.8, dR=2.2), VLP10=dict(dlam=88.5, dR=15.1))   # means of Fig. 2a,b / Fig. 3 (PBS: 5 tests, VLP10: 2)
        out['measured'] = meas
        fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6))
        for tag, (R, T, per) in D.items():
            ax[0].plot(lam, 100 * R, lw=2.2 if tag == 'base' else 1.2, c='k' if tag == 'base' else None, label=LABEL[tag])
        ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('R from the glass side (%)'); ax[0].set_xlim(420, 850); ax[0].legend(fontsize=8)
        ax[0].set_title('(a) Tamm device with modified island films (3D, P = 0.8 um)')
        for tag, v in out['device'].items():
            if tag == 'base': continue
            ax[1].plot(v['dlam'], v['dR_pct'], 'o', ms=8); ax[1].annotate(LABEL[tag], (v['dlam'], v['dR_pct']), fontsize=8, xytext=(4, 3), textcoords='offset points')
        ax[1].plot(meas['PBS']['dlam'], meas['PBS']['dR'], 's', c='0.4', ms=10); ax[1].annotate('measured: PBS', (meas['PBS']['dlam'], meas['PBS']['dR']), fontsize=9, xytext=(4, -10), textcoords='offset points')
        ax[1].plot(meas['VLP10']['dlam'], meas['VLP10']['dR'], 's', c='#9a3412', ms=10); ax[1].annotate('measured: VLP 10 ng/mL', (meas['VLP10']['dlam'], meas['VLP10']['dR']), fontsize=9, xytext=(4, 3), textcoords='offset points')
        ax[1].axhline(0, c='0.6', lw=0.8); ax[1].axvline(0, c='0.6', lw=0.8)
        ax[1].set_xlabel('dip shift (nm)'); ax[1].set_ylabel('change of the dip reflectance (%)'); ax[1].set_title('(b) response map: model vs experiment')
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t3_mechanisms.png')); plt.close(fig)
    json.dump(out, open(os.path.join(ROOT, 'results', 'mechanisms3d.json'), 'w'), indent=1, default=float)
    for k, v in out['glass'].items():
        print('glass', f'{k:12s}', ' '.join(f"{100*v[f'R{l}']:5.1f}" for l in (450, 550, 650, 750)), '| dR', ' '.join(f"{100*v[f'dR{l}']:+5.1f}" for l in (450, 550, 650, 750)))


if __name__ == '__main__':
    main()
