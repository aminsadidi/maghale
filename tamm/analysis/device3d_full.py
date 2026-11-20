"""Round 3: full 3D Tamm device (island film + DBR + glass, P = 0.3 um, light from the glass side, R and T from fluxes).
For every silver modification: Tamm dip position and reflectance, shift and depth change vs the as-deposited film, per realisation and
averaged; the incoherent back face of the thick glass is added. Particles: one 100 nm VLP / PS sphere per 0.4 um cell vs the bare film.
usage: python tamm/analysis/device3d_full.py"""
import json, os, sys
import numpy as np, matplotlib
from scipy.interpolate import CubicSpline
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); MEEP = os.path.join(ROOT, 'results', 'meep')
sys.path.insert(0, HERE)
from mechanisms3d import dip, LABEL  # noqa: E402
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
TAGS = ['base', 'agcl3', 'agcl6', 'prot5', 'cov75', 'cov65', 'shrink90', 'thin85', 'dg10', 'dg20']
lam = np.arange(450, 851, 1.0)


def load(n):
    p = os.path.join(MEEP, n + '.npz')
    if not os.path.exists(p): return None
    o = np.load(p); l = o['lam'] * 1000; s = np.argsort(l); l = l[s]
    R, T = o['R'][s], o['T'][s]
    rb = ((1.52 - 1) / 2.52) ** 2                                   # incoherent back face of the thick glass, light from the glass side
    Rg = rb + (1 - rb) ** 2 * R / (1 - rb * R); Tg = (1 - rb) * T / (1 - rb * R)
    return CubicSpline(l, Rg)(lam), CubicSpline(l, Tg)(lam)


def names(tag):
    if tag == 'base': return ['D_s1_bottom_x', 'DV_base_s2_x', 'DV_base_s3_x', 'DV_base_s4_x']
    return [f'DV_{tag}_s1_x', f'DV_{tag}_s2_x']


def main():
    out = dict(per_seed={}, mean={}, particles={})
    spec = {}
    for tag in TAGS:
        rs = [(n, load(n)) for n in names(tag)]; rs = [(n, x) for n, x in rs if x]
        if not rs: continue
        spec[tag] = np.mean([x[0] for n, x in rs], 0)
        out['per_seed'][tag] = {n: dict(zip(('dip', 'Rdip'), map(float, dip(lam, x[0])))) for n, x in rs}
    # paired comparison: same realisation (seeds 1, 2) with and without the modification removes most of the realisation scatter
    b = {1: load('D_s1_bottom_x'), 2: load('DV_base_s2_x')}
    for tag in TAGS[1:]:
        d = []
        for s in (1, 2):
            m = load(f'DV_{tag}_s{s}_x')
            if m and b[s]:
                l0, R0 = dip(lam, b[s][0]); l1, R1 = dip(lam, m[0]); d.append((l1 - l0, 100 * (R1 - R0)))
        if d:
            d = np.array(d); out['mean'][tag] = dict(dlam=float(d[:, 0].mean()), dR_pct=float(d[:, 1].mean()),
                                                     dlam_seeds=d[:, 0].tolist(), dR_seeds=d[:, 1].tolist())
    lb = [v['dip'] for v in out['per_seed']['base'].values()]; Rb = [v['Rdip'] for v in out['per_seed']['base'].values()]
    out['base_scatter'] = dict(dip_mean=float(np.mean(lb)), dip_sd=float(np.std(lb, ddof=1)), R_mean=float(np.mean(Rb)), R_sd=float(np.std(Rb, ddof=1)))
    y = load('DV_base_s1_y')
    if y: out['pol_y'] = dict(zip(('dip', 'Rdip'), map(float, dip(lam, y[0]))))
    ref = load('DV_ref_P40_s1_x')
    for t in ('vlp', 'ps'):
        p = load(f'DV_{t}_P40_s1_x')
        if p and ref:
            l0, R0 = dip(lam, ref[0]); l1, R1 = dip(lam, p[0])
            out['particles'][t] = dict(dlam=float(l1 - l0), dR_pct=float(100 * (R1 - R0)), max_abs_dR_pct=float(100 * np.max(np.abs(p[0] - ref[0]))))
    print(f"as deposited (4 realisations): dip {out['base_scatter']['dip_mean']:.1f} +- {out['base_scatter']['dip_sd']:.1f} nm, "
          f"R {100*out['base_scatter']['R_mean']:.1f} +- {100*out['base_scatter']['R_sd']:.1f} %")
    if 'pol_y' in out: print(f"y polarisation (seed 1): dip {out['pol_y']['dip']:.1f} nm R {100*out['pol_y']['Rdip']:.1f} %")
    for tag, v in out['mean'].items():
        print(f"{LABEL[tag]:28s} dlam {v['dlam']:+6.1f} nm ({', '.join(f'{x:+.1f}' for x in v['dlam_seeds'])})  dR {v['dR_pct']:+5.1f} % ({', '.join(f'{x:+.1f}' for x in v['dR_seeds'])})")
    for t, v in out['particles'].items():
        print(f"particle {t}: dlam {v['dlam']:+.2f} nm, dR {v['dR_pct']:+.2f} %, max |dR| {v['max_abs_dR_pct']:.2f} %")
    meas = dict(PBS=dict(dlam=92.8, dR=2.2), VLP10=dict(dlam=88.5, dR=15.1)); out['measured'] = meas
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6))
    for tag, R in spec.items():
        ax[0].plot(lam, 100 * R, lw=2.2 if tag == 'base' else 1.1, c='k' if tag == 'base' else None, label=LABEL[tag])
    ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('R from the glass side (%)'); ax[0].legend(fontsize=8)
    ax[0].set_title('(a) full 3D Tamm device, realisation mean (P = 0.3 um)')
    for tag, v in out['mean'].items():
        ax[1].errorbar(v['dlam'], v['dR_pct'], xerr=np.ptp(v['dlam_seeds']) / 2, yerr=np.ptp(v['dR_seeds']) / 2, fmt='o', ms=7, capsize=3)
        ax[1].annotate(LABEL[tag], (v['dlam'], v['dR_pct']), fontsize=8, xytext=(4, 3), textcoords='offset points')
    for k, c in (('PBS', '0.4'), ('VLP10', '#9a3412')):
        ax[1].plot(meas[k]['dlam'], meas[k]['dR'], 's', c=c, ms=10); ax[1].annotate('measured: ' + k, (meas[k]['dlam'], meas[k]['dR']), fontsize=9, xytext=(4, 3), textcoords='offset points')
    ax[1].axhline(0, c='0.6', lw=0.8); ax[1].axvline(0, c='0.6', lw=0.8)
    ax[1].set_xlabel('dip shift (nm)'); ax[1].set_ylabel('change of the dip reflectance (%)'); ax[1].set_title('(b) paired response (same realisation)')
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t3_device_full.png')); plt.close(fig)
    json.dump(out, open(os.path.join(ROOT, 'results', 'device3d_full.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
