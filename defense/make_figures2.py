"""Defense deck, revision 2 figures (all from our own calculations):
  img/ldos_rod.png        LDOS map of the 60 x 20 nm gold rod in air at its resonance (BEM, MNPBEM, isi/results/bem_extra/ldosmap_air_L60_608.csv)
                          + Purcell factor and efficiency on the rod axis: BEM line, Lumerical FDTD gap sweep at 607 nm (points)
  img/sphere_spectrum.png equal-volume gold sphere (a = 15.9 nm), radial dipole: Purcell factor and radiative enhancement spectra,
                          exact quasi-static multipole theory (Gersten-Nitzan / Ruppin) + Lumerical FDTD sphere at d = 5 nm (points)
  img/sphere_distance.png same sphere: total, radiative and non-radiative rates and efficiency versus distance at 607 and 530 nm
usage: python defense/make_figures2.py"""
import os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch
import arabic_reshaper
from bidi.algorithm import get_display
D = os.path.dirname(os.path.abspath(__file__)); ISI = os.path.join(D, '..', 'isi'); IMG = os.path.join(D, 'img')
sys.path.insert(0, os.path.join(ISI, 'analysis')); import ldos_map
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 13, 'axes.linewidth': 1.0, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'axes.edgecolor': '#555555', 'xtick.color': '#555555', 'ytick.color': '#555555', 'axes.labelcolor': '#1C1917',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 220})
ROD, SPH, INK, MUT = '#D97706', '#78716C', '#1C1917', '#555555'
fa = lambda s: s   # this matplotlib shapes and orders RTL text itself (checked visually); no reshaper/bidi needed


def tsv(name):
    d = np.genfromtxt(os.path.join(ISI, 'data', 'lumerical', name + '_spectra.tsv'), delimiter='\t', names=True)
    return d[np.argsort(d['lambda_nm'])]


# Lumerical FDTD gap sweep of the rod (axial dipole) at 607 nm
GAPS = {3: 'G3_rod_axial_gap3_mesh1', 5: 'A_rod_axial_gap5_mesh2', 10: 'G10_rod_axial_gap10_mesh2', 20: 'G20_rod_axial_gap20_mesh2'}
FD = {}
for g, n in GAPS.items():
    d = tsv(n); FD[g] = (np.interp(607, d['lambda_nm'], d['Fp']), np.interp(607, d['lambda_nm'], d['T']))

# exact quasi-static sphere (same code as isi/thesis_sphere/sphere_vs_rod.py)
E, n_, k_ = np.loadtxt(os.path.join(ISI, 'thesis_sphere', 'gold_jc.dat'), comments='%', unpack=True)
lam_t = 1239.84 / E; o = np.argsort(lam_t); lam_t = lam_t[o]; eps_t = (n_[o] + 1j * k_[o]) ** 2
eps = lambda lam: np.interp(lam, lam_t, eps_t.real) + 1j * np.interp(lam, lam_t, eps_t.imag)
V = np.pi * 10 ** 2 * 40 + 4 / 3 * np.pi * 10 ** 3; A = (3 * V / (4 * np.pi)) ** (1 / 3)


def sphere(lam, d, N=120):
    e = eps(lam); k = 2 * np.pi / lam; r = A + d; ns = np.arange(1, N + 1)
    g = ns * (e - 1) / (ns * e + ns + 1) * (A / r) ** (2 * ns + 1) / r ** 3
    rad = abs(1 + 2 * g[0] * r ** 3) ** 2                      # dipole + induced sphere dipole radiate together
    nr = 1.5 / k ** 3 * np.sum((ns + 1) ** 2 * g.imag)           # absorption in the gold (all multipoles)
    return rad + nr, rad                                        # total = radiative + non-radiative (energy conservation)


def sphere_tan(lam, d, N=120):
    e = eps(lam); k = 2 * np.pi / lam; r = A + d; ns = np.arange(1, N + 1)
    g = ns * (e - 1) / (ns * e + ns + 1) * (A / r) ** (2 * ns + 1) / r ** 3
    rad = abs(1 - g[0] * r ** 3) ** 2; nr = 0.75 / k ** 3 * np.sum(ns * (ns + 1) * g.imag)
    return rad + nr, rad


