"""Independent verification of section 15 (pulsed single-photon emission of the emitter on the trimer).

1. A second solver written from scratch (numpy + scipy.linalg.expm only, no QuTiP): Liouvillian of the driven two-level system
   with decay Gamma and pure dephasing gamma*, midpoint (second-order) propagators on a uniform grid, two-time correlations by the
   quantum regression theorem. Compared with the QuTiP results (pulsed_tls.run) for the cases of the report.
2. Analytic delta-pulse limit: I = Gamma / (Gamma + 2 gamma*), g2(0) = 0, N = 1.
3. Pulse-area check: integral of Omega(t) = pi, population after the pulse.
4. Correlation maps and the HBT peak shapes of the design case (figure fig_s15_corr.png).
5. Antenna input check: raw FDTD rows around 1550 nm, linear interpolation, convergence and gold-data variants (fig_s15_input.png).
6. Sensitivity of g2(0) and I to Fp (method, mesh, gold data), intrinsic lifetime tau0 and pulse length.
usage: python isi/analysis/verify_s15.py -> isi/results/verify_s15.md / .json, isi/figures/fig_s15_corr.png, fig_s15_input.png"""
import json, os, sys, time
import numpy as np, matplotlib
from scipy.linalg import expm
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
from pulsed_tls import run as qutip_run  # noqa: E402
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HB = 6.582119569e-16
LUM = os.path.join(ROOT, 'data', 'lab_20261111', 'lumerical')

# ---------------------------------------------------------------- independent two-level solver (units: Gamma = 1)
SM = np.array([[0, 1], [0, 0]], complex)        # sigma_- = |g><e|, basis (g, e)
SP = SM.conj().T; NE = SP @ SM; I2 = np.eye(2)
vec = lambda X: X.reshape(-1, order='F')
unvec = lambda v: v.reshape(2, 2, order='F')


def liouvillian(H, cops):
    L = -1j * (np.kron(I2, H) - np.kron(H.T, I2))
    for c in cops:
        cd = c.conj().T @ c
        L += np.kron(c.conj(), c) - 0.5 * np.kron(I2, cd) - 0.5 * np.kron(cd.T, I2)
    return L


