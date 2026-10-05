"""Geometry schematic (Fig. 1): capped gold nanorod, dipole positions/orientations, equal-volume sphere, spacer shell.
usage: python isi/analysis/make_geometry.py  (run from repo root)"""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, FancyArrowPatch
plt.rcParams.update({'font.family': 'serif', 'font.size': 8})
GOLD, EDGE, C1, C2 = '#e2b84a', '#8a6d1f', '#1f4e9c', '#c0392b'
L, D, R, Rs, d = 60, 20, 10, 15.874, 5

def arrow(ax, x0, y0, dx, dy, c, lw=1.6):
    ax.add_patch(FancyArrowPatch((x0, y0), (x0 + dx, y0 + dy), arrowstyle='-|>',
                                 mutation_scale=9, color=c, lw=lw))
def dim(ax, x0, y0, x1, y1, txt, off=(0, 0), **kw):
    ax.annotate('', (x0, y0), (x1, y1), arrowprops=dict(arrowstyle='<->', lw=0.6, color='0.3', shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], txt, ha='center', va='center', fontsize=7, **kw)

fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.9), gridspec_kw={'width_ratios': [1.25, 0.9, 1.0]})
# (a) rod, side view (axis vertical = z)
a = ax[0]; h = (L - D) / 2
a.add_patch(Rectangle((-R, -h), D, 2 * h, fc=GOLD, ec='none'))
for s in (1, -1):
    a.add_patch(Wedge((0, s * h), R, 0 if s > 0 else 180, 180 if s > 0 else 360, fc=GOLD, ec='none'))
t = np.linspace(0, np.pi, 100)
a.plot(R * np.cos(t), h + R * np.sin(t), c=EDGE, lw=0.8); a.plot(R * np.cos(t), -h - R * np.sin(t), c=EDGE, lw=0.8)
a.plot([R, R], [-h, h], c=EDGE, lw=0.8); a.plot([-R, -R], [-h, h], c=EDGE, lw=0.8)
zt = L / 2; ze = zt + d
a.plot([0, 0], [-L / 2 - 6, ze + 16], c='0.5', lw=0.5, ls='-.')
a.plot(0, ze, 'o', c='k', ms=2.5)
arrow(a, 0, ze, 0, 8, C1); arrow(a, 0, ze, 8, 0, C2)
a.text(1.5, ze + 6.5, r'axial ($z$)', color=C1, fontsize=7); a.text(5, ze - 3.2, 'transverse ($x$)', color=C2, fontsize=7)
dim(a, -16, -L / 2, -16, L / 2, f'$L$ = {L} nm', off=(-4.5, 0), rotation=90)
dim(a, -R, -L / 2 - 4, R, -L / 2 - 4, f'$D$ = {D} nm', off=(0, -3))
dim(a, -5, zt, -5, ze, '$d$', off=(-3.5, 0))
a.text(0, 0, 'Au', ha='center', va='center', fontsize=9, color=EDGE)
a.text(14, 2, 'hemispherical\ncaps, $R$ = 10 nm', fontsize=6.5, color='0.3')
a.set_title('(a) nanorod, aspect ratio 3', fontsize=8)
# (b) equal-volume sphere
b = ax[1]
b.add_patch(Circle((0, 0), Rs, fc=GOLD, ec=EDGE, lw=0.8)); b.text(0, 0, 'Au', ha='center', va='center', fontsize=9, color=EDGE)
b.plot([0, 0], [-Rs - 6, Rs + d + 16], c='0.5', lw=0.5, ls='-.'); b.plot(0, Rs + d, 'o', c='k', ms=2.5)
arrow(b, 0, Rs + d, 0, 8, C1); arrow(b, 0, Rs + d, 8, 0, C2)
b.text(1.5, Rs + d + 6.5, 'radial', color=C1, fontsize=7); b.text(5, Rs + d - 3.2, 'tangential', color=C2, fontsize=7)
dim(b, -Rs - 4, -Rs, -Rs - 4, Rs, r'$2R_{\rm sph}$', off=(-4.5, 0), rotation=90)
b.text(0, -Rs - 9, r'$R_{\rm sph}$ = 15.874 nm' + '\n(same gold volume)', ha='center', fontsize=6.5, color='0.3')
b.set_title('(b) equal-volume sphere', fontsize=8)
# (c) tip close-up: spacer shell, polar angle
c = ax[2]; s = 5
t = np.linspace(-0.15, np.pi + 0.15, 200)
c.add_patch(Wedge((0, 0), R, 0, 180, fc=GOLD, ec=EDGE, lw=0.8)); c.add_patch(Rectangle((-R, -8), D, 8, fc=GOLD, ec='none'))
c.plot([R, R], [-8, 0], c=EDGE, lw=0.8); c.plot([-R, -R], [-8, 0], c=EDGE, lw=0.8)
c.add_patch(Wedge((0, 0), R + s, 0, 180, width=s, fc='#cfe3f7', ec='0.6', lw=0.5))
c.plot([0, 0], [-8, R + s + 9], c='0.5', lw=0.5, ls='-.')
for th in (0, 40, 80):
    tr = np.radians(th); x, y = (R + s) * np.sin(tr), (R + s) * np.cos(tr)
    c.plot(x, y, 'o', c='k', ms=2.2); arrow(c, x, y, 6 * np.sin(tr), 6 * np.cos(tr), C1, lw=1.2)
c.plot([0, (R + s) * np.sin(np.radians(40))], [0, (R + s) * np.cos(np.radians(40))], c='0.4', lw=0.5)
c.text(1.8, 6.5, r'$\theta$', fontsize=8)
c.text(-R - s - 1, R + 2, 'spacer\nshell $s$', fontsize=6.5, color='0.3', ha='right')
c.text(R + s + 1, -6, 'glass substrate\nor water host\n(variants)', fontsize=6, color='0.3')
c.set_title('(c) tip: emitter on a spacer shell', fontsize=8)
for x, lim in zip(ax, [(-28, 34, -38, 50), (-26, 26, -30, 46), (-24, 26, -10, 30)]):
    x.set_xlim(lim[0], lim[1]); x.set_ylim(lim[2], lim[3]); x.set_aspect('equal'); x.axis('off')
fig.tight_layout(); fig.savefig('isi/figures/fig_geometry.pdf'); fig.savefig('isi/figures/fig_geometry.png', dpi=200)
