"""Rounds 6 and 7: FULL 3D Tamm device with large cells (island film + DBR + glass in one Meep run, P = 0.8 um, light from the glass side, R and T
from fluxes; no cascade approximation). Realisation-mean spectra (the measured spot averages many realisations); dip position and
depth vs the as-deposited film; compared with the measured PBS / VLP 10 ng/mL spectra (Fig. 2) and with the cascade result (round 5).
usage: python tamm/analysis/fullvol6.py"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import device3d_full as D, mechanisms3d as M  # noqa: E402
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
LEV = [('base', 'as deposited'), ('v21', 'restructured: voids 21 %'), ('cov65', 'restructured: voids 35 %'),
       ('sh94', 'dissolved: grains -6 % (17 % Ag lost)'), ('shrink90', 'dissolved: grains -10 % (27 % Ag lost)'),
       ('FG_g133_40', 'interlayer n 1.33, 40 nm (round 7)'), ('FG_g133_80', 'interlayer n 1.33, 80 nm (round 7)'),
       ('FG_g207_20', 'interlayer AgCl, 20 nm (round 7)'), ('FG_g207_40', 'interlayer AgCl, 40 nm (round 7)')]
lam = D.lam


def main():
    out = dict(levels={})
    spec = {}
    for tag, lab in LEV:
        rs = [D.load(f'{tag}_s{s}_x' if tag.startswith('FG_') else f'FV_{tag}_s{s}_x') for s in (1, 2)]; rs = [r for r in rs if r]
        if not rs: continue
        R = np.mean([r[0] for r in rs], 0); T = np.mean([r[1] for r in rs], 0); spec[tag] = (R, T)
        l, Rd = M.dip(lam, R, 590, 845)
        seeds = [M.dip(lam, r[0], 590, 845) for r in rs]
        out['levels'][tag] = dict(label=lab, n=len(rs), dip=float(l), Rdip=float(Rd), R_at_635=float(np.interp(635, lam, R)),
                                  seeds=[dict(dip=float(a), Rdip=float(b)) for a, b in seeds])
    b = out['levels']['base']
    for tag, v in out['levels'].items():
        v['dlam'] = v['dip'] - b['dip']; v['dR_pct'] = 100 * (v['Rdip'] - b['Rdip']); v['dR_old_dip_pct'] = 100 * (np.interp(b['dip'], lam, spec[tag][0]) - b['Rdip'])
        print(f"{v['label']:42s} n={v['n']} dip {v['dip']:6.1f} nm  R {100*v['Rdip']:5.1f} %  dlam {v['dlam']:+6.1f}  dR {v['dR_pct']:+5.1f}  "
              f"R rise at old dip {v['dR_old_dip_pct']:+5.1f}   seeds: " + ', '.join(f"{s['dip']:.0f}/{100*s['Rdip']:.0f}%" for s in v['seeds']))
    # measured spectra (Fig. 2): before / after
    meas = {}
    for k, f in (('PBS', 'fig2d_vlp0.csv'), ('VLP10', 'fig2c_vlp10.csv')):
        d = np.genfromtxt(os.path.join(ROOT, 'data', f), delimiter=',', names=True); d = d[np.argsort(d['lambda_nm'])]
        rb, ra = np.interp(lam, d['lambda_nm'], d['R_before']) / 100, np.interp(lam, d['lambda_nm'], d['R_after']) / 100
        (l0, r0), (l1, r1) = M.dip(lam, rb, 590, 845), M.dip(lam, ra, 590, 845)
        meas[k] = dict(before=rb, after=ra, dip0=l0, dip1=l1, R0=r0, R1=r1, rise_old=float(np.interp(l0, lam, ra) - r0))
        print(f"measured {k:6s}: dip {l0:.0f} -> {l1:.0f} nm ({l1-l0:+.0f}), R {100*r0:.0f} -> {100*r1:.0f} %, R rise at old dip {100*meas[k]['rise_old']:+.0f} %")
    out['measured'] = {k: {q: float(v[q]) for q in ('dip0', 'dip1', 'R0', 'R1', 'rise_old')} for k, v in meas.items()}
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6))
    for tag, (R, T) in spec.items():
        ax[0].plot(lam, 100 * R, lw=2.2 if tag == 'base' else 1.3, c='k' if tag == 'base' else None, label=out['levels'][tag]['label'])
    ax[0].set_xlim(540, 850); ax[0].set_ylim(0, 100); ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('R from the glass side (%)')
    ax[0].set_title('(a) full 3D device, P = 0.8 um, realisation mean'); ax[0].legend(fontsize=8)
    for k, c in (('PBS', '0.35'), ('VLP10', '#9a3412')):
        ax[1].plot(lam, 100 * meas[k]['before'], c=c, lw=1.2, ls='--'); ax[1].plot(lam, 100 * meas[k]['after'], c=c, lw=2, label=f'{k}: before (dashed) / after')
    ax[1].set_xlim(540, 850); ax[1].set_ylim(0, 100); ax[1].set_xlabel('wavelength (nm)'); ax[1].set_ylabel('R (%)')
    ax[1].set_title('(b) measured (Fig. 2)'); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t5_full_large.png')); plt.close(fig)
    json.dump(out, open(os.path.join(ROOT, 'results', 'fullvol6.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
