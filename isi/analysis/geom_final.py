"""Top view of the final trimer (L = 275, R3 = 295 nm, D = 60 nm, gap 40 nm, R3 centre (0, 160) nm) -> isi/figures/fig_geom_final.png"""
import os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12})
L, L3, D, g, Y3 = 275, 295, 60, 40, 160
fig, ax = plt.subplots(figsize=(9, 4.2))
def rod(xc, yc, Lr, lab):
    ax.add_patch(FancyBboxPatch((xc - Lr / 2, yc - D / 2), Lr, D, boxstyle=f'round,pad=0,rounding_size={D/2}', fc='#d4a017', ec='#7a5a00', lw=1.2))
    ax.text(xc, yc, lab, ha='center', va='center', fontsize=13, weight='bold', color='#3b2a00')
xc = g / 2 + L / 2
rod(-xc, 0, L, 'R1'); rod(xc, 0, L, 'R2'); rod(0, Y3, L3, 'R3')
ax.plot(0, 0, 'o', c='#c0392b', ms=9); ax.annotate('', (22, 0), (-22, 0), arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=1.6))
ax.annotate('گسیلنده (دوقطبی x)', (0, -8), (150, -110), color='#c0392b', fontsize=11, arrowprops=dict(arrowstyle='-', color='#c0392b', lw=0.8))
def dim(x0, x1, y, t):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle='<->', mutation_scale=12, color='#4a5263', lw=1))
    ax.text((x0 + x1) / 2, y + (14 if y > 0 else -34), t, ha='center', fontsize=11, color='#4a5263')
dim(-xc - L / 2, -xc + L / 2, -95, f'L = {L} nm'); dim(-g / 2, g / 2, -45, f'گاف {g} nm'); dim(-L3 / 2, L3 / 2, Y3 + 50, f'L3 = {L3} nm')
ax.annotate('', (xc + L / 2 + 25, -D / 2), (xc + L / 2 + 25, D / 2), arrowprops=dict(arrowstyle='<->', color='#4a5263'))
ax.text(xc + L / 2 + 32, 0, f'D = {D} nm', va='center', fontsize=11, color='#4a5263')
ax.annotate('', (-L3 / 2 - 30, Y3), (-L3 / 2 - 30, 0), arrowprops=dict(arrowstyle='<->', color='#4a5263'))
ax.text(-L3 / 2 - 38, Y3 / 2, f'{Y3} nm', va='center', ha='right', fontsize=11, color='#4a5263')
ax.annotate('', (-520, 230), (-520, 150), arrowprops=dict(arrowstyle='->', color='#1f4e9c', lw=2)); ax.text(-512, 236, '+y: جهت گسیل', fontsize=11, color='#1f4e9c')
ax.text(-560, -150, 'محیط همگن n = 1.5', fontsize=11, color='#7a8191')
ax.set_xlim(-600, 600); ax.set_ylim(-160, 270); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(os.path.join(FIG, 'fig_geom_final.png'), dpi=200, bbox_inches='tight'); print('ok')
