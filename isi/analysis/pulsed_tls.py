"""Pulsed excitation of a Purcell-enhanced two-level emitter (QuTiP master equation).

Resonant Gaussian pi-pulse (intensity FWHM tau_p), radiative+non-radiative decay Gamma (the Purcell-enhanced total
rate), pure dephasing gamma* (coherences decay at Gamma/2 + gamma*). In units of 1/Gamma. For a single pulse:
    N   = int <s+ s->(t) dt                                   (emitted photons per pulse, before eta)
    g2  = 2 int_0^inf dt int_0^inf dtau G2(t, tau) / N^2       (area of the zero-delay peak / side peak)
    I   = 2 int dt int dtau |G1(t, tau)|^2 / N^2               (two-photon interference visibility, Fischer et al.)
G1(t, tau) = <s+(t+tau) s-(t)>, G2(t, tau) = <s+(t) s+(t+tau) s-(t+tau) s-(t)>.
usage: python isi/analysis/pulsed_tls.py -> isi/results/pulsed_tls.md, isi/results/pulsed_tls.csv
"""
import os, numpy as np, qutip as qt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')

sm = qt.destroy(2); sp = sm.dag(); n = sp * sm


def run(taup, gstar, nt=400):
    """taup, gstar in units of 1/Gamma and Gamma. Returns N, g2, I."""
    s = taup / (2 * np.sqrt(2 * np.log(2)))          # Gaussian sigma of the intensity -> field area pi
    sig_f = s * np.sqrt(2)                            # Rabi envelope ~ sqrt(intensity) -> sigma_field = sqrt(2) sigma_int
    A = np.pi / (np.sqrt(2 * np.pi) * sig_f)
    t0 = 4 * sig_f
    H = [[0.5 * (sp + sm), lambda t: A * np.exp(-0.5 * ((t - t0) / sig_f) ** 2)]]
    c_ops = [sm, np.sqrt(2 * gstar) * n]
    T = t0 + 4 * sig_f + 12.0
    tp_end = t0 + 4 * sig_f                            # dense grids where the pulse acts (t) and for short delays (tau)
    tl = np.unique(np.concatenate([np.linspace(0, tp_end, nt // 2), np.linspace(tp_end, T, nt // 2)]))
    taul = np.unique(np.concatenate([np.linspace(0, 8 * sig_f, nt // 2), np.linspace(8 * sig_f, T - tp_end, nt // 2)]))
    rho0 = qt.basis(2, 0) * qt.basis(2, 0).dag()
    pop = qt.mesolve(H, rho0, tl, c_ops, e_ops=[n]).expect[0]
    N = np.trapezoid(pop, tl)
    G1 = qt.correlation_2op_2t(H, rho0, tl, taul, c_ops, sp, sm)          # <sp(t+tau) sm(t)>
    G2 = qt.correlation_3op_2t(H, rho0, tl, taul, c_ops, sp, n, sm)       # <sp(t) n(t+tau) sm(t)>
    tz = lambda F: np.trapezoid(np.trapezoid(F, taul, axis=1), tl)
    g2 = 2 * tz(np.real(G2)) / N ** 2
    I = 2 * tz(np.abs(G1) ** 2) / N ** 2
    return N, g2, I


def main():
    rows = []
    for taup in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0):
        for gs in (0.0, 0.01, 0.1, 1.0):
            N, g2, I = run(taup, gs)
            rows.append((taup, gs, N, g2, I)); print(f'tau_p*Gamma={taup:5.2f} gamma*/Gamma={gs:5.2f}: N={N:.3f} g2={g2:.4f} I={I:.4f}')
    np.savetxt(os.path.join(RES, 'pulsed_tls.csv'), np.array(rows), delimiter=',', header='taup_Gamma,gstar_over_Gamma,N,g2,I', comments='')
    # translate to resonance-matched nanorods (telecom.md, bright emitter q0 = 1, tau_0 = 1 ns): Gamma = Fp / tau_0
    designs = [('810 nm', 5, 2305), ('810 nm', 20, 125), ('1550 nm', 5, 5305), ('1550 nm', 10, 1736), ('1550 nm', 20, 378)]
    out = ['# Pulsed two-level emitter (QuTiP): g2(0) and indistinguishability vs pulse length and dephasing', '',
           '| tau_p Gamma | gamma*/Gamma | N | g2(0) | I |', '|---|---|---|---|---|']
    out += [f'| {r[0]} | {r[1]} | {r[2]:.3f} | {r[3]:.4f} | {r[4]:.4f} |' for r in rows]
    out += ['', '## Resonance-matched gold nanorods (n = 1.45), q0 = 1, tau_0 = 1 ns', '',
            '| emitter | gap | Fp | 1/Gamma (fs) | pulse | gamma* | tau_p Gamma | g2(0) | I |', '|---|---|---|---|---|---|---|---|---|']
    hb = 6.582e-16
    for lab, g, F in designs:
        G = F / 1e-9                                  # s^-1
        for tp in (100e-15, 1e-12):
            for gs_eV, gl in ((1e-6, '1 ueV (4 K)'), (1e-2, '10 meV (300 K)')):
                gs = gs_eV / hb
                N, g2, I = run(tp * G, gs / G)
                out.append(f'| {lab} | {g} | {F} | {1e15/G:.0f} | {tp*1e15:.0f} fs | {gl} | {tp*G:.3g} | {g2:.3f} | {I:.3f} |')
    open(os.path.join(RES, 'pulsed_tls.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out[-22:]))


if __name__ == '__main__':
    main()
