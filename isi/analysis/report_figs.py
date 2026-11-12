"""Extra figures for the comprehensive supervisor report (campaign 2 data, isi/data/lab_20261111/lumerical):
  fig_rep_sweep.png      FDTD retuning sweep: directionality and efficiency at 1550 nm vs R3 length, resonance positions
  fig_rep_patterns.png   in-plane (xy) and xz far-field patterns of the selected design at 1450 / 1550 / 1650 nm
  fig_rep_waveguide.png  guided fractions into a Si3N4 waveguide: selected trimer and dimer, earlier trimer
  fig_rep_tolerance.png  directionality spectra under mesh changes and R3 displacement
  fig_rep_quantum2.png   indistinguishability vs dephasing for several Purcell factors; photons per excitation vs intrinsic quantum yield
usage: python isi/analysis/report_figs.py"""
import os, json
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures'); RES = os.path.join(HERE, '..', 'results')
LUM = os.path.join(HERE, '..', 'data', 'lab_20261111', 'lumerical')
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
COL = {265: '#9a3412', 270: '#b8892a', 275: '#1f4e9c', 280: '#2a7a4b'}
HB = 6.582119569e-16


def fd(n):
    d = np.genfromtxt(os.path.join(LUM, f'fdtd_{n}.csv'), delimiter=',', names=True, skip_header=1); return d[np.argsort(d['lambda_nm'])]


at = lambda d, k, l=1550: float(np.interp(l, d['lambda_nm'], d[k]))


def peak(d, k):
    i = int(np.argmax(d[k])); return d['lambda_nm'][i]


def sweep():
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.1)); rows = []
    for L in (265, 270, 275, 280):
        xs, rs, es, ps = [], [], [], []
        for dL in (20, 30, 40):
            d = fd(f'sw_L{L}_R{L+dL}'); xs.append(L + dL); rs.append(at(d, 'ff_py60') / at(d, 'ff_my60')); es.append(100 * at(d, 'eta')); ps.append(peak(d, 'T'))
            rows.append((L, L + dL, rs[-1], es[-1], ps[-1], at(d, 'Fp'), at(d, 'T')))
        ax[0].plot(xs, rs, 'o-', c=COL[L], lw=2, ms=7, label=f'L = {L} nm'); ax[1].plot(xs, es, 'o-', c=COL[L], lw=2, ms=7, label=f'L = {L} nm')
        ax[2].plot(xs, ps, 'o-', c=COL[L], lw=2, ms=7, label=f'تریمر L = {L}')
        ax[2].plot([L + 40.5], [peak(fd(f'sw_L{L}'), 'T')], '*', c=COL[L], ms=13)
    ax[0].plot(295, rows[6][2], 'o', ms=17, mfc='none', mec='k', mew=2); ax[0].annotate('طرح انتخاب‌شده', (295, rows[6][2]), (-70, -30), textcoords='offset points', fontsize=11)
    ax[0].set_ylabel('نسبت +y/−y در ۱۵۵۰ nm'); ax[0].set_title('(الف) جهت‌دهی در ۱۵۵۰ nm', fontsize=12)
    ax[1].set_ylabel('بازده آنتن در ۱۵۵۰ nm (٪)'); ax[1].set_title('(ب) بازده', fontsize=12); ax[1].axhline(50, c='0.6', ls='--', lw=1)
    ax[2].set_ylabel('قله‌ی تقویت تابشی (nm)'); ax[2].set_title('(ج) مکان تشدید (ستاره: دیمر بدون R3)', fontsize=12)
    for a in ax: a.set_xlabel('طول میله‌ی سوم R3 (nm)'); a.legend(fontsize=9.5)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rep_sweep.png')); plt.close(fig)
    json.dump(rows, open(os.path.join(RES, 'sweep_campaign2.json'), 'w'), indent=1)
    return rows


def patterns():
    p = np.genfromtxt(os.path.join(LUM, 'fdtd_sw_L275_R295_pattern.csv'), delimiter=',', names=True, skip_header=1)
    th = np.radians(p['angle_deg']); th = np.append(th, th[0])
    fig = plt.figure(figsize=(11, 4.6))
    for k, (pl, t) in enumerate((('xy', '(الف) صفحه‌ی آنتن (xy)'), ('xz', '(ب) صفحه‌ی عمود (xz)'))):
        a = fig.add_subplot(1, 2, k + 1, projection='polar')
        for l, c in ((1450, '#7a8191'), (1550, '#1f4e9c'), (1650, '#b8892a')):
            u = p[f'U_{pl}_{l}']; a.plot(th, np.append(u, u[0]), c=c, lw=2.2 if l == 1550 else 1.4, label=f'{l} nm')
        a.set_title(t, fontsize=12, pad=14); a.set_rticks([0.5, 1.0]); a.tick_params(labelsize=9)
        a.set_xticks(np.radians([0, 90, 180, 270])); a.set_xticklabels(['+x', '+y' if pl == 'xy' else '+z', '−x', '−y' if pl == 'xy' else '−z'])
        if k == 0: a.legend(fontsize=10, loc='lower left', bbox_to_anchor=(-0.25, -0.12))
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rep_patterns.png')); plt.close(fig)