def ldos_fig():
    X, Z, G, raw = ldos_map.grid(os.path.join(ISI, 'results', 'bem_extra', 'ldosmap_air_L60_608.csv'))
    iso = (G['Fp_x'] + G['Fp_y'] + G['Fp_z']) / 3
    ax_ = raw[np.abs(raw['x']) < 1e-6]; ax_ = ax_[np.argsort(ax_['dist'])]
    fig = plt.figure(figsize=(13.0, 4.6)); gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.25, 1.25], wspace=0.55)
    a = fig.add_subplot(gs[0]); b = fig.add_subplot(gs[1]); c = fig.add_subplot(gs[2])
    pm = a.pcolormesh(X, Z, np.ma.masked_invalid(iso), norm=LogNorm(1, 3e3), cmap='inferno', shading='nearest')
    a.add_patch(FancyBboxPatch((-10, -30), 20, 60, boxstyle='round,pad=0,rounding_size=10', fc='#d4a017', ec='k', lw=0.8))
    for dd in (3, 5, 10, 20): a.plot(0, 30 + dd, 'o', ms=5, mfc='none', mec='#38bdf8', mew=1.4)
    a.annotate(fa('گسیلنده‌ها'), (0, 50), (14, 52), color='#38bdf8', fontsize=11, arrowprops=dict(arrowstyle='-', color='#38bdf8', lw=0.8))
    a.set_aspect('equal'); a.set_xlabel('x (nm)'); a.set_ylabel('z (nm)'); a.set_title(fa('(الف) نقشه‌ی LDOS در ۶۰۸ نانومتر'), fontsize=13)
    cb = fig.colorbar(pm, ax=a, fraction=0.06, pad=0.03); cb.set_label('LDOS / LDOS(vacuum)', fontsize=11)
    d = ax_['dist']
    b.semilogy(d, ax_['Fp_z'], c=INK, lw=2, label=fa('BEM (همین نانومیله)'))
    gx = np.array(list(FD)); b.semilogy(gx, [FD[g][0] for g in gx], 'o', ms=9, c=ROD, label=fa('FDTD (پویش گاف)'))
    for g in gx: b.annotate(f'{FD[g][0]:.0f}', (g, FD[g][0]), (6, 4), textcoords='offset points', color=ROD, fontsize=12)
    b.set_xlabel(fa('فاصله از کلاهک، d (نانومتر)')); b.set_ylabel(fa('فاکتور پورسل (دوقطبی محوری)')); b.set_xlim(0, 31)
    b.set_title(fa('(ب) افت میدان نزدیک روی محور'), fontsize=13); b.legend(fontsize=11, loc='lower left')
    c.plot(d, 100 * ax_['T_z'] / ax_['Fp_z'], c=INK, lw=2, label='BEM')
    c.plot(gx, [100 * FD[g][1] / FD[g][0] for g in gx], 'o', ms=9, c=ROD, label='FDTD')
    for g in gx: c.annotate(f'{100*FD[g][1]/FD[g][0]:.1f}%', (g, 100 * FD[g][1] / FD[g][0]), (4, -20), textcoords='offset points', color=ROD, fontsize=12)
    c.set_ylim(0, 20); c.set_xlim(0, 31); c.set_xlabel(fa('فاصله از کلاهک، d (نانومتر)')); c.set_ylabel(fa('بازده (درصد)'))
    c.set_title(fa('(ج) بازده در تشدید'), fontsize=13); c.legend(fontsize=11, loc='upper left')
    fig.savefig(os.path.join(IMG, 'ldos_rod.png')); plt.close(fig)


