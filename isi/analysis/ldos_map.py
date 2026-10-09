"""Maps of the local density of states and of the local intensity around the 60 x 20 nm gold rod (BEM, job_ldosmap.m):
isotropic LDOS (mean of Fp over x, y, z), radiative LDOS (mean T), axial-to-radial ratio, and |E|^2/|E_0|^2 for a plane
wave polarised along the rod, at the resonance (608 nm) and in the interband region (520 nm). The xz quadrant computed
is mirrored to the full rod.
usage: python isi/analysis/ldos_map.py -> isi/figures/fig_ldosmap.pdf, isi/results/ldosmap.md"""
import os, glob, re
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 8, 'axes.linewidth': 0.8, 'xtick.direction': 'in',
                     'ytick.direction': 'in', 'savefig.bbox': 'tight', 'figure.dpi': 150})


def grid(f):
    d = np.genfromtxt(f, delimiter=',', names=True, skip_header=1)
    xs = np.unique(d['x']); zs = np.unique(d['z'])
    G = {}
    for k in ('Fp_x', 'Fp_y', 'Fp_z', 'T_x', 'T_y', 'T_z', 'E2', 'Ez2', 'dist'):
        A = np.full((len(zs), len(xs)), np.nan)
        A[np.searchsorted(zs, d['z']), np.searchsorted(xs, d['x'])] = d[k]
        A = np.concatenate([A[::-1], A[1:]], 0); A = np.concatenate([A[:, ::-1], A[:, 1:]], 1)   # mirror z, then x
        G[k] = A
    X = np.concatenate([-xs[::-1], xs[1:]]); Z = np.concatenate([-zs[::-1], zs[1:]])
    return X, Z, G, d


def rod(ax, L=60, D=20):
    ax.add_patch(FancyBboxPatch((-D / 2, -L / 2), D, L, boxstyle=f'round,pad=0,rounding_size={D/2}', fc='#d4a017', ec='k', lw=0.6))


def main():
    files = {re.search(r'ldosmap_(\w+)\.csv', f).group(1): f for f in glob.glob(os.path.join(RES, 'bem_extra', 'ldosmap_*.csv'))}
    if 'air_L60_608' not in files: print('no map'); return
    panels = []
    X, Z, G, d = grid(files['air_L60_608'])
    lds = (G['Fp_x'] + G['Fp_y'] + G['Fp_z']) / 3; rad = (G['T_x'] + G['T_y'] + G['T_z']) / 3
    panels += [(lds, r'LDOS $\rho/\rho_0$, 608 nm', LogNorm(1, lds[np.isfinite(lds)].max())),
               (rad, r'radiative LDOS, 608 nm', LogNorm(0.1, rad[np.isfinite(rad)].max())),
               (G['E2'], r'$|E|^2/|E_0|^2$, 608 nm', LogNorm(0.1, np.nanmax(G['E2'])))]
    eff = 100 * rad / lds
    panels.insert(2, (eff, r'efficiency $\langle T\rangle/\langle F_p\rangle$ (%), 608 nm', None))
    fig, ax = plt.subplots(1, len(panels), figsize=(1.85 * len(panels), 3.0))
    for a, (A, t, nrm) in zip(ax, panels):
        kw = dict(norm=nrm) if nrm is not None else dict(vmin=0, vmax=np.nanmax(A))
        im = a.pcolormesh(X, Z, A, cmap='inferno', shading='nearest', rasterized=True, **kw)
        rod(a); a.set_aspect('equal'); a.set_title(t, fontsize=7.5); a.set_xlabel('x (nm)')
        fig.colorbar(im, ax=a, fraction=0.06, pad=0.02)
    ax[0].set_ylabel('z (nm)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_ldosmap.pdf')); fig.savefig(os.path.join(FIG, 'fig_ldosmap.png'), dpi=130)
    # numbers: values 5 nm from the surface on the axis (apex) and at the side (waist)
    out = ['# LDOS map, rod 60 x 20 nm in air', '']
    for key, f in sorted(files.items()):
        dd = np.genfromtxt(f, delimiter=',', names=True, skip_header=1)
        for lab, sel in (('apex, on axis', (dd['x'] == 0)), ('waist, z = 0', (dd['z'] == 0))):
            s = sel & (abs(dd['dist'] - 5) < 1.01)
            if s.any():
                i = np.where(s)[0][0]
                out.append(f"- {key}, {lab}, d={dd['dist'][i]:.1f} nm: Fp_x {dd['Fp_x'][i]:.0f}, Fp_y {dd['Fp_y'][i]:.0f}, Fp_z {dd['Fp_z'][i]:.0f}, "
                           f"T_x {dd['T_x'][i]:.2f}, T_z {dd['T_z'][i]:.2f}, |E|^2 {dd['E2'][i]:.1f}")
        # hot-spot volume (one quadrant x 4 by symmetry, approximate cylindrical: weight 2 pi x)
        w = 2 * np.pi * np.maximum(dd['x'], 1.0) * 4.0   # dx = dz = 2 nm, two half-spaces in z
        for thr in (100, 30):
            v = np.sum(w[dd['E2'] > thr])
            out.append(f'  - {key}: volume with |E|^2 > {thr}: ~{v:.0f} nm^3 (axisymmetric estimate)')
    open(os.path.join(RES, 'ldosmap.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__':
    main()