def waveguide():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.1))
    for n, c, lab in (('sel_wg_trimer', '#1f4e9c', 'تریمر نهایی'), ('wg_trimer_L285_R315', '#b8892a', 'تریمر قبلی'), ('sel_wg_dimer', '#7a8191', 'دیمر')):
        d = fd(n); ax[0].plot(d['lambda_nm'], 100 * d['beta_py'], c=c, lw=2.2, label=f'{lab}  +y'); ax[0].plot(d['lambda_nm'], 100 * d['beta_my'], c=c, lw=2.2, ls='--', label=f'{lab}  −y')
        ax[1].plot(d['lambda_nm'], d['beta_py'] / d['beta_my'], c=c, lw=2.2, label=lab)
    ax[0].set_ylabel('توان هدایت‌شده / توان کل گسیل (٪)'); ax[0].set_title('(الف) جفت‌شدگی به موجبر Si3N4 در دو جهت', fontsize=12); ax[0].legend(fontsize=8.8, ncol=2)
    ax[1].axhline(1, c='0.6', lw=0.8); ax[1].set_ylabel('نسبت +y/−y در موجبر'); ax[1].set_title('(ب) جهت‌دهی درون موجبر', fontsize=12); ax[1].legend(fontsize=10)
    for a in ax: a.axvline(1550, c='0.55', ls=':', lw=1.2); a.set_xlim(1300, 1700); a.set_xlabel('طول موج (nm)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rep_waveguide.png')); plt.close(fig)


def tolerance():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.1))
    for n, c, lab in (('sw_L275_R295', '#1d2330', 'مرجع'), ('sel_gap05', '#1f4e9c', 'مش گاف ۰.۵ nm'), ('sel_rod1', '#2a7a4b', 'مش میله ۱ nm'), ('sel_conformal', '#b8892a', 'مش منطبق (conformal)')):
        d = fd(n); ax[0].plot(d['lambda_nm'], d['ff_py60'] / d['ff_my60'], c=c, lw=2.2 if n.startswith('sw') else 1.6, label=lab)
    for n, c, lab in (('sel_Y150', '#9a3412', 'R3 در y = ۱۵۰'), ('sw_L275_R295', '#1d2330', 'R3 در y = ۱۶۰ (طرح)'), ('sel_Y170', '#2a7a4b', 'R3 در y = ۱۷۰')):
        d = fd(n); ax[1].plot(d['lambda_nm'], d['ff_py60'] / d['ff_my60'], c=c, lw=2.2, label=lab)
    ax[0].set_title('(الف) حساسیت به مش FDTD', fontsize=12); ax[1].set_title('(ب) تلرانس ساخت: جای میله‌ی سوم', fontsize=12)
    for a in ax: a.axvline(1550, c='0.55', ls=':', lw=1.2); a.axhline(1, c='0.6', lw=0.8); a.set_xlim(1300, 1700); a.set_xlabel('طول موج (nm)'); a.set_ylabel('نسبت +y/−y'); a.legend(fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rep_tolerance.png')); plt.close(fig)


def quantum2():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.1))
    g = np.logspace(-1, 4, 300) * 1e-6
    for F, c in ((1, '#7a8191'), (30, '#b8892a'), (100, '#2a7a4b'), (286, '#1f4e9c')):
        G = F / 2e-9; ax[0].semilogx(g * 1e6, G / (G + 2 * g / HB), c=c, lw=2.2, label=f'Fp = {F}')
    ax[0].set_xlabel('آهنگ ناهمدوسی خالص (µeV)'); ax[0].set_ylabel('تمیزناپذیری (حد پالس کوتاه)'); ax[0].set_ylim(0, 1.02)
    ax[0].set_title('(الف) نقش ضریب پورسل در تمیزناپذیری (طول عمر ذاتی ۲ ns)', fontsize=12); ax[0].legend(fontsize=10)
    q = np.linspace(0.02, 1, 100); Fp, T = 286.0, 199.0
    ax[1].plot(q, q, c='#7a8191', lw=2.2, label='بدون آنتن (= بازده ذاتی)')
    ax[1].plot(q, q * T / (q * Fp + 1 - q), c='#1f4e9c', lw=2.2, label='با آنتن، دوقطبی x')
    Fi, Ti = 96.0, 199.0 / 3
    ax[1].plot(q, q * Ti / (q * Fi + 1 - q), c='#b8892a', lw=2.2, ls='--', label='با آنتن، دوقطبی همسانگرد')
    ax[1].set_xlabel('بازده کوانتومی ذاتی گسیلنده (q0)'); ax[1].set_ylabel('فوتون به دوردست در هر تحریک'); ax[1].set_ylim(0, 1.02)
    ax[1].set_title('(ب) آنتن گسیلنده‌ی کم‌بازده را بهتر می‌کند', fontsize=12); ax[1].legend(fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rep_quantum2.png')); plt.close(fig)


if __name__ == '__main__':
    r = sweep(); waveguide(); tolerance(); quantum2()
    for x in r: print('L %d R3 %d ratio %.2f eta %.0f%% peakT %.0f Fp %.0f T %.0f' % x)