def solve(taup, gstar, dt=None, keep=False):
    """taup = tau_p * Gamma, gstar = gamma*/Gamma. Non-uniform grid: fine (sigma/25) during the pulse, uniform dt after it
    (there the Liouvillian is constant). Returns N, g2, I (and correlation maps if keep)."""
    sf = np.sqrt(2) * taup / (2 * np.sqrt(2 * np.log(2)))
    A = np.pi / (np.sqrt(2 * np.pi) * sf); t0 = 4 * sf; tp_end = t0 + 4 * sf; T = tp_end + 12.0
    dt = dt or min(0.004, 0.05 / (0.5 + gstar))
    df = min(sf / 25, dt)
    t = np.unique(np.r_[np.arange(0, tp_end, df), np.arange(tp_end, T + dt / 2, dt)])
    nt = len(t) - 1; h = np.diff(t)
    cops = [SM, np.sqrt(2 * gstar) * NE]
    Om = lambda tt: A * np.exp(-0.5 * ((tt - t0) / sf) ** 2)
    L0 = liouvillian(np.zeros((2, 2)), cops); cache = {}
    U = []
    for k in range(nt):
        om = Om(t[k] + h[k] / 2)
        if om < 1e-10 * A:
            key = round(h[k], 12)
            if key not in cache: cache[key] = expm(L0 * h[k])
            U.append(cache[key])
        else: U.append(expm(liouvillian(0.5 * om * (SP + SM), cops) * h[k]))
    rho = np.zeros((nt + 1, 4), complex); rho[0] = vec(np.diag([1.0, 0.0]).astype(complex))
    for k in range(nt): rho[k + 1] = U[k] @ rho[k]
    pe = np.real(rho[:, 3]); N = np.trapezoid(pe, t)
    w = np.zeros(nt + 1); w[:-1] += h / 2; w[1:] += h / 2          # trapezoid weights in t
    trSP = vec(SP.T); trN = vec(NE.T)                                # Tr[A X] = vec(A^T) . vec(X)
    X = np.zeros((nt + 1, 4), complex); Y = np.zeros((nt + 1, 4), complex)
    S1 = S2 = 0.0
    if keep:
        ic = np.where(t >= tp_end - 1e-12)[0]; ev = max(1, len(ic) // 500); sel = ic[::ev]; pos = {j: n for n, j in enumerate(sel)}
        M1 = np.zeros((len(sel), len(sel))); M2 = np.zeros_like(M1)
        bw = 0.01; cent = np.zeros(int(T / bw) + 2)
    for k in range(nt + 1):
        r = unvec(rho[k]); X[k] = vec(SM @ r); Y[k] = vec(SM @ r @ SP)
        g1 = X[:k + 1] @ trSP; g2 = Y[:k + 1] @ trN               # G1(t_i, t_k - t_i), G2(t_i, t_k - t_i), i = 0..k
        wtau = np.full(k + 1, (h[k - 1] if k > 0 else 0) / 2 + (h[k] if k < nt else 0) / 2)   # tau weight of the point k for start i < k
        wtau[k] = (h[k] if k < nt else 0) / 2                                                  # tau = 0 end
        S1 += np.sum(w[:k + 1] * wtau * np.abs(g1) ** 2); S2 += np.sum(w[:k + 1] * wtau * np.real(g2))
        if keep: np.add.at(cent, ((t[k] - t[:k + 1]) / bw).astype(int), w[:k + 1] * wtau * np.real(g2))
        if keep and k in pos:
            ii = [j for j in sel if j <= k]; M1[[pos[j] for j in ii], [pos[k] - pos[j] for j in ii]] = np.abs(g1[ii]) ** 2
            M2[[pos[j] for j in ii], [pos[k] - pos[j] for j in ii]] = np.real(g2[ii])
        if k < nt:
            X[:k + 1] = X[:k + 1] @ U[k].T; Y[:k + 1] = Y[:k + 1] @ U[k].T
    out = dict(N=N, g2=2 * S2 / N ** 2, I=2 * S1 / N ** 2, area=np.trapezoid(Om(t), t), pe_max=pe.max(), dt=dt, npts=nt + 1)
    if keep:
        tb = np.arange(len(cent)) * bw; peu = np.interp(np.arange(0, T, bw), t, pe)
        side = np.correlate(peu, peu, 'full')[len(peu) - 1:] * bw
        out.update(t=t[sel], pe=pe[sel], dtp=dt * ev, M1=M1, M2=M2, t0=t0, sel=sel, cent=cent / bw, side=side, bw=bw)
    return out


def main():
    res = {}; lines = ['# Verification of section 15', '']
    # ---- antenna inputs
    d = np.genfromtxt(os.path.join(LUM, 'fdtd_sw_L275_R295.csv'), delimiter=',', names=True, skip_header=1); d = d[np.argsort(d['lambda_nm'])]
    i = np.searchsorted(d['lambda_nm'], 1550)
    rows = [{k: float(d[k][j]) for k in d.dtype.names} for j in (i - 1, i)]
    at = lambda dd, k: float(np.interp(1550, dd['lambda_nm'], dd[k]))
    res['raw_rows'] = rows
    var = {}
    for n, lab in (('sw_L275_R295', 'reference (gap mesh 1 nm, rods 2 nm, JC)'), ('sel_gap05', 'gap mesh 0.5 nm'), ('sel_rod1', 'rod mesh 1 nm'),
                   ('sel_conformal', 'conformal mesh'), ('sel_palik', 'gold: Palik'), ('sel_crc', 'gold: CRC')):
        x = np.genfromtxt(os.path.join(LUM, f'fdtd_{n}.csv'), delimiter=',', names=True, skip_header=1); x = x[np.argsort(x['lambda_nm'])]
        var[lab] = dict(Fp=at(x, 'Fp'), T=at(x, 'T'), eta=at(x, 'T') / at(x, 'Fp'), ratio=at(x, 'ff_py60') / at(x, 'ff_my60'),
                        ffcheck=at(x, 'ff_check'), na13=at(x, 'ff_zNA13'))
    var['BEM h = 3 nm (MNPBEM)'] = dict(Fp=240.46, T=181.05, eta=181.05 / 240.46, ratio=float('nan'), ffcheck=float('nan'), na13=0.282)
    res['variants'] = var
    # ---- figure: inputs
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.3))
    s = (d['lambda_nm'] > 1450) & (d['lambda_nm'] < 1650)
    ax[0].plot(d['lambda_nm'][s], d['Fp'][s], 'o-', c='#9a3412', ms=4, lw=1.6, label='Fp (نقطه‌های FDTD)')
    ax[0].plot(d['lambda_nm'][s], d['T'][s], 's-', c='#1f4e9c', ms=4, lw=1.6, label='T (نقطه‌های FDTD)')
    ax[0].axvline(1550, c='0.5', ls=':'); ax[0].plot([1550, 1550], [at(d, 'Fp'), at(d, 'T')], '*', c='k', ms=14, label='درون‌یابی خطی در ۱۵۵۰')
    ax[0].set_xlabel('طول موج (nm)'); ax[0].set_ylabel('نسبت به محیط همگن'); ax[0].legend(fontsize=10)
    ax[0].set_title('(الف) داده‌ی خام FDTD اطراف ۱۵۵۰ nm (طرح نهایی)', fontsize=12)
    labs = list(var); fa = [var[k]['Fp'] for k in labs]; ea = [100 * var[k]['eta'] for k in labs]
    yy = np.arange(len(labs)); ax[1].barh(yy - 0.2, fa, 0.4, color='#9a3412', label='Fp'); ax[1].barh(yy + 0.2, [e * 4 for e in ea], 0.4, color='#2a7a4b', label='بازده × ۴ (٪)')
    for k, (f, e) in enumerate(zip(fa, ea)): ax[1].text(f + 5, k - 0.2, f'{f:.0f}', va='center', fontsize=9); ax[1].text(4 * e + 5, k + 0.2, f'{e:.0f}%', va='center', fontsize=9)
    fa_lab = {'reference (gap mesh 1 nm, rods 2 nm, JC)': 'FDTD مرجع', 'gap mesh 0.5 nm': 'مش گاف ۰.۵ nm', 'rod mesh 1 nm': 'مش میله ۱ nm',
              'conformal mesh': 'مش منطبق', 'gold: Palik': 'طلا: Palik', 'gold: CRC': 'طلا: CRC', 'BEM h = 3 nm (MNPBEM)': 'BEM (h = ۳ nm)'}
    ax[1].set_yticks(yy); ax[1].set_yticklabels([fa_lab[k] for k in labs], fontsize=10); ax[1].invert_yaxis(); ax[1].legend(fontsize=10, loc='lower right')
    ax[1].set_title('(ب) ضریب پورسل و بازده در ۱۵۵۰ nm: همگرایی و حساسیت', fontsize=12); ax[1].set_xlim(0, 560)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_s15_input.png')); plt.close(fig)
    # ---- independent solver vs QuTiP
    Fp, tau0 = var['reference (gap mesh 1 nm, rods 2 nm, JC)']['Fp'], 2e-9
    G = Fp / tau0; G0 = 1 / tau0
    cases = [('با آنتن، ۲۰۰ fs، γ* = ۱ µeV', 200e-15 * G, 1e-6 / HB / G), ('با آنتن، ۲۰۰ fs، γ* = ۱۰ µeV', 200e-15 * G, 10e-6 / HB / G),
             ('با آنتن، ۲۰۰ fs، γ* = ۵۰ µeV', 200e-15 * G, 50e-6 / HB / G), ('با آنتن، ۲ ps، γ* = ۱ µeV', 2e-12 * G, 1e-6 / HB / G),
             ('بدون آنتن، ۲ ps، γ* = ۱ µeV', 2e-12 * G0, 1e-6 / HB / G0), ('بدون آنتن، ۲۰ ps، γ* = ۱ µeV', 20e-12 * G0, 1e-6 / HB / G0),
             ('آزمون: τpΓ = ۰.۵، γ*/Γ = ۰.۱', 0.5, 0.1), ('آزمون: τpΓ = ۲، γ*/Γ = ۱', 2.0, 1.0)]
    comp = []
    for lab, tp, gs in cases:
        t1 = time.time(); a = solve(tp, gs); t2 = time.time(); q = qutip_run(tp, gs); t3 = time.time()
        comp.append(dict(case=lab, taupG=tp, gsG=gs, N_ind=a['N'], g2_ind=a['g2'], I_ind=a['I'], N_qt=q[0], g2_qt=q[1], I_qt=q[2],
                         area=a['area'], pe_max=a['pe_max'], analytic=1 / (1 + 2 * gs), dt=a['dt']))
        print(lab, f"tp*G={tp:.4g} g*/G={gs:.4g}  ind N={a['N']:.4f} g2={a['g2']:.4f} I={a['I']:.4f} | qutip N={q[0]:.4f} g2={q[1]:.4f} I={q[2]:.4f} | "
              f"area/pi={a['area']/np.pi:.5f} ({t2-t1:.0f}+{t3-t2:.0f} s)", flush=True)
    res['comparison'] = comp
    # grid convergence of the independent solver for the design case
    conv = []
    for f in (2.0, 1.0, 0.5):
        a = solve(200e-15 * G, 1e-6 / HB / G, dt=0.004 * f)
        conv.append(dict(dt=a['dt'], npts=a['npts'], N=a['N'], g2=a['g2'], I=a['I'])); print('conv', conv[-1], flush=True)
    res['convergence'] = conv
    # delta-pulse limit (very short pulse)
    lim = []
    for tp in (0.02, 0.005):
        a = solve(tp, 0.1); lim.append(dict(taupG=tp, gs=0.1, N=a['N'], g2=a['g2'], I=a['I'], analytic_I=1 / 1.2)); print('limit', lim[-1], flush=True)
    res['delta_limit'] = lim
    # ---- sensitivity (QuTiP), I with gamma* = 1 and 10 ueV, 200 fs pulse
    sens = []
    for lab, F in (('FDTD مرجع', Fp), ('BEM h = 3 nm', 240.46), ('مش منطبق', var['conformal mesh']['Fp']), ('طلا: Palik', var['gold: Palik']['Fp']),
                   ('طلا: CRC', var['gold: CRC']['Fp']), ('فاصله‌ی R3 = ۹۰ nm', 254.6), ('فاصله‌ی R3 = ۱۱۰ nm', 317.0)):
        for t0_ in (2e-9, 1e-9):
            Gx = F / t0_; r = {'case': lab, 'Fp': F, 'tau0_ns': t0_ * 1e9, 'life_ps': 1e12 / Gx}
            for ge in (1e-6, 10e-6):
                N, g2, I = qutip_run(200e-15 * Gx, ge / HB / Gx); r[f'g2_{ge*1e6:.0f}'] = g2; r[f'I_{ge*1e6:.0f}'] = I
            sens.append(r); print('sens', r, flush=True)
    res['sensitivity'] = sens
    # ---- correlation maps of the design case
    a = solve(200e-15 * G, 1e-6 / HB / G, keep=True)
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6))
    tt = a['t'] - a['t0']; ext = [0, tt[-1] - tt[0], tt[0], tt[-1]]
    m = ax[0].imshow(a['M1'], origin='lower', aspect='auto', extent=ext, cmap='viridis'); fig.colorbar(m, ax=ax[0])
    ax[0].set_xlim(0, 5); ax[0].set_ylim(0, 5); ax[0].set_xlabel(r'$\tau\ \ [1/\Gamma = 7.0\ \mathrm{ps}]$'); ax[0].set_ylabel(r'$t\ \ [1/\Gamma]$')
    ax[0].set_title('(الف) مربع اندازه‌ی همبستگی مرتبه‌ی اول، پایه‌ی تمیزناپذیری', fontsize=12)
    c0 = a['cent']; sd = a['side']; n = min(len(c0), len(sd)); tau = np.arange(n) * a['bw']
    full = lambda y: np.r_[y[:n][::-1], y[1:n]]; tf = np.r_[-tau[::-1], tau[1:]]
    ax[1].plot(tf - 12, full(sd) / sd.max(), c='#7a8191', lw=1.8, label='قله‌ی کناری (دو پالس پیاپی)')
    ax[1].plot(tf, full(c0) / sd.max(), c='#9a3412', lw=2.2, label='قله‌ی مرکزی (یک پالس)')
    ax[1].plot(tf, 20 * full(c0) / sd.max(), c='#9a3412', lw=1.2, ls='--', label='قله‌ی مرکزی × ۲۰')
    ax[1].set_xlim(-17, 5); ax[1].set_xlabel(r'$\tau\ \ [1/\Gamma]$'); ax[1].set_ylabel('شمارش هم‌زمانی (بهنجار)')
    ax[1].legend(fontsize=9.5, loc='upper left'); ax[1].set_title('(ب) هیستوگرام شبیه‌سازی‌شده‌ی آزمایش HBT', fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_s15_corr.png')); plt.close(fig)
    res['hbt_area_ratio'] = float((2 * c0.sum() - c0[0]) / (2 * sd.sum() - sd[0]))
    json.dump(res, open(os.path.join(ROOT, 'results', 'verify_s15.json'), 'w'), indent=1, default=float)
    print('hbt ratio', res['hbt_area_ratio'])


if __name__ == '__main__':
    main()
