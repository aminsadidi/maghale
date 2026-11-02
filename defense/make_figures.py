"""Figures for the defense deck: geometry schematic (slide 6) and key equations (theory slide)."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img'); os.makedirs(OUT, exist_ok=True)
INK, MUTED, ACC, GOLD, BG = '#1C1917', '#78716C', '#D97706', '#E8B04A', '#FAFAF9'

# ---------- geometry schematic: 5.83 x 7.5 in (same frame as the old picture) ----------
fig = plt.figure(figsize=(5.83, 7.5), dpi=220); fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-60, 60); ax.set_ylim(-62, 92); ax.set_aspect('equal'); ax.axis('off')
# radiative monitor box (large) and Purcell box (small)
ax.add_patch(Rectangle((-48, -52), 96, 130, fill=False, ls=(0, (5, 4)), lw=1.4, ec=MUTED))
ax.text(46, 74, 'radiative box\n(6 monitors)', ha='right', va='top', fontsize=9, color=MUTED)
# gold rod along z: L = 60, D = 20 (capsule)
rod = FancyBboxPatch((-10, -30), 20, 60, boxstyle='round,pad=0,rounding_size=10', fc=GOLD, ec='#B7791F', lw=1.5)
ax.add_patch(rod)
ax.add_patch(FancyBboxPatch((-6.5, -24), 4, 48, boxstyle='round,pad=0,rounding_size=2', fc='white', ec='none', alpha=0.35))
ax.text(0, 0, 'Au', ha='center', va='center', fontsize=15, color=INK, fontweight='bold')
# dipole 3 nm above the top cap, along z
ax.add_patch(FancyArrowPatch((0, 33.5), (0, 44.5), arrowstyle='-|>', mutation_scale=16, lw=2.4, color=ACC))
ax.add_patch(Circle((0, 39), 1.3, color=ACC))
ax.add_patch(Rectangle((-4.5, 34.5), 9, 9, fill=False, lw=1.0, ec=ACC, ls=':'))
ax.text(6.5, 41, r'$\mathbf{p}\parallel z$', fontsize=13, color=ACC, va='center')
ax.text(-6.5, 46.5, 'Purcell box', fontsize=8.5, color=ACC, ha='right')
# gap d
ax.annotate('', xy=(-16, 30), xytext=(-16, 39), arrowprops=dict(arrowstyle='<->', color=INK, lw=1.1))
ax.plot([-18, -1], [39, 39], color=MUTED, lw=0.6, ls=':'); ax.plot([-18, -8], [30, 30], color=MUTED, lw=0.6, ls=':')
ax.text(-18, 34.5, r'$d=3,\ 5,\ 20$ nm', fontsize=11, ha='right', va='center', color=INK)
# dimensions
ax.annotate('', xy=(22, -30), xytext=(22, 30), arrowprops=dict(arrowstyle='<->', color=INK, lw=1.1))
ax.text(25, 0, r'$L=60$ nm', fontsize=12, va='center', color=INK)
ax.annotate('', xy=(-10, -38), xytext=(10, -38), arrowprops=dict(arrowstyle='<->', color=INK, lw=1.1))
ax.text(0, -42.5, r'$D=20$ nm  ($R_{cap}=10$ nm)', fontsize=11, ha='center', va='top', color=INK)
# axes
ax.add_patch(FancyArrowPatch((-40, -44), (-40, -32), arrowstyle='-|>', mutation_scale=11, color=INK, lw=1.2))
ax.add_patch(FancyArrowPatch((-40, -44), (-28, -44), arrowstyle='-|>', mutation_scale=11, color=INK, lw=1.2))
ax.text(-40, -30.5, 'z', ha='center', fontsize=11, color=INK); ax.text(-26.5, -44, 'x', va='center', fontsize=11, color=INK)
# radiation pattern hint (sin^2 lobes)
import numpy as np
th = np.linspace(0, 2 * np.pi, 300); rr = 9 * np.sin(th) ** 2
ax.plot(36 + rr * np.sin(th), 30 + rr * np.cos(th), color=ACC, lw=1.2, alpha=0.8)
ax.text(36, 17, r'$\propto\sin^2\theta$', ha='center', fontsize=10, color=ACC)
ax.text(0, 86, r'vacuum ($n=1$), Johnson & Christy gold, $\lambda=500$–$900$ nm', ha='center', fontsize=9.5, color=MUTED)
fig.savefig(os.path.join(OUT, 'geometry.png'), facecolor=BG); plt.close(fig)

# ---------- equations (transparent PNGs) ----------
eqs = {
    'eq_purcell': r'$F_P=\dfrac{\Gamma_{\rm tot}}{\Gamma_0}=\dfrac{P_{\rm tot}}{P_0}=1+\dfrac{6\pi c}{\omega}\,\mathbf{n}_p\!\cdot\!\mathrm{Im}\{\mathbf{G}_{\rm scatt}(\mathbf{r}_0,\mathbf{r}_0)\}\!\cdot\!\mathbf{n}_p$',
    'eq_split':   r'$P_{\rm tot}=P_{\rm rad}+P_{\rm nonrad}\,,\qquad \eta=\dfrac{P_{\rm rad}}{P_{\rm tot}}\,,\qquad \dfrac{\Gamma_{\rm rad}}{\Gamma_0}=\eta\,F_P$',
    'eq_near':    r'$\Gamma_{\rm nonrad}\ \propto\ \dfrac{\mathrm{Im}\,\epsilon_m}{d^{\,3}}\qquad (d\ll\lambda)$',
}
for name, tex in eqs.items():
    f = plt.figure(figsize=(8, 1.0), dpi=250); f.patch.set_alpha(0)
    f.text(0.5, 0.5, tex, fontsize=22, ha='center', va='center', color=INK)
    f.savefig(os.path.join(OUT, name + '.png'), transparent=True, bbox_inches='tight', pad_inches=0.05); plt.close(f)
print('figures written to', OUT)
