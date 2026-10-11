"""Quantum emitter inside rod-shaped gold nanoshells (silica core D = 20 nm, length L, shell t; host n = 1.45), BEM
(job_nshell.m). Chunked runs (spec '<geom>_cK') are merged per geometry. Reference: spherical shells (exact-validated),
solid rods of the same outer size (emitter 4 nm beyond the tip) and solid rods tuned to the telecom bands
(telecom_*.csv, same host).
usage: python isi/analysis/nshell.py -> isi/results/nshell.md, isi/figures/fig_nshell.pdf"""
import os, re, glob
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})
C = {4: '#c0392b', 7: '#1f4e9c', 12: '#2a9d5c'}


def load(f):
    return np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1))


def geometry(g):
    fs = sorted(glob.glob(os.path.join(EX, f'nshell_{g}_c*.csv')), key=lambda f: int(re.search(r'_c(\d+)\.csv', f).group(1)))
    if not fs: return None
    d = np.concatenate([load(f) for f in fs]); return d[np.argsort(d['lambda_nm'])]


def summary(d):
    lam = d['lambda_nm']; T = d['T_z_centre']; F = d['Fp_z_centre']; i = np.argmax(T)
    return dict(lamT=lam[i], T=T[i], Fp=F[i], eta=T[i] / F[i], Tside=d['T_z_side4'][i], Tcap=d['T_z_axis_cap4'][i],
                Tx=d['T_x_centre'][i], Fx=d['Fp_x_centre'][i], lamext=lam[np.argmax(d['ext_z'])])


def main():
    geoms = sorted({re.search(r'nshell_(L\d+_t\d+)_c', f).group(1) for f in glob.glob(os.path.join(EX, 'nshell_L*_c*.csv'))},
                   key=lambda g: (int(g.split('_t')[1]), int(g[1:].split('_')[0])))
    S = {}
    out = ['# Emitter inside rod-shaped gold nanoshells (core D = 20 nm, host and core n = 1.45)', '',
           'Centre of the core, axial dipole; values at the radiative peak lambda_T. side/cap: same wavelength, 4 nm from the inner wall / inner cap.', '',
           '| geometry | lambda_T | T | Fp | eta | T side | T cap | T_x (centre) at lambda_T | T at 1310 | T at 1550 |', '|---|---|---|---|---|---|---|---|---|---|']
    for g in geoms:
        d = geometry(g); s = summary(d); S[g] = (d, s); lam = d['lambda_nm']
        t1310 = np.interp(1310, lam, d['T_z_centre']) if lam.max() >= 1310 else np.nan
        t1550 = np.interp(1550, lam, d['T_z_centre']) if lam.max() >= 1550 else np.nan
        out.append(f"| {g} | {s['lamT']:.0f} | {s['T']:.0f} | {s['Fp']:.0f} | {100*s['eta']:.1f}% | {s['Tside']:.0f} | {s['Tcap']:.0f} | {s['Tx']:.2f} | {t1310:.2f} | {t1550:.2f} |")
    out += ['', '## References', '']
    for f in sorted(glob.glob(os.path.join(EX, 'nshell_s*_t*.csv'))):
        tag = re.search(r'nshell_(\w+)\.csv', f).group(1); d = load(f); lam = d['lambda_nm']
        key = 'tip_out' if tag.startswith('solid') else 'centre'
        T, F = d[f'T_z_{key}'], d[f'Fp_z_{key}']; i = np.argmax(T)
        out.append(f'- {tag}: T max {T[i]:.0f} at {lam[i]:.0f} nm, Fp {F[i]:.0f}, eta {100*T[i]/F[i]:.1f}%')
    open(os.path.join(RES, 'nshell.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.7))
    a = ax[0]
    for g in geoms:
        if not g.endswith('_t4'): continue
        d = S[g][0]; a.semilogy(d['lambda_nm'], d['T_z_centre'], lw=1.1, label=g.replace('_t4', '').replace('L', 'L = ') + ' nm')
    for le in (1310, 1550): a.axvline(le, c='0.6', lw=0.8, ls=':')
    a.set_xlabel('wavelength (nm)'); a.set_ylabel(r'$T$ (emitter at centre, axial)'); a.set_title('(a) shell 4 nm', loc='left', fontsize=9)
    a.legend(fontsize=6); a.set_ylim(1e-3, 1e3)
    a = ax[1]
    for t in (4, 7, 12):
        pts = sorted((int(g[1:].split('_')[0]), S[g][1]['lamT']) for g in geoms if g.endswith(f'_t{t}'))
        if pts: a.plot(*zip(*pts), 'o-', c=C[t], ms=3.5, label=f't = {t} nm')
    for le in (1310, 1550): a.axhline(le, c='0.6', lw=0.8, ls=':')
    a.set_xlabel('core length L (nm)'); a.set_ylabel(r'radiative peak $\lambda_T$ (nm)'); a.legend(fontsize=6); a.set_title('(b)', loc='left', fontsize=9)
    a = ax[2]
    for t in (4, 7, 12):
        pts = [(S[g][1]['lamT'], 100 * S[g][1]['eta']) for g in geoms if g.endswith(f'_t{t}')]
        if pts: a.plot(*zip(*sorted(pts)), 'o-', c=C[t], ms=3.5, label=f'shell, t = {t} nm')
    for D, mk in ((20, 's'), (30, '^')):
        fs = glob.glob(os.path.join(EX, 'telecom_L*.csv')) if D == 20 else glob.glob(os.path.join(EX, f'telecom_D{D}L*.csv'))
        pts = []
        for f in fs:
            d = load(f); T, F = d['T_z_g5'], d['Fp_z_g5']; i = np.argmax(T)
            if d['lambda_nm'][i] < d['lambda_nm'].max() - 20: pts.append((d['lambda_nm'][i], 100 * T[i] / F[i]))
        if pts: a.plot(*zip(*sorted(pts)), mk + '--', c='0.4', ms=3.5, mfc='none', lw=0.8, label=f'solid rod D = {D} nm (5 nm outside)')
    a.set_xlabel(r'$\lambda_T$ (nm)'); a.set_ylabel(r'antenna efficiency $\eta_a$ (%)'); a.legend(fontsize=5.5); a.set_title('(c)', loc='left', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_nshell.pdf')); fig.savefig(os.path.join(FIG, 'fig_nshell.png'), dpi=130)


if __name__ == '__main__':
    main()
