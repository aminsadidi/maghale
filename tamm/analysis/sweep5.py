"""Round 5: how much silver has to be lost to reproduce the measured responses? Large cells (P = 0.8 um), 3 realisations, paired with
the as-deposited film of the same realisation (same seed: the remaining grains are a subset of the as-deposited ones).
For every loss level: fraction of the silver volume lost, Ag-on-glass reflectance change (vs Fig. S3c,d) and Tamm-device dip shift and
depth change (zeroth-order cascade on the DBR, as in mechanisms3d.py), compared with the measured PBS / VLP 10 ng/mL responses.
usage: python tamm/analysis/sweep5.py"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'meep'))
import mechanisms3d as M, islands  # noqa: E402
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
LEVELS = [('base', dict()), ('v17', dict(void=0.17)), ('v19', dict(void=0.19)), ('v21', dict(void=0.21)), ('v23', dict(void=0.23)),
          ('cov75', dict(void=0.25)), ('cov65', dict(void=0.35)),
          ('sh97', dict(s=0.97)), ('sh94', dict(s=0.94)), ('shrink90', dict(s=0.90))]
SEEDS = (1, 2, 3)
lam = np.arange(420, 851, 1.0)


def volume(seed, k):
    """silver volume per area (nm) of the film as built in film3d.py"""
    f = islands.make(0.8, seed, void=k.get('void', 0.144))
    s = k.get('s', 1.0)
    if s == 1.0: return 1000 * f['t_mean']
    # lateral and vertical shrinking of every grain: volume scales ~ s^3 (overlaps neglected; exact enough for a label)
    return 1000 * f['t_mean'] * s ** 3


def main():
    B = json.load(open(os.path.join(ROOT, 'results', 'baseline.json')))
    sc = json.load(open(os.path.join(ROOT, 'results', 'mechanisms3d.json')))['scale']
    S3 = {k: np.genfromtxt(os.path.join(ROOT, 'data', f), delimiter=',', names=True) for k, f in (('PBS', 'figS3c_ag_pbs.csv'), ('VLP10', 'figS3d_ag_vlp10.csv'))}
    band = (lam >= 450) & (lam <= 700)
    meas_glass = {}
    for k, d in S3.items():
        d = d[np.argsort(d['lambda_nm'])]
        meas_glass[k] = float(np.mean(np.interp(lam[band], d['lambda_nm'], d['R_after'] - d['R_before'])))
    out = dict(levels={}, measured=dict(PBS=dict(dlam=92.8, dR=2.2, dRglass=meas_glass['PBS']), VLP10=dict(dlam=88.5, dR=15.1, dRglass=meas_glass['VLP10'])),
               scale=sc)
    base = {}
    for s in SEEDS:
        F = M.load(f'LT_base_s{s}_bottom_x'); G = M.load(f'LG_base_s{s}_bottom_x')
        if F and G: base[s] = (M.device_from_film(F, lam, B, sc)[0], M.glass_side(np.interp(lam, G['lam'], G['R'])), volume(s, {}))
    curves = {}
    for tag, k in LEVELS:
        rows = []
        for s in SEEDS:
            F = M.load(f'LT_{tag}_s{s}_bottom_x'); G = M.load(f'LG_{tag}_s{s}_bottom_x')
            if not (F and G and s in base): continue
            Rd = M.device_from_film(F, lam, B, sc)[0]; Rg = M.glass_side(np.interp(lam, G['lam'], G['R']))
            l0, R0 = M.dip(lam, base[s][0], 590, 845); l1, R1 = M.dip(lam, Rd, 590, 845)
            rows.append(dict(seed=s, loss=100 * (1 - volume(s, k) / base[s][2]), dlam=l1 - l0, dR=100 * (R1 - R0),
                             dRglass=100 * float(np.mean((Rg - base[s][1])[band])), R_old_dip=100 * float(np.interp(l0, lam, Rd) - R0)))
            curves.setdefault(tag, []).append(Rd)
        if rows:
            m = {q: float(np.mean([r[q] for r in rows])) for q in ('loss', 'dlam', 'dR', 'dRglass', 'R_old_dip')}
            # ensemble: the measured spot averages over many realisations -> dip of the realisation-mean spectrum (paired seeds)
            Rm = np.mean(curves[tag], 0); Rb = np.mean([base[r['seed']][0] for r in rows], 0)
            (lb, Rb0), (lm, Rm0) = M.dip(lam, Rb, 590, 845), M.dip(lam, Rm, 590, 845)
            m.update(ens_dip=lm, ens_dlam=lm - lb, ens_dR=100 * (Rm0 - Rb0), void=k.get('void', 0.144))
            m.update({q + '_sd': float(np.std([r[q] for r in rows], ddof=1)) if len(rows) > 1 else 0.0 for q in ('dlam', 'dR', 'dRglass')})
            out['levels'][tag] = dict(m, n=len(rows), seeds=rows)
    print(f"{'level':9s} {'void':>5s} {'Ag lost':>8s} {'ens dip':>8s} {'ens dlam':>9s} {'ens dR':>7s} | {'per-seed dlam':>22s} | R at old dip | Ag on glass dR  n")
    for tag, v in out['levels'].items():
        ps = ' '.join('%+6.0f' % r['dlam'] for r in v['seeds'])
        print(f"{tag:9s} {v['void']:5.3f} {v['loss']:7.1f}% {v['ens_dip']:8.1f} {v['ens_dlam']:+9.1f} {v['ens_dR']:+7.1f} | {ps:>22s} | "
              f"{v['R_old_dip']:+11.1f} | {v['dRglass']:+6.1f} +- {v['dRglass_sd']:4.1f}  {v['n']}")
    for k, v in out['measured'].items():
        print(f"measured {k:6s}: dip shift {v['dlam']:+.1f} nm, dR {v['dR']:+.1f} %, Ag on glass dR (450-700 nm) {v['dRglass']:+.1f} %")
    # ---- figure: response vs silver lost
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.4))
    for fam, tags, mk in (('more voids (dissolution of whole grains)', ['base', 'v17', 'v19', 'v21', 'v23', 'cov75', 'cov65'], 'o-'),
                          ('uniform shrinking of all grains', ['base', 'sh97', 'sh94', 'shrink90'], 's--')):
        t = [x for x in tags if x in out['levels']]
        L = [out['levels'][x]['loss'] for x in t]
        for a, q in zip(ax[:2], ('dlam', 'dRglass')):
            a.errorbar(L, [out['levels'][x][q] for x in t], yerr=[out['levels'][x][q + '_sd'] for x in t], fmt=mk, capsize=3, label=fam)
    for k, c in (('PBS', '0.35'), ('VLP10', '#9a3412')):
        ax[0].axhline(out['measured'][k]['dlam'], c=c, ls=':', lw=1.4, label=f'measured {k}')
        ax[1].axhline(out['measured'][k]['dRglass'], c=c, ls=':', lw=1.4, label=f'measured {k}')
    ax[0].set_xlabel('silver volume lost (%)'); ax[0].set_ylabel('Tamm dip shift (nm)'); ax[0].set_title('(a) device: dip shift'); ax[0].legend(fontsize=8)
    ax[1].set_xlabel('silver volume lost (%)'); ax[1].set_ylabel('mean change of R, 450-700 nm (%)'); ax[1].set_title('(b) Ag on glass vs Fig. S3c,d'); ax[1].legend(fontsize=8)
    for tag in ('base', 'v19', 'v23', 'cov75'):
        if tag in curves: ax[2].plot(lam, 100 * np.mean(curves[tag], 0), lw=2 if tag == 'base' else 1.2, c='k' if tag == 'base' else None,
                                     label=f"{tag} ({out['levels'][tag]['loss']:.0f} % lost)")
    ax[2].set_xlim(540, 850); ax[2].set_xlabel('wavelength (nm)'); ax[2].set_ylabel('device R from the glass side (%)')
    ax[2].set_title('(c) device spectra (realisation mean)'); ax[2].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t4_sweep.png')); plt.close(fig)
    json.dump(out, open(os.path.join(ROOT, 'results', 'sweep5.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
