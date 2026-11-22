"""To-scale top views of the three structures of the supervisor's distance study (2026-11-22), all with the same gold rods
(L = 275 nm, D = 60 nm, hemispherical caps, host n = 1.5, emitter dipole along x):
  (a) single rod R1, emitter on the axis facing its tip, distance h = 4 ... 40 nm (one BEM run: job_tri2 S_L275_E_H4)
  (b) tip-to-tip dimer R1 + R2, emitter at the gap centre, gap g = 10 ... 80 nm (h = g/2)   (job_tri2 L275_G<g>_H4)
  (c) trimer: dimer + R3 (295 nm, parallel, centre y = 160 nm), same gaps            (job_tri2 L275_R295_A0_Y160_G<g>_H4)
usage: python isi/analysis/geom_study.py -> isi/figures/fig_g1_structures.png"""
import os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.transforms as mt
from matplotlib.patches import FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures')
plt.rcParams.update({'font.size': 11, 'savefig.bbox': 'tight', 'savefig.dpi': 200})
L, D, L3, Y3 = 275, 60, 295, 160
HS = [4, 6, 8, 10, 12, 15, 20, 25, 30, 40]; GAPS = [10, 20, 30, 40, 60, 80]
GOLD = dict(fc='#e9c46a', ec='#8a6d1d', lw=1.3)


def rod(ax, xc, yc, Lr, **kw):
    p = FancyBboxPatch((xc - Lr / 2, yc - D / 2), Lr, D, boxstyle=f'round,pad=0,rounding_size={D/2}', **kw)
    p.set_transform(mt.Affine2D() + ax.transData); ax.add_patch(p)


def dim(ax, x0, y0, x1, y1, t, off=(0, 0), **k):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='<->', color='0.3', lw=1))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], t, ha='center', va='center', fontsize=10, color='0.2', **k)


def emitter(ax, x, y, c='#9a3412', s=1.0):
    ax.annotate('', xy=(x + 11 * s, y), xytext=(x - 11 * s, y), arrowprops=dict(arrowstyle='<->', color=c, lw=1.6))
    ax.plot(x, y, 'o', c=c, ms=5, zorder=5)


def main():
    fig, ax = plt.subplots(3, 1, figsize=(11, 13.0), gridspec_kw=dict(height_ratios=[180, 190, 355]))   # ratios = y-ranges -> one scale
    # (a) single rod: tip at x = -20 (as in job_tri2, g = 40), emitter line on the axis
    a = ax[0]; tip = -20; xc = tip - L / 2
    rod(a, xc, 0, L, **GOLD); a.text(xc, 0, 'R1', ha='center', va='center', fontsize=13)
    for h in HS: a.plot(tip + h, 0, 'o', c='#1f4e9c', ms=3.5)
    emitter(a, tip + 20, 0, s=0.6)
    dim(a, tip, -48, tip + 40, -48, 'h = 4 ... 40 nm (10 positions)', (0, -14))
    dim(a, xc - L / 2, 52, xc + L / 2, 52, 'L = 275 nm', (0, 14)); dim(a, xc - L / 2 - 14, -30, xc - L / 2 - 14, 30, 'D = 60', (-12, 0), rotation=90)
    a.text(tip + 60, 8, 'blue dots: computed emitter positions\nred: emitter (x dipole), shown at h = 20 nm', fontsize=9.5, color='0.25', va='bottom')
    a.set_title('(a) single rod, emitter on the axis facing the tip; distance h varied', fontsize=12)
    a.set_ylim(-100, 80)
    # (b) dimer, drawn at g = 40 with the tip positions of the other gaps marked
    for k, (a, tri) in enumerate(((ax[1], False), (ax[2], True))):
        g = 40; x1 = g / 2 + L / 2
        rod(a, -x1, 0, L, **GOLD); rod(a, x1, 0, L, **GOLD)
        a.text(-x1, 0, 'R1', ha='center', va='center', fontsize=13); a.text(x1, 0, 'R2', ha='center', va='center', fontsize=13)
        for gg in GAPS:
            a.plot([gg / 2, gg / 2], [-D / 2 - 6, -D / 2 - 14], c='0.35', lw=1); a.plot([-gg / 2, -gg / 2], [-D / 2 - 6, -D / 2 - 14], c='0.35', lw=1)
        a.text(0, -D / 2 - 24, 'tick marks: tip positions for gaps 10, 20, 30, 40, 60, 80 nm (rods move apart, length fixed)', ha='center', fontsize=9.5, color='0.25')
        emitter(a, 0, 0)
        dim(a, -g / 2, 44, g / 2, 44, 'g', (0, 12)); dim(a, -x1 - L / 2, -82, -x1 + L / 2, -82, 'L = 275 nm', (0, -13))
        dim(a, x1 - L / 2, -82, x1 + L / 2, -82, 'L = 275 nm', (0, -13))
        if tri:
            rod(a, 0, Y3, L3, **GOLD); a.text(0, Y3, 'R3', ha='center', va='center', fontsize=13)
            dim(a, -L3 / 2, Y3 + 48, L3 / 2, Y3 + 48, 'L3 = 295 nm', (0, 13)); dim(a, x1 + L / 2 + 30, 0, x1 + L / 2 + 30, Y3, 'Y3 = 160 nm', (14, 0), rotation=90)
            a.text(0, Y3 - 48, 'R3 to dimer, surface to surface: 100 nm (fixed)', ha='center', fontsize=9.5, color='0.35')
            a.set_title('(c) trimer: same dimer + R3 (as the final design), gap g varied; emitter at the gap centre (h = g/2)', fontsize=12)
            a.set_ylim(-110, Y3 + 85)
        else:
            a.set_title('(b) tip-to-tip dimer on one line, emitter at the gap centre; gap g = 10 ... 80 nm (h = g/2)', fontsize=12)
            a.set_ylim(-110, 80)
    X1 = 20 + L / 2
    for a in ax: a.set_xlim(-X1 - L / 2 - 45, X1 + L / 2 + 75); a.set_aspect('equal'); a.axis('off')
    ax[0].annotate('', xy=(ax[0].get_xlim()[0] + 60, -60), xytext=(ax[0].get_xlim()[0] + 5, -60), arrowprops=dict(arrowstyle='->', color='0.3'))
    ax[0].text(ax[0].get_xlim()[0] + 66, -60, 'x', va='center'); ax[0].text(ax[0].get_xlim()[0] + 5, -85, 'all panels on the same scale (1 unit = 1 nm), top view, z out of page', fontsize=9, color='0.35')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_g1_structures.png')); plt.close(fig)


if __name__ == '__main__':
    main()
