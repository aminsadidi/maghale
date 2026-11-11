"""Final telecom design after retuning (L = 275, R3 = 295 nm, Y3 = 160 nm): FDTD (Lumerical, far field) vs BEM (h = 4, 3 nm),
and the gold-data sensitivity (Johnson-Christy, CRC, Palik; FDTD).
usage: python isi/analysis/final_design2.py -> isi/figures/fig_sel_design.png"""
import os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures'); LUM = os.path.join(HERE, '..', 'data', 'lab_20261111', 'lumerical')
sys.path.insert(0, HERE); import tri2
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})


def fd(n):
    d = np.genfromtxt(os.path.join(LUM, f'fdtd_{n}.csv'), delimiter=',', names=True, skip_header=1); return d[np.argsort(d['lambda_nm'])]


F = fd('sw_L275_R295'); B4, _ = tri2.series('L275_R295_A0_Y160_H4'); B3, _ = tri2.series('L275_R295_A0_Y160_H3')
fig, ax = plt.subplots(1, 3, figsize=(15, 4.1))
ax[0].plot(F['lambda_nm'], F['Fp'], c='#c0392b', lw=2.2, label='FDTD  Fp'); ax[0].plot(F['lambda_nm'], F['T'], c='#c0392b', lw=2.2, ls='--', label='FDTD  T')
for B, c, h in ((B4, '#7f9cc9', 4), (B3, '#1f4e9c', 3)):
    s = (B['lambda_nm'] >= 1300) & (B['lambda_nm'] <= 1700)
    ax[0].plot(B['lambda_nm'][s], B['Fp_x_c'][s], c=c, lw=1.6, label=f'BEM h={h}  Fp'); ax[0].plot(B['lambda_nm'][s], B['T_x_c'][s], c=c, lw=1.6, ls='--', label=f'BEM h={h}  T')
ax[0].set_ylabel('تقویت نسبت به محیط'); ax[0].set_title('(الف) فاکتور پورسل و تقویت تابشی', fontsize=12); ax[0].legend(fontsize=8.5, ncol=2, loc='upper right')
ax[1].plot(F['lambda_nm'], F['ff_py60'] / F['ff_my60'], c='#c0392b', lw=2.4, label='FDTD (میدان دوردست)')
for B, c, h in ((B4, '#7f9cc9', 4), (B3, '#1f4e9c', 3)):
    s = (B['lambda_nm'] >= 1300) & (B['lambda_nm'] <= 1700)
    ax[1].plot(B['lambda_nm'][s], (B['f_py60_x_c'] / B['f_my60_x_c'])[s], c=c, lw=1.8, label=f'BEM h = {h} nm')
ax[1].axhline(1, c='0.6', lw=0.8); ax[1].set_ylabel('نسبت +y/−y (مخروط ۶۰ درجه)'); ax[1].set_title('(ب) جهت‌دهی: همگرایی BEM به سمت FDTD', fontsize=12)
ax[1].legend(fontsize=10, loc='upper left')
for n, c, lab in (('sw_L275_R295', '#1d2330', 'Johnson-Christy'), ('sel_crc', '#2a7a4b', 'CRC'), ('sel_palik', '#b8892a', 'Palik')):
    d = fd(n); ax[2].plot(d['lambda_nm'], d['ff_py60'] / d['ff_my60'], c=c, lw=2.2, label=lab)
ax[2].axhline(1, c='0.6', lw=0.8); ax[2].set_ylabel('نسبت +y/−y'); ax[2].set_title('(ج) حساسیت به داده‌ی طلا (FDTD)', fontsize=12); ax[2].legend(fontsize=10, loc='upper left')
for a in ax: a.axvline(1550, c='0.55', ls=':', lw=1.2); a.set_xlim(1300, 1700); a.set_xlabel('طول موج (نانومتر)')
fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_sel_design.png')); print('ok')
