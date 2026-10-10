"""Khatua et al. (2014) comparison: effect of surface damping and of the glass substrate on the dependence of the
maximum fluorescence enhancement on the resonance wavelength (job_khvar.m) versus the homogeneous JC model
(job_khatua.m) and the digitised measurements (isi/data/khatua2014_fig5.csv).
The resonance (SPR) is taken as the radiative peak of the axial dipole at a 10 nm gap for all variants (the substrate
runs have no extinction); for the homogeneous model this differs from the extinction maximum by <= 5 nm.
usage: python isi/analysis/khatua_variants.py -> isi/results/khatua_variants.md, isi/figures/fig_khatua_var.pdf"""
import os, re, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})
Q0 = 0.0228; GAPS = (3, 5, 7, 10)


def xi_curve(pattern, key_re):
    out = []
    for f in sorted(glob.glob(os.path.join(RES, 'bem_extra', pattern)), key=lambda f: int(re.search(r'_L(\d+)', f).group(1))):
        L = int(re.search(r'_L(\d+)', f).group(1)); meta = open(f).readline()
        d = np.genfromtxt(f, delimiter=',', names=True, skip_header=1); lam = d['lambda_nm']
        e594 = [float(x) for x in re.search(r'594 nm: ([\d.e+\- ]+);', meta).group(1).split()]
        e633 = [float(x) for x in re.search(r'633 nm: ([\d.e+\- ]+)', meta).group(1).split()]
        spr = lam[np.argmax(d['T_g10'])]
        w = np.exp(-0.5 * ((lam - 640) / (60 / 2.355)) ** 2); w /= w.sum()
        for gi, g in enumerate(GAPS):
            F, T = d[f'Fp_g{g}'], d[f'T_g{g}']
            Eem = np.sum(w * T / (F + (1 - Q0) / Q0)) / Q0
            out.append((L, spr, g, e594[gi] * Eem, e633[gi] * Eem, e633[gi], Eem))
    return np.array(out)


def main():
    V = {'JC, homogeneous': xi_curve('khatua_L*.csv', None), 'JC + surface damping': xi_curve('khvar_L*_surf.csv', None),
         'on glass (substrate)': xi_curve('khvar_L*_sub.csv', None)}
    x = np.genfromtxt(os.path.join(HERE, '..', 'data', 'khatua2014_fig5.csv'), delimiter=',', names=True, skip_header=4)
    out = ['# Khatua comparison: surface damping and substrate', '',
           'SPR = radiative peak at 10 nm gap; xi = E_exc * E_em (dipole on the axis, along it).', '']
    for lab, K in V.items():
        out += [f'## {lab}', '', '| L | SPR | gap | xi(594) | xi(633) | E_exc(633) | E_em |', '|---|---|---|---|---|---|---|']
        for r in K:
            if r[2] in (3, 5): out.append(f'| {r[0]:.0f} | {r[1]:.0f} | {r[2]:.0f} | {r[3]:.0f} | {r[4]:.0f} | {r[5]:.0f} | {r[6]:.1f} |')
        out.append('')
        for g in (3, 5):
            m = K[:, 2] == g; o = np.argsort(K[m, 1]); s = K[m, 1][o]
            for ex, col in ((633, 4), (594, 3)):
                sel = (x['excitation_nm'] == ex) & (x['spr_nm'] >= s.min()) & (x['spr_nm'] <= s.max())
                pred = np.exp(np.interp(x['spr_nm'][sel], s, np.log(K[m, col][o])))
                r = x['xi'][sel] / pred
                out.append(f'- gap {g}, {ex} nm: n={sel.sum()}, measured/model median {np.median(r):.2f}, range {r.min():.2f}-{r.max():.2f}, rms log10 {np.sqrt(np.mean(np.log10(r)**2)):.2f}; max model {K[m, col].max():.0f}')
        out.append('')
    open(os.path.join(RES, 'khatua_variants.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.6), sharey=True)
    st = {'JC, homogeneous': ('-', '#1f4e9c'), 'JC + surface damping': ('--', '#2a9d5c'), 'on glass (substrate)': (':', '#c0392b')}
    for a, (ex, col, t) in zip(ax, ((633, 4, '633 nm excitation'), (594, 3, '594 nm excitation'))):
        for lab, K in V.items():
            m = K[:, 2] == 5; o = np.argsort(K[m, 1])
            a.semilogy(K[m, 1][o], K[m, col][o], st[lab][0], c=st[lab][1], label=lab + ', 5 nm')
        sel = x['excitation_nm'] == ex
        a.plot(x['spr_nm'][sel], x['xi'][sel], '*', c='k', ms=6, label='experiment')
        a.set_xlabel('resonance wavelength (nm)'); a.set_title(t, fontsize=9); a.set_xlim(575, 745)
    ax[0].set_ylabel(r'fluorescence enhancement $\xi$'); ax[0].legend(fontsize=6); ax[0].set_ylim(1, 4000)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_khatua_var.pdf')); fig.savefig(os.path.join(FIG, 'fig_khatua_var.png'), dpi=130)


if __name__ == '__main__':
    main()
