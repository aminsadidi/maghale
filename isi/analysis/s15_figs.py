"""Figures for the detailed section-15 report (pulsed single-photon emission of the emitter on the trimer).
  fig_s15_mech.png : (a) pi pulse and excited-state population vs time (antenna, 1/Gamma = 7.0 ps; 200 fs and 2 ps pulses)
                     (b) g2(0) vs tau_p * Gamma (QuTiP grid, isi/results/pulsed_tls.csv) with the design points
                     (c) indistinguishability vs gamma*/Gamma (QuTiP) against the analytic limit Gamma/(Gamma + 2 gamma*)
usage: python isi/analysis/s15_figs.py"""
import os
import numpy as np, qutip as qt, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures'); RES = os.path.join(HERE, '..', 'results')
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HB = 6.582119569e-16
Fp, tau0 = 285.97, 2e-9
G = Fp / tau0                                   # 1/s
sm = qt.destroy(2); sp = sm.dag(); n = sp * sm


def trace(tp, gstar_eV=1e-6):
    taup = tp * G; s = taup / (2 * np.sqrt(2 * np.log(2))); sf = s * np.sqrt(2)
    A = np.pi / (np.sqrt(2 * np.pi) * sf); t0 = 4 * sf
    H = [[0.5 * (sp + sm), lambda t: A * np.exp(-0.5 * ((t - t0) / sf) ** 2)]]
    tl = np.linspace(0, t0 + 6.0, 3000)
    pop = qt.mesolve(H, qt.basis(2, 0) * qt.basis(2, 0).dag(), tl, [sm, np.sqrt(2 * gstar_eV / HB / G) * n], e_ops=[n]).expect[0]
    env = np.exp(-((tl - t0) / sf) ** 2)                 # intensity ~ Omega^2
    return (tl - t0) / G * 1e12, pop, env


fig, ax = plt.subplots(1, 3, figsize=(16, 4.4))
for tp, c, lab in ((200e-15, '#1f4e9c', 'پالس ۲۰۰ fs'), (2e-12, '#b8892a', 'پالس ۲ ps')):
    t, p, e = trace(tp)
    ax[0].plot(t, p, c=c, lw=2.2, label=f'جمعیت حالت برانگیخته، {lab}'); ax[0].fill_between(t, 0, 0.35 * e, color=c, alpha=0.18)
ax[0].plot(t, np.exp(-np.clip(t, 0, None) * 1e-12 * G) * (t >= 0), c='0.4', lw=1, ls=':', label='$e^{-\\Gamma t}$، $1/\\Gamma$ = 7.0 ps')
ax[0].set_xlim(-4, 25); ax[0].set_ylim(0, 1.05); ax[0].set_xlabel('زمان نسبت به مرکز پالس (ps)'); ax[0].set_ylabel('جمعیت حالت برانگیخته')
ax[0].set_title('(الف) برانگیختگی با پالس پی و فروافت (با آنتن)', fontsize=12); ax[0].legend(fontsize=9, loc='upper right')
d = np.genfromtxt(os.path.join(RES, 'pulsed_tls.csv'), delimiter=',', names=True)
z = d[d['gstar_over_Gamma'] == 0]
ax[1].loglog(z['taup_Gamma'], z['g2'], 'o-', c='#1d2330', lw=1.8, ms=6, label='QuTiP ($\\gamma^*$ = 0)')
for x, lab, c in ((200e-15 * G, 'با آنتن، ۲۰۰ fs', '#1f4e9c'), (2e-12 * G, 'با آنتن، ۲ ps', '#b8892a'), (2e-12 / tau0, 'بدون آنتن، ۲ ps', '#7a8191')):
    y = np.interp(np.log(x), np.log(z['taup_Gamma']), z['g2']) if x >= z['taup_Gamma'].min() else z['g2'][0] * x / z['taup_Gamma'][0]
    ax[1].plot(x, y, '*', ms=15, c=c, label=lab)
ax[1].set_xlabel(r'$\tau_p\,\Gamma$'); ax[1].set_ylabel('g2(0)'); ax[1].legend(fontsize=8.6, loc='upper left')
ax[1].set_title('(ب) خلوص تک‌فوتونی: وابسته به طول پالس × آهنگ فروافت', fontsize=12)
r = np.logspace(-3, 0.3, 200)
ax[2].semilogx(r, 1 / (1 + 2 * r), c='0.35', lw=1.4, ls='--', label=r'$\Gamma/(\Gamma+2\gamma^*)$')
for tpg, c in ((0.02, '#1f4e9c'), (0.2, '#b8892a'), (2.0, '#9a3412')):
    q = d[(abs(d['taup_Gamma'] - tpg) < 1e-9) & (d['gstar_over_Gamma'] > 0)]
    ax[2].semilogx(q['gstar_over_Gamma'], q['I'], 'o-', c=c, lw=1.8, ms=6, label=f'QuTiP, $\\tau_p\\Gamma$ = {tpg:g}')
for g, lab in ((1e-6, '۱ µeV'), (10e-6, '۱۰ µeV'), (50e-6, '۵۰ µeV')):
    x = g / HB / G; ax[2].axvline(x, c='#2a7a4b', lw=0.8, ls=':'); ax[2].text(x * 1.08, 0.04, f'$\\gamma^*$ = {lab}\nبا آنتن', fontsize=8.5, color='#2a7a4b')
ax[2].set_ylim(0, 1.02); ax[2].set_xlabel(r'$\gamma^*/\Gamma$'); ax[2].set_ylabel('تمیزناپذیری I'); ax[2].legend(fontsize=9, loc='lower left')
ax[2].set_title('(ج) تمیزناپذیری: مدل کامل در برابر حد تحلیلی', fontsize=12)
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_s15_mech.png')); print('ok', 1e12 / G, HB * G * 1e6)
