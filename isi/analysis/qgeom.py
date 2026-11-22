"""g2(0) and indistinguishability versus geometry with the Green-function emitter-antenna model (qmodel.py).
For every BEM geometry (job_tri2, emitter x dipole at the gap centre, 1550 nm, tau0 = 2 ns): antenna modes (omega_j, kappa_j, g_j),
Lamb shift, Purcell rate, local-field enhancement K; then the pulsed quantum dynamics (200 fs local pi pulse, gamma* = 1 and 10 ueV),
laser tuned to the shifted (dressed) transition and, to show the Lamb shift, to the bare transition. The explicit emitter + modes model
is solved for every geometry at gamma* = 1 ueV as a check of the effective (Markov) model.
usage: python isi/analysis/qgeom.py -> isi/results/qgeom.json, qgeom.md, isi/figures/fig_q_modes.png, fig_q_geom.png, fig_q_lamb.png"""
import glob, json, os, re, sys, time
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import qmodel as Q, gmodes  # noqa: E402
plt.rcParams.update({'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HC = 1239.841984; TP = 200e-15
GROUPS = {
    'gap': [('L235_G10', 10), ('L255_G20', 20), ('L270', 40)],
    'angle': [('L270_R300_A0_Y160', 0), ('L270_R300_A20_Y160', 20), ('L270_R300_A27_Y160', 27), ('L270_R300_A35_Y160', 35)],
    'y3': [('L285_R315_A0_Y150', 150), ('L285_R315_A0_Y160', 160), ('L285_R315_A0_Y170', 170)],
    'y3b': [('L270_R300_A35_Y160', 160), ('L270_R300_A35_Y190', 190), ('L270_R300_A35_Y220', 220)],
    'l3': [('L270_R260_A35_Y160', 260), ('L270_R280_A35_Y160', 280), ('L270_R300_A35_Y160', 300), ('L270_R320_A35_Y160', 320), ('L270_R340_A35_Y160', 340)],
    'L': [('L240', 240), ('L260', 260), ('L270', 270), ('L280', 280)],
    'n': [('L270_N1.33', 1.33), ('L270_N1.45', 1.45), ('L270', 1.5), ('L270_N1.6', 1.6), ('L270_N1.7', 1.7)],
}


def run_one(stem, explicit_check=True):
    P = Q.params(stem)
    r = dict(stem=stem, Fp=P['Fp'], T=P['T'], eta=P['T'] / P['Fp'], ratio=P['ratio'], K=P['K'], hG=P['G_eff'], delta=P['delta_eff'],
             delta_green=P['delta_green'], rms_im=P['rms_im'], rms_re=P['rms_re'],
             modes=[dict(lam=HC / m['E'], E=m['E'], kappa=m['kappa'], g=m['g'], A=m['A']) for m in P['modes']])
    r['life_ps'] = 6.582119569e-16 / P['G_eff'] * 1e12
    for gs in (1e-6, 10e-6):
        a = Q.solve(P, TP, gs, 0.0, explicit=False); r[f'g2_{gs*1e6:.0f}'], r[f'I_{gs*1e6:.0f}'], r[f'pe_{gs*1e6:.0f}'] = a['g2'], a['I'], a['pe_max']
    b = Q.solve(P, TP, 1e-6, -P['delta_eff'], explicit=False)          # laser on the bare transition
    r['bare_g2'], r['bare_I'], r['bare_pe'] = b['g2'], b['I'], b['pe_max']
    if explicit_check:
        c = Q.solve(P, TP, 1e-6, 0.0, explicit=True, detect='s'); r['x_g2'], r['x_I'], r['x_pe'] = c['g2'], c['I'], c['pe_max']
    return r


def main():
    stems = sorted({re.sub(r'_c\d+\.csv', '', os.path.basename(f))[5:] for f in glob.glob(os.path.join(ROOT, 'results', 'bem_extra', 'tri2_*_c6.csv'))})
    R = {}
    for s in stems:
        t = time.time(); R[s] = run_one(s); r = R[s]
        print(f"{s:26s} Fp {r['Fp']:7.1f} hG {r['hG']*1e6:7.1f} d {r['delta']*1e6:8.1f} ueV | g2 {r['g2_1']:.4f} I1 {r['I_1']:.4f} I10 {r['I_10']:.4f} | "
              f"explicit g2 {r['x_g2']:.4f} I {r['x_I']:.4f} | bare: pe {r['bare_pe']:.3f} ({time.time()-t:.0f} s)", flush=True)
    json.dump(R, open(os.path.join(ROOT, 'results', 'qgeom.json'), 'w'), indent=1, default=float)
    # Lamb shift vs pulse length (final design and gap 10 nm)
    lamb = []
    for s in ('L275_R295_A0_Y160_H3', 'L235_G10'):
        P = Q.params(s)
        for tp in (0.2e-12, 2e-12, 10e-12, 30e-12):
            for lab, ld in (('dressed', 0.0), ('bare', -P['delta_eff'])):
                if tp * P['G_eff'] / 6.582e-16 > 3.5: continue
                a = Q.solve(P, tp, 1e-6, ld, explicit=False)
                lamb.append(dict(stem=s, tp=tp, laser=lab, g2=a['g2'], I=a['I'], pe=a['pe_max'], N=a['N'])); print('lamb', lamb[-1], flush=True)
    json.dump(dict(R=R, lamb=lamb), open(os.path.join(ROOT, 'results', 'qgeom.json'), 'w'), indent=1, default=float)
    figures(R, lamb)


def figures(R, lamb):
    # ---- modes of the final design
    d = gmodes.load('L275_R295_A0_Y160_H3'); P = Q.params('L275_R295_A0_Y160_H3'); Ee = P['Ee']
    f = gmodes.fit(d, 2, Ee); E = d['E']; Ef = np.linspace(E.min(), E.max(), 400)
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.4))
    ax[0].plot(HC / E, d['ImG'], 'o', c='#1d2330', ms=4, label='BEM: Im G')
    ax[0].plot(HC / Ef, gmodes.model_im(f['p'], Ef, Ee), c='#9a3412', lw=2, label='fit: 2 modes')
    for j in range(2):
        ax[0].plot(HC / Ef, gmodes.model_im(f['p'][3 * j:3 * j + 3], Ef, Ee), c=['#1f4e9c', '#2a7a4b'][j], lw=1.2, ls='--', label=f'mode {j+1}')
    ax[0].axvline(1550, c='0.5', ls=':'); ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('Im G (normalised)'); ax[0].legend(fontsize=9.5)
    ax[0].set_title('(a) spectral density (Im G) and the two antenna modes', fontsize=12)
    X = np.c_[(Ee / E) ** 3, np.ones_like(E)]; c, *_ = np.linalg.lstsq(X, d['ReG'] - gmodes.model_re(f['p'], E, Ee), rcond=None)
    Xf = np.c_[(Ee / Ef) ** 3, np.ones_like(Ef)]
    ax[1].plot(HC / E, d['ReG'], 'o', c='#1d2330', ms=4, label='BEM: Re G')
    ax[1].plot(HC / Ef, gmodes.model_re(f['p'], Ef, Ee) + Xf @ c, c='#9a3412', lw=2, label='predicted by the modes + background')
    ax[1].axvline(1550, c='0.5', ls=':'); ax[1].set_xlabel('wavelength (nm)'); ax[1].set_ylabel('Re G (normalised)'); ax[1].legend(fontsize=9.5)
    ax[1].set_title('(b) Kramers-Kronig test: predicted Re G', fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_q_modes.png')); plt.close(fig)
    # ---- geometry: quantum figures of merit (left) and g2 (right)
    panels = [('gap', 'dimer gap (nm)', '(a) gap between R1 and R2'), ('angle', 'angle of R3 (deg)', '(b) angle of R3 (L = 270)'),
              ('y3', 'centre of R3, Y3 (nm)', '(c) distance of R3 (L = 285)'), ('l3', 'length of R3 (nm)', '(d) length of R3 (L = 270)'),
              ('L', 'dimer arm length (nm)', '(e) dimer length (no R3)'), ('n', 'host refractive index', '(f) host medium (dimer L = 270)')]
    for name, key in (('fig_q_geom.png', 'q'), ('fig_q_rates.png', 'r')):
        fig, ax = plt.subplots(2, 3, figsize=(16, 8.6)); ax = ax.ravel()
        for a, (g, xl, tl) in zip(ax, panels):
            xs = [x for s_, x in GROUPS[g]]; rr = [R[s_] for s_, x in GROUPS[g]]
            if key == 'q':
                a.plot(xs, [r['I_1'] for r in rr], 'o-', c='#2a7a4b', lw=2, ms=6, label=r'I  ($\gamma^*$ = 1 µeV)')
                a.plot(xs, [r['I_10'] for r in rr], 's--', c='#2a7a4b', lw=1.5, ms=5, label=r'I  ($\gamma^*$ = 10 µeV)')
                a.plot(xs, [r['x_I'] for r in rr], 'x', c='k', ms=9, mew=1.6, label='I  (explicit emitter + modes)')
                a.set_ylim(0.6, 1.0); a.set_ylabel('indistinguishability I', color='#2a7a4b')
                b2 = a.twinx(); b2.plot(xs, [r['g2_1'] for r in rr], 'D-', c='#b8892a', lw=2, ms=5); b2.plot(xs, [r['x_g2'] for r in rr], '+', c='k', ms=9)
                b2.set_ylabel('g2(0)  (gamma* = 1 ueV)', color='#b8892a'); b2.grid(False); b2.set_ylim(0, max(0.02, 1.15 * max(r['g2_1'] for r in rr)))
                if g == 'gap': a.legend(fontsize=8.6, loc='lower right')
            else:
                a.semilogy(xs, [r['hG'] * 1e6 for r in rr], 'o-', c='#9a3412', lw=2, ms=6, label=r'$\hbar\Gamma$ (µeV)')
                a.semilogy(xs, [-r['delta'] * 1e6 for r in rr], 's-', c='#1f4e9c', lw=2, ms=6, label=r'$-\hbar\delta$ (µeV), from modes')
                a.semilogy(xs, [-r['delta_green'] * 1e6 for r in rr], 'x', c='k', ms=9, label=r'$-\hbar\delta$ (µeV), direct Re G')
                a.semilogy(xs, [max(m['g'] for m in r['modes']) * 1e6 for r in rr], '^--', c='#7a8191', lw=1.4, ms=6, label=r'$\hbar g_{max}$ (µeV)')
                a.set_ylabel('energy (µeV), log scale')
                if g == 'gap': a.legend(fontsize=8.6)
            a.set_xlabel(xl); a.set_title(tl, fontsize=12)
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', name)); plt.close(fig)
    # ---- Lamb shift vs pulse length
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.3))
    for k, (s_, tl) in enumerate((('L275_R295_A0_Y160_H3', '(a) final design (gap 40 nm)'), ('L235_G10', '(b) dimer with gap 10 nm'))):
        for lab, c in (('dressed', '#1f4e9c'), ('bare', '#9a3412')):
            rr = [x for x in lamb if x['stem'] == s_ and x['laser'] == lab]
            tp = [x['tp'] * 1e12 for x in rr]
            ax[k].semilogx(tp, [x['pe'] for x in rr], 'o-', c=c, lw=2, ms=6, label=('max. excited population, laser on the ' + ('shifted line' if lab == 'dressed' else 'bare line')))
            ax[k].semilogx(tp, [x['g2'] for x in rr], 's--', c=c, lw=1.5, ms=5, label='g2(0), laser on the ' + ('shifted line' if lab == 'dressed' else 'bare line'))
        ax[k].set_xlabel('pulse length (ps)'); ax[k].set_ylim(0, 1.02); ax[k].set_title(tl, fontsize=12); ax[k].grid(True); ax[k].legend(fontsize=8.6)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_q_lamb.png')); plt.close(fig)

if __name__ == '__main__':
    if '--figs' in sys.argv:
        J = json.load(open(os.path.join(ROOT, 'results', 'qgeom.json'))); figures(J['R'], J['lamb'])
    else: main()