def sphere_spectrum_fig():
    lam = np.arange(450, 801, 2.0); fd = tsv('D_sphere_radial_gap5_mesh2')
    fig, ax = plt.subplots(1, 2, figsize=(13.0, 4.4)); cols = {3: '#9a3412', 5: ROD, 10: '#a8a29e', 20: '#44403c'}
    for dd, col in cols.items():
        R = np.array([sphere(l, dd) for l in lam])
        ax[0].semilogy(lam, R[:, 0], c=col, lw=2, label=fa(f'd = {dd} نانومتر'))
        ax[1].semilogy(lam, R[:, 1], c=col, lw=2, label=fa(f'd = {dd} نانومتر'))
    sel = (fd['lambda_nm'] >= 450) & (fd['lambda_nm'] <= 800); s = np.flatnonzero(sel)[::6]
    ax[0].semilogy(fd['lambda_nm'][s], fd['Fp'][s], 'o', ms=6, mfc='white', mec=ROD, mew=1.6, label=fa('FDTD کره، d = 5'))
    ax[1].semilogy(fd['lambda_nm'][s], fd['T'][s], 'o', ms=6, mfc='white', mec=ROD, mew=1.6, label=fa('FDTD کره، d = 5'))
    for a_, yl, t in ((ax[0], 'فاکتور پورسل (دوقطبی شعاعی)', '(الف) نرخ کل واپاشی'), (ax[1], 'تقویت تابشی', '(ب) نرخ تابشی')):
        a_.axvline(530, c=SPH, ls=':', lw=1.2); a_.axvline(607, c=ROD, ls=':', lw=1.2)
        a_.set_xlabel(fa('طول موج (نانومتر)')); a_.set_ylabel(fa(yl)); a_.set_title(fa(t), fontsize=13); a_.set_xlim(450, 800)
    ax[0].text(527, 5.5e3, fa('تشدید کره ۵۳۰'), color=SPH, fontsize=11, ha='right'); ax[0].text(611, 5.5e3, fa('تشدید میله ۶۰۷'), color=ROD, fontsize=11)
    ax[1].legend(fontsize=10.5, loc='upper right', ncol=1); ax[0].set_ylim(1, 1e4); ax[1].set_ylim(1, 20)
    fig.tight_layout(); fig.savefig(os.path.join(IMG, 'sphere_spectrum.png')); plt.close(fig)


def sphere_distance_fig():
    d = np.geomspace(1, 40, 120)
    fig, ax = plt.subplots(1, 2, figsize=(13.0, 4.4))
    R = np.array([sphere(607, x) for x in d]); tot, rad = R[:, 0], R[:, 1]
    ax[0].loglog(d, tot, c=INK, lw=2.2, label=fa('کل (پورسل)')); ax[0].loglog(d, rad, c=ROD, lw=2.2, label=fa('تابشی'))
    ax[0].loglog(d, tot - rad, c=SPH, lw=2.2, ls='--', label=fa('غیرتابشی (اتلاف در فلز)'))
    for x in (3, 5, 10, 20):
        t, r = sphere(607, x); ax[0].plot(x, t, 'o', c=INK, ms=6); ax[0].plot(x, r, 'o', c=ROD, ms=6)
        ax[0].annotate(f'{t:.0f}' if t >= 10 else f'{t:.1f}', (x, t), (4, 5), textcoords='offset points', fontsize=11, color=INK)
        ax[0].annotate(f'{r:.1f}', (x, r), (4, -14), textcoords='offset points', fontsize=11, color=ROD)
    ax[0].set_xlabel(fa('فاصله از سطح، d (نانومتر)')); ax[0].set_ylabel(fa('نرخ / نرخ در خلأ')); ax[0].set_title(fa('(الف) نرخ‌ها در ۶۰۷ نانومتر'), fontsize=13)
    ax[0].legend(fontsize=11, loc='upper right'); ax[0].set_ylim(0.5, 3e4)
    for lam, col, lab in ((607, ROD, '۶۰۷ نانومتر (تشدید میله)'), (530, SPH, '۵۳۰ نانومتر (تشدید کره)')):
        R = np.array([sphere(lam, x) for x in d]); ax[1].semilogx(d, 100 * R[:, 1] / R[:, 0], c=col, lw=2.2, label=fa(lab))
    ax[1].set_ylim(0, 100); ax[1].set_xlabel(fa('فاصله از سطح، d (نانومتر)')); ax[1].set_ylabel(fa('بازده (درصد)'))
    ax[1].set_title(fa('(ب) بازده: خاموشی در فواصل کم'), fontsize=13); ax[1].legend(fontsize=11, loc='upper left')
    fig.tight_layout(); fig.savefig(os.path.join(IMG, 'sphere_distance.png')); plt.close(fig)


if __name__ == '__main__':
    ldos_fig(); sphere_spectrum_fig(); sphere_distance_fig()
    print('rod FDTD at 607 nm:', {g: (round(v[0]), round(v[1], 1), f'{100*v[1]/v[0]:.1f}%') for g, v in FD.items()})
    for x in (3, 5, 10, 20):
        t, r = sphere(607, x); tt, _ = sphere_tan(607, x)
        print(f'sphere 607 nm d={x}: Fp {t:.1f} T {r:.2f} eta {100*r/t:.1f}%  radial/tangential Fp {t/tt:.2f}')
