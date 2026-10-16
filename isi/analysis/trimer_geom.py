"""Top-view schematic of the gold-nanorod dimer/trimer (model M4) -> isi/figures/fig_trimer_geom.png"""
import os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Affine2D
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9})


def rod(ax, xc, yc, L, D, ang=0, **kw):
    p = FancyBboxPatch((-L / 2 + D / 2, -D / 2), L - D, D, boxstyle=f'round,pad=0,rounding_size={D/2}', mutation_aspect=1, **kw)
    p.set_transform(Affine2D().rotate_deg(ang).translate(xc, yc) + ax.transData); ax.add_patch(p)


fig, ax = plt.subplots(figsize=(5.6, 3.0))
L, D, g = 270, 60, 40; xc = g / 2 + L / 2
for s in (-1, 1): rod(ax, s * xc, 0, L, D, fc='#d9a441', ec='#7a5a12', lw=1)
rod(ax, 0, 160, 300, D, 35, fc='#d9a441', ec='#7a5a12', lw=1, alpha=0.95)
ax.annotate('', xy=(28, 0), xytext=(-28, 0), arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.6))
ax.plot(0, 0, 'o', c='#c0392b', ms=4)
ax.text(0, 14, 'emitter', ha='center', va='bottom', color='#c0392b', fontsize=8)
ax.text(-xc, 0, 'R1', ha='center', va='center'); ax.text(xc, 0, 'R2', ha='center', va='center'); ax.text(0, 160, 'R3', ha='center', va='center')
ax.annotate('', xy=(-g / 2, -45), xytext=(g / 2, -45), arrowprops=dict(arrowstyle='<->', lw=0.8))
ax.text(0, -52, f'gap {g} nm', ha='center', va='top', fontsize=7.5)
ax.text(-xc, -72, f'L = {L} nm, D = {D} nm', ha='center', va='top', fontsize=7.5)
ax.text(-320, 312, r'R3: length $L_3$, angle $\theta_3$, centre $(X_3, Y_3)$', fontsize=7.5)
ax.annotate('', xy=(290, 325), xytext=(290, 255), arrowprops=dict(arrowstyle='->', color='#1f4e9c', lw=1.2))
ax.text(298, 285, '+y', color='#1f4e9c', fontsize=8)
ax.set_xlim(-330, 330); ax.set_ylim(-105, 340); ax.set_aspect('equal'); ax.set_xlabel('x (nm)'); ax.set_ylabel('y (nm)')
ax.set_title('host n = 1.5 (rods in the plane z = 0)', fontsize=8.5, loc='left')
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_trimer_geom.png'), dpi=150, bbox_inches='tight')
