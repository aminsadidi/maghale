"""Figures of the Tamm-study report (tamm/figures/fig_r*.png).
usage: python tamm/analysis/report_figs.py"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'meep'))
import device3d_full as D, mechanisms3d as M, islands  # noqa: E402
FIG = os.path.join(ROOT, 'figures')
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6', 'font.family': 'DejaVu Sans'})
lam = D.lam
C = dict(meas='#1d2330', pbs='#4a5263', vlp='#9a3412', base='#111111', ag='#1f4e9c', inter='#2a7a4b', shell='#b8892a')


def measured():
    out = {}
    for k, f in (('PBS', 'fig2d_vlp0.csv'), ('VLP 10 ng/mL', 'fig2c_vlp10.csv')):
        d = np.genfromtxt(os.path.join(ROOT, 'data', f), delimiter=',', names=True); d = d[np.argsort(d['lambda_nm'])]
        out[k] = (np.interp(lam, d['lambda_nm'], d['R_before']), np.interp(lam, d['lambda_nm'], d['R_after']))
    return out


def mean_dev(names):
    rs = [D.load(n) for n in names]; rs = [r for r in rs if r]
    return 100 * np.mean([r[0] for r in rs], 0) if rs else None


def fig_problem(meas):
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.0), sharey=True)
    for a, (k, (b, af)) in zip(ax, meas.items()):
        a.plot(lam, b, c='0.55', lw=1.6, ls='--', label='before'); a.plot(lam, af, c=C['vlp'] if 'VLP' in k else C['pbs'], lw=2.4, label='after')
        (l0, r0), (l1, r1) = M.dip(lam, b / 100, 590, 845), M.dip(lam, af / 100, 590, 845)
        a.annotate('', xy=(l1, 100 * r1 - 3), xytext=(l0, 100 * r0 - 3), arrowprops=dict(arrowstyle='->', lw=1.6, color='k'))
        a.text(0.5 * (l0 + l1), min(r0, r1) * 100 - 9, f'{l1 - l0:+.0f} nm', ha='center', fontsize=11, fontweight='bold')
        a.set_title(f'measured Tamm device: {k} (Rossini et al., Fig. 2)'); a.set_xlim(540, 850); a.set_ylim(0, 100); a.set_xlabel('wavelength (nm)')
        a.legend(loc='upper right')
    ax[0].set_ylabel('reflectance (%)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_r1_problem.png')); plt.close(fig)


def fig_model():
    f = islands.make(0.8, 1)
    fig = plt.figure(figsize=(13, 4.3)); g = fig.add_gridspec(1, 2, width_ratios=[1, 1.35])
    a = fig.add_subplot(g[0]); im = a.imshow(1000 * f['Hmap'].T, origin='lower', extent=[0, 800, 0, 800], cmap='cividis')
    a.set_title(f"(a) random Ag island film, 0.8 x 0.8 um cell\n{len(f['grains'])} grains, coverage {100*f['coverage']:.0f} %, mean thickness {1000*f['t_mean']:.0f} nm")
    a.set_xlabel('x (nm)'); a.set_ylabel('y (nm)'); a.grid(False); fig.colorbar(im, ax=a, label='height (nm)', fraction=0.046)
    b = fig.add_subplot(g[1]); b.set_xlim(0, 10); b.set_ylim(-0.4, 10.6); b.axis('off'); b.set_title('(b) simulated structure (one Meep run, light from the glass side)')
    y = 0.0
    b.add_patch(Rectangle((1, y), 8, 1.4, fc='#dfe7f2', ec='0.5')); b.text(5, y + 0.7, 'glass (n = 1.52)', ha='center', va='center'); y += 1.4
    for i in range(5):
        b.add_patch(Rectangle((1, y), 8, 0.55, fc='#f2efe6', ec='0.6')); y += 0.55
        b.add_patch(Rectangle((1, y), 8, 0.45, fc='#c9d3e3', ec='0.6')); y += 0.45
    b.text(9.15, 1.4 + 1.6, 'DBR: 5 x (SiO$_2$ 98 nm /\nTiO$_2$ 73 nm), fit of Fig. 1', va='center', fontsize=9)
    gap = y
    b.add_patch(Rectangle((1, y), 8, 0.5, fc='#d9efe1', ec=C['inter'], ls='--')); b.text(9.15, y - 0.2, 'interlayer (round 7):\nAgCl or hydrated, 20-80 nm', va='top', fontsize=9, color=C['inter']); y += 0.5
    rng = np.random.default_rng(3); x = 1.1
    while x < 8.8:
        w = rng.uniform(0.35, 0.8); h = rng.uniform(0.55, 0.9)
        b.add_patch(Rectangle((x, y), w, 0.8 * h, fc='#b0b4bb', ec='0.35')); b.add_patch(Ellipse((x + w / 2, y + 0.8 * h), w, 0.4 * h, fc='#b0b4bb', ec='0.35'))
        x += w + rng.uniform(0.0, 0.25)
    b.text(9.15, y + 0.6, 'Ag islands, 33 nm\n(AFM statistics)', va='bottom', fontsize=9); b.text(5, y + 1.6, 'air', ha='center', color='0.4')
    b.annotate('', xy=(0.5, 2.5), xytext=(0.5, -0.3), arrowprops=dict(arrowstyle='->', lw=2, color=C['vlp'])); b.text(0.15, 1.0, 'light', rotation=90, color=C['vlp'], va='center')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_r2_model.png')); plt.close(fig)


def fig_glass(meas_glass):
    """Ag on glass: mean change of R over 450-700 nm, each modification vs the as-deposited film (same realisations)"""
    band = (lam >= 450) & (lam <= 700)
    def dRg(tag, seeds):
        v = []
        for s in seeds:
            a, b = M.load(f'LG_{tag}_s{s}_bottom_x'), M.load(f'LG_base_s{s}_bottom_x')
            if a and b: v.append(100 * np.mean((M.glass_side(np.interp(lam, a['lam'], a['R'])) - M.glass_side(np.interp(lam, b['lam'], b['R'])))[band]))
        return (np.mean(v), np.std(v)) if v else (np.nan, 0)
    rows = [('AgCl shell 3 nm', 'agcl3', C['shell']), ('AgCl shell 6 nm', 'agcl6', C['shell']), ('protein shell 5 nm', 'prot5', C['shell']),
            ('damping +0.1 eV', 'dg10', '#7a8191'), ('damping +0.2 eV', 'dg20', '#7a8191'),
            ('restructured, voids 21 %', 'v21', C['ag']), ('restructured, voids 25 %', 'cov75', C['ag']), ('restructured, voids 35 %', 'cov65', C['ag']),
            ('dissolved, 17 % Ag lost', 'sh94', C['ag']), ('dissolved, 27 % Ag lost', 'shrink90', C['ag'])]
    vals = [dRg(t, (1, 2, 3)) for _, t, _ in rows]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [v[0] for v in vals], xerr=[v[1] for v in vals], color=[c for _, _, c in rows], height=0.62, capsize=3)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
    for k, c in (('PBS', C['pbs']), ('VLP 10 ng/mL', C['vlp'])):
        ax.axvline(meas_glass[k], c=c, lw=2, ls=':'); ax.text(meas_glass[k] + 0.2, -0.9, f'measured {k}', color=c, ha='left', fontsize=9, fontweight='bold')
    ax.axvline(0, c='0.3', lw=0.8); ax.set_xlabel('change of R of Ag on glass, mean 450-700 nm (%)')
    ax.set_ylim(-1.3, len(rows) - 0.4); ax.set_title('Ag film on glass (Fig. S3c,d): shells raise R (wrong sign); damping, loss and restructuring lower it', fontsize=10.5)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_r3_glass.png')); plt.close(fig)
    return {t: v for (_, t, _), v in zip(rows, vals)}


def fig_device(meas):
    base = mean_dev(['FV_base_s1_x', 'FV_base_s2_x'])
    cases = [('as deposited', base, C['base'], '-', 2.6),
             ('silver only: 27 % Ag lost', mean_dev(['FV_shrink90_s1_x', 'FV_shrink90_s2_x']), C['ag'], '--', 1.6),
             ('silver only: voids 35 %', mean_dev(['FV_cov65_s1_x']), '#6b8fd0', '--', 1.4),
             ('interlayer AgCl 20 nm', mean_dev(['FG_g207_20_s1_x', 'FG_g207_20_s2_x']), '#7cc49a', '-', 1.6),
             ('interlayer AgCl 40 nm', mean_dev(['FG_g207_40_s1_x', 'FG_g207_40_s2_x']), C['inter'], '-', 2.2),
             ('interlayer n=1.33, 80 nm', mean_dev(['FG_g133_80_s1_x', 'FG_g133_80_s2_x']), '#0f5132', ':', 2.0)]
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6), sharey=True)
    for lab, R, c, ls, lw in cases:
        ax[0].plot(lam, R, c=c, ls=ls, lw=lw, label=lab)
    ax[0].set_title('(a) simulation: full 3D device (mean of realisations)'); ax[0].legend(fontsize=8.5, loc='lower right')
    for k, (b, af) in meas.items():
        c = C['vlp'] if 'VLP' in k else C['pbs']
        ax[1].plot(lam, b, c=c, lw=1.3, ls='--'); ax[1].plot(lam, af, c=c, lw=2.4, label=f'{k}: before (dashed), after')
    ax[1].set_title('(b) experiment (Fig. 2)'); ax[1].legend(fontsize=8.5, loc='lower right')
    for a in ax: a.set_xlim(540, 850); a.set_ylim(0, 100); a.set_xlabel('wavelength (nm)')
    ax[0].set_ylabel('reflectance from the glass side (%)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_r4_device.png')); plt.close(fig)


def fig_map(meas):
    pts = []
    def add(lab, names, base_names, c, mk):
        R = mean_dev(names); B = mean_dev(base_names)
        if R is None or B is None: return
        (l0, r0), (l1, r1) = M.dip(lam, B / 100, 590, 845), M.dip(lam, R / 100, 590, 845)
        pts.append((lab, l1 - l0, np.interp(l0, lam, R) - 100 * r0, c, mk))
    fb = ['FV_base_s1_x', 'FV_base_s2_x']; db = ['D_s1_bottom_x', 'DV_base_s2_x']
    for t, lab in (('agcl3', 'AgCl shell 3'), ('agcl6', 'AgCl shell 6'), ('prot5', 'protein 5'), ('dg10', 'damping .1'), ('dg20', 'damping .2')):
        add(lab, [f'DV_{t}_s1_x', f'DV_{t}_s2_x'], db, C['shell'], 'D')
    for t, lab in (('v21', 'voids 21 %'), ('cov65', 'voids 35 %'), ('sh94', '17 % lost'), ('shrink90', '27 % lost')):
        add(lab, [f'FV_{t}_s1_x', f'FV_{t}_s2_x'], fb, C['ag'], 'o')
    for t, lab in (('g207_20', 'AgCl 20 nm'), ('g207_40', 'AgCl 40 nm'), ('g133_40', 'n1.33 40 nm'), ('g133_80', 'n1.33 80 nm')):
        add(lab, [f'FG_{t}_s1_x', f'FG_{t}_s2_x'], fb, C['inter'], 's')
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for lab, x, y, c, mk in pts:
        ax.plot(x, y, mk, c=c, ms=9, mec='k', mew=0.5)
        if abs(x) > 10: ax.annotate(lab, (x, y), xytext=(6, 4), textcoords='offset points', fontsize=8.5)
    ax.annotate('shells, damping, small silver loss:\nno shift (9 cases)', (0, 0), xytext=(14, 14), textcoords='offset points', fontsize=8.5,
                arrowprops=dict(arrowstyle='-', lw=0.6, color='0.4'))
    for k, (b, af) in meas.items():
        (l0, r0), (l1, r1) = M.dip(lam, b / 100, 590, 845), M.dip(lam, af / 100, 590, 845)
        y = np.interp(l0, lam, af) - 100 * r0
        ax.plot(l1 - l0, y, '*', ms=19, c=C['vlp'] if 'VLP' in k else C['pbs'], mec='k')
        ax.annotate('measured ' + k, (l1 - l0, y), xytext=(10, 10) if 'PBS' in k else (10, -18), textcoords='offset points', fontsize=9.5, fontweight='bold')
    ax.plot([], [], 'D', c=C['shell'], label='shell / damping (P = 0.3 um)'); ax.plot([], [], 'o', c=C['ag'], label='silver loss / restructuring')
    ax.plot([], [], 's', c=C['inter'], label='interlayer under the silver'); ax.legend(loc='upper left', fontsize=9)
    ax.axhline(0, c='0.6', lw=0.8); ax.axvline(0, c='0.6', lw=0.8)
    ax.set_xlabel('shift of the reflectance minimum (nm)'); ax.set_ylabel('rise of R at the old dip wavelength (%)')
    ax.set_title('response map: which change of the film reproduces the measurement?')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_r5_map.png')); plt.close(fig)
    return pts


def main():
    meas = measured()
    fig_problem(meas); fig_model(); fig_device(meas)
    S3 = {}
    band = (lam >= 450) & (lam <= 700)
    for k, f in (('PBS', 'figS3c_ag_pbs.csv'), ('VLP 10 ng/mL', 'figS3d_ag_vlp10.csv')):
        d = np.genfromtxt(os.path.join(ROOT, 'data', f), delimiter=',', names=True); d = d[np.argsort(d['lambda_nm'])]
        S3[k] = float(np.mean(np.interp(lam[band], d['lambda_nm'], d['R_after'] - d['R_before'])))
    g = fig_glass(S3); pts = fig_map(meas)
    print('Ag on glass dR (450-700):', {k: (round(v[0], 1), round(v[1], 1)) for k, v in g.items()}, 'measured', {k: round(v, 1) for k, v in S3.items()})
    for p in pts: print(f'{p[0]:14s} dlam {p[1]:+6.1f}  rise {p[2]:+5.1f}')


if __name__ == '__main__':
    main()
