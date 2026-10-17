"""Side-by-side top views: supervisor's baseline M4 vs the best directional design -> isi/figures/fig_trimer_opt.png"""
import os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Affine2D
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 8.5})


def rod(ax, xc, yc, L, D=60, ang=0, fc='#d9a441'):
    p = FancyBboxPatch((-L / 2 + D / 2, -D / 2), L - D, D, boxstyle=f'round,pad=0,rounding_size={D/2}', fc=fc, ec='#7a5a12', lw=1)
    p.set_transform(Affine2D().rotate_deg(ang).translate(xc, yc) + ax.transData); ax.add_patch(p)


def panel(ax, L, L3, A, title, note, arrow):
    xc = 20 + L / 2
    rod(ax, -xc, 0, L); rod(ax, xc, 0, L); rod(ax, 0, 160, L3, ang=A, fc='#e8b860')
    ax.annotate('', xy=(26, 0), xytext=(-26, 0), arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.6)); ax.plot(0, 0, 'o', c='#c0392b', ms=3.5)
    ax.text(-xc, 0, f'R1\n{L} nm', ha='center', va='center', fontsize=7.5); ax.text(xc, 0, f'R2\n{L} nm', ha='center', va='center', fontsize=7.5)
    ax.text(0, 160, f'R3  {L3} nm' + ('' if A == 0 else f', {A}°'), ha='center', va='center', fontsize=7.5)
    ax.annotate('', xy=(-20, -42), xytext=(20, -42), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(0, -48, '40 nm', ha='center', va='top', fontsize=7)
    if A == 0:
        ax.annotate('', xy=(-235, 30), xytext=(-235, 130), arrowprops=dict(arrowstyle='<->', lw=0.7, color='0.35'))
        ax.text(-242, 80, '100 nm\ngap', ha='right', va='center', fontsize=6.5, color='0.35')
    if arrow:
        ax.annotate('', xy=(250, 330), xytext=(250, 215), arrowprops=dict(arrowstyle='-|>', color='#1f4e9c', lw=2.4, mutation_scale=14))
        ax.annotate('', xy=(250, -95), xytext=(250, -50), arrowprops=dict(arrowstyle='-|>', color='#1f4e9c', lw=0.9, mutation_scale=8))
        ax.text(262, 272, arrow[0], color='#1f4e9c', fontsize=7.5, va='center'); ax.text(262, -72, arrow[1], color='#1f4e9c', fontsize=7, va='center')
    ax.set_xlim(-340, 340); ax.set_ylim(-110, 345); ax.set_aspect('equal'); ax.set_xlabel('x (nm)')
    ax.set_title(title, fontsize=9, loc='left'); ax.text(-330, 330, note, fontsize=7, va='top')


fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.4))
panel(ax[0], 300, 240, 35, '(a) M4 as proposed', 'peak 1660 nm, ratio 1.6 at 1550', ('38%', '24%'))
panel(ax[1], 285, 315, 0, '(b) final design (R3 parallel)', 'ratio 5.1 at 1550 nm, T = 196', ('62%', '12%'))
ax[0].set_ylabel('y (nm)')
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_trimer_opt.png'), dpi=150, bbox_inches='tight')
