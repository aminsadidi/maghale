"""Detailed figures for the supervisor: the three-nanorod (trimer) final design L275_R295_A0_Y160_H3 and its two-mode description.
  fig_d1_geometry.png  top view of the trimer with all dimensions, emitter positions and the dipole orientation
  fig_d2_spectra.png   raw BEM outputs vs wavelength (Purcell, radiative enhancement, efficiency, Im G / Re G, directionality, mesh h = 3 vs 4)
  fig_d3_nmodes.png    Im G fitted with 1, 2 and 3 Lorentzian modes + relative residuals
  fig_d4_origin.png    dimer alone (no R3) vs trimer: where the two modes come from
  fig_d5_position.png  three emitter positions (gap centre, 5 nm along x, 10 nm along y): Im G and two-mode couplings
usage: python isi/analysis/modes_detail.py -> isi/figures/fig_d*.png, isi/results/modes_detail.json"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import gmodes, tri2  # noqa: E402
plt.rcParams.update({'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HC = 1239.841984; EE = HC / 1550; STEM = 'L275_R295_A0_Y160_H3'
FIG = os.path.join(ROOT, 'figures'); C = dict(k='#1d2330', r='#9a3412', b='#1f4e9c', g='#2a7a4b', y='#b8892a', s='#7a8191')


def rod(ax, xc, yc, L, D=60, ang=0, **kw):
    p = FancyBboxPatch((xc - L / 2, yc - D / 2), L, D, boxstyle=f'round,pad=0,rounding_size={D/2}', **kw)
    import matplotlib.transforms as mt
    p.set_transform(mt.Affine2D().rotate_deg_around(xc, yc, ang) + ax.transData); ax.add_patch(p)


def fig_geometry():
    fig, ax = plt.subplots(figsize=(11, 5.6))
    L, g, L3, Y3 = 275, 40, 295, 160; xc = g / 2 + L / 2
    kw = dict(fc='#e9c46a', ec='#8a6d1d', lw=1.4)
    rod(ax, -xc, 0, L, **kw); rod(ax, xc, 0, L, **kw); rod(ax, 0, Y3, L3, **kw)
    ax.text(-xc, 0, 'R1', ha='center', va='center', fontsize=13); ax.text(xc, 0, 'R2', ha='center', va='center', fontsize=13)
    ax.text(0, Y3, 'R3', ha='center', va='center', fontsize=13)
    # emitter positions
    for (x, y), c, lab in (((0, 0), C['r'], 'c'), ((5, 0), C['b'], 'px5'), ((0, 10), C['g'], 'py10')):
        ax.plot(x, y, 'o', c=c, ms=6, zorder=5)
    ax.annotate('', xy=(18, -0.0), xytext=(-18, 0), arrowprops=dict(arrowstyle='<->', color=C['r'], lw=1.6))
    ax.text(0, -78, 'emitter (x dipole)\nat the gap centre', ha='center', va='top', fontsize=10.5, color=C['r'])
    # dimensions
    def dim(x0, y0, x1, y1, t, off=(0, 0), **k):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='<->', color='0.3', lw=1))
        ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], t, ha='center', va='center', fontsize=10.5, color='0.2', **k)
    dim(-xc - L / 2, -45, -xc + L / 2, -45, 'L = 275 nm', (0, -14)); dim(xc - L / 2, -45, xc + L / 2, -45, 'L = 275 nm', (0, -14))
    dim(-g / 2, 42, g / 2, 42, 'gap 40 nm', (0, 13)); dim(-L3 / 2, Y3 + 50, L3 / 2, Y3 + 50, 'L3 = 295 nm', (0, 14))
    dim(xc + L / 2 + 45, 0, xc + L / 2 + 45, Y3, 'Y3 = 160 nm', (16, 0), rotation=90)
    dim(xc + L / 2 + 12, -30, xc + L / 2 + 12, 30, 'D = 60', (14, 0), rotation=90)
    ax.text(0, Y3 - 52, 'R3 to dimer, surface to surface: 100 nm', ha='center', fontsize=10, color='0.35')
    ax.annotate('', xy=(-xc - L / 2 - 30, 90), xytext=(-xc - L / 2 - 30, 20), arrowprops=dict(arrowstyle='->', color='0.3'))
    ax.text(-xc - L / 2 - 30, 100, '+y', ha='center', fontsize=10.5)
    ax.annotate('', xy=(-xc - L / 2 + 40, 20 - 0), xytext=(-xc - L / 2 - 30, 20), arrowprops=dict(arrowstyle='->', color='0.3'))
    ax.text(-xc - L / 2 + 52, 20, '+x', va='center', fontsize=10.5)
    ax.text(-xc - L / 2 - 30, -60, 'z out of page\n(collection from +z)', ha='center', va='top', fontsize=9.5, color='0.35')
    ax.set_aspect('equal'); ax.set_xlim(-xc - L / 2 - 90, xc + L / 2 + 90); ax.set_ylim(-120, Y3 + 90); ax.axis('off')
    ax.set_title('Final three-rod design, top view (gold rods in the plane z = 0, host n = 1.5)', fontsize=13)
    fig.savefig(os.path.join(FIG, 'fig_d1_geometry.png')); plt.close(fig)


def fig_spectra(out):
    d3, _ = tri2.series(STEM); d4, _ = tri2.series(STEM.replace('H3', 'H4')); dm, _ = tri2.series('L270')
    lam = d3['lambda_nm']
    fig, ax = plt.subplots(2, 2, figsize=(14, 8.6)); ax = ax.ravel()
    a = ax[0]
    a.plot(lam, d3['Fp_x_c'], '-o', c=C['r'], ms=3.5, lw=2, label='Fp = total rate / $\Gamma_0$ (mesh 3 nm)')
    a.plot(lam, d3['T_x_c'], '-s', c=C['b'], ms=3.5, lw=2, label='T = radiated power / free dipole (mesh 3 nm)')
    a.plot(d4['lambda_nm'], d4['Fp_x_c'], '--', c=C['r'], lw=1.2, label='Fp (mesh 4 nm)')
    a.plot(d4['lambda_nm'], d4['T_x_c'], '--', c=C['b'], lw=1.2, label='T (mesh 4 nm)')
    a.set_ylabel('enhancement factor'); a.set_title('(a) total and radiative rate, emitter at the gap centre', fontsize=12); a.legend(fontsize=9)
    a = ax[1]
    a.plot(lam, 100 * d3['T_x_c'] / d3['Fp_x_c'], '-o', c=C['g'], ms=3.5, lw=2, label='antenna efficiency $\eta$ = T / Fp')
    a.plot(lam, 100 * d3['f_zNA13_x_c'], '-', c=C['y'], lw=2, label='fraction of radiated power in NA 1.3 (+z)')
    a.plot(lam, 100 * d3['f_zNA09_x_c'], '--', c=C['y'], lw=1.5, label='fraction of radiated power in NA 0.9 (+z)')
    a.set_ylabel('%'); a.set_ylim(0, 100); a.set_title('(b) efficiency and collected fraction', fontsize=12); a.legend(fontsize=9)
    a = ax[2]
    a.plot(lam, d3['ImG_x_c'], '-o', c=C['k'], ms=3.5, lw=2, label='Im G  (= Fp - 1)')
    a.plot(lam, d3['ReG_x_c'], '-s', c=C['s'], ms=3.5, lw=2, label='Re G')
    a.plot(dm['lambda_nm'], dm['ImG_x_c'], ':', c=C['k'], lw=1.5, label='Im G, dimer alone (L = 270, no R3)')
    a.set_ylabel('normalised Green function'); a.set_title('(c) input of the quantum model: Im G and Re G', fontsize=12); a.legend(fontsize=9)
    a = ax[3]
    a.plot(lam, d3['f_py60_x_c'] / d3['f_my60_x_c'], '-o', c=C['b'], ms=3.5, lw=2, label='trimer: power to +y / power to -y (60 deg cones)')
    a.plot(dm['lambda_nm'], dm['f_py60_x_c'] / dm['f_my60_x_c'], ':', c=C['k'], lw=1.5, label='dimer alone (symmetric: 1)')
    a.set_ylabel('directivity ratio +y / -y'); a.set_title('(d) in-plane directivity created by R3', fontsize=12); a.legend(fontsize=9)
    for a in ax: a.axvline(1550, c='0.5', ls=':', lw=1); a.set_xlabel('wavelength (nm)'); a.set_xlim(1100, 1900)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_d2_spectra.png')); plt.close(fig)
    e = lambda d, k: float(np.interp(1550, d['lambda_nm'], d[k]))
    i = int(np.argmax(d3['Fp_x_c']))
    out['spectra'] = dict(peak_lam=float(lam[i]), peak_Fp=float(d3['Fp_x_c'][i]), peak_T=float(d3['T_x_c'][i]),
                          at1550=dict(Fp=e(d3, 'Fp_x_c'), T=e(d3, 'T_x_c'), eta=e(d3, 'T_x_c') / e(d3, 'Fp_x_c'), na13=e(d3, 'f_zNA13_x_c'),
                                      na09=e(d3, 'f_zNA09_x_c'), ratio=e(d3, 'f_py60_x_c') / e(d3, 'f_my60_x_c'), ImG=e(d3, 'ImG_x_c'), ReG=e(d3, 'ReG_x_c'),
                                      Fp_h4=e(d4, 'Fp_x_c'), T_h4=e(d4, 'T_x_c')),
                          max_ratio=float(np.max(d3['f_py60_x_c'] / d3['f_my60_x_c'])),
                          max_ratio_lam=float(lam[int(np.argmax(d3['f_py60_x_c'] / d3['f_my60_x_c']))]))


def fit_all(d):
    return {n: gmodes.fit(d, n, EE) for n in (1, 2, 3)}


def fig_nmodes(out):
    d = gmodes.load(STEM); E = d['E']; Ef = np.linspace(E.min(), E.max(), 500); F = fit_all(d)
    fig, ax = plt.subplots(2, 3, figsize=(16, 7.6), gridspec_kw=dict(height_ratios=[3, 1.2]), sharex=True)
    cols = [C['b'], C['g'], C['y']]
    out['nmodes'] = {}
    for k, n in enumerate((1, 2, 3)):
        f = F[n]; a = ax[0, k]
        a.plot(HC / E, d['ImG'], 'o', c=C['k'], ms=4, label='BEM (41 wavelengths)')
        a.plot(HC / Ef, gmodes.model_im(f['p'], Ef, EE), c=C['r'], lw=2.2, label=f'sum of {n} mode(s)')
        for j in range(n):
            pj = f['p'][3 * j:3 * j + 3]
            a.plot(HC / Ef, gmodes.model_im(pj, Ef, EE), ls='--', lw=1.3, c=cols[j], label=f'mode {HC/pj[1]:.0f} nm, Q = {pj[1]/pj[2]:.1f}')
        a.axvline(1550, c='0.5', ls=':'); a.set_ylim(0, 450); a.legend(fontsize=8.8, loc='upper right')
        a.set_title(f'({"abc"[k]}) {n} mode(s): rms rel. error {100*f["rms_im"]:.1f} %', fontsize=12)
        if k == 0: a.set_ylabel('Im G (normalised)')
        r = (gmodes.model_im(f['p'], E, EE) - d['ImG']) / d['ImG']
        ax[1, k].plot(HC / E, 100 * r, 'o-', c=C['r'], ms=3, lw=1); ax[1, k].axhline(0, c='0.4', lw=0.8)
        ax[1, k].set_ylim(-40, 40); ax[1, k].set_xlabel('wavelength (nm)')
        if k == 0: ax[1, k].set_ylabel('residual (%)')
        ImG_e = float(gmodes.model_im(f['p'], np.array([EE]), EE)[0])
        out['nmodes'][n] = dict(rms=f['rms_im'], max_abs_res=float(np.max(np.abs(r))), ImG_1550=ImG_e,
                                modes=[dict(lam=HC / m['E'], kappa_meV=1e3 * m['kappa'], Q=m['E'] / m['kappa'], A=m['A'], g_meV=1e3 * m['g'])
                                       for m in gmodes.couplings(f)])
    out['ImG_1550_bem'] = gmodes.at(d, 'ImG')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_d3_nmodes.png')); plt.close(fig)


def fig_origin(out):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6), sharey=True)
    out['origin'] = {}
    for k, (s, tl) in enumerate((('L270', '(a) dimer alone, L = 270 nm'), ('L280', '(b) dimer alone, L = 280 nm'), (STEM, '(c) final design: dimer L = 275 + R3'))):
        d = gmodes.load(s); E = d['E']; Ef = np.linspace(E.min(), E.max(), 500); f = gmodes.fit(d, 2, EE); f1 = gmodes.fit(d, 1, EE)
        a = ax[k]; a.plot(HC / E, d['ImG'], 'o', c=C['k'], ms=4, label='BEM')
        a.plot(HC / Ef, gmodes.model_im(f1['p'], Ef, EE), c=C['s'], lw=1.6, ls='-.', label=f'1 mode (error {100*f1["rms_im"]:.1f} %)')
        a.plot(HC / Ef, gmodes.model_im(f['p'], Ef, EE), c=C['r'], lw=2, label=f'2 modes (error {100*f["rms_im"]:.1f} %)')
        for j, c in zip(range(2), (C['b'], C['g'])):
            pj = f['p'][3 * j:3 * j + 3]
            a.plot(HC / Ef, gmodes.model_im(pj, Ef, EE), ls='--', lw=1.2, c=c, label=f'{HC/pj[1]:.0f} nm, Q {pj[1]/pj[2]:.1f}, A {pj[0]:.0f}')
        a.axvline(1550, c='0.5', ls=':'); a.set_title(tl, fontsize=12); a.set_xlabel('wavelength (nm)'); a.legend(fontsize=8.8)
        out['origin'][s] = dict(rms1=f1['rms_im'], rms2=f['rms_im'], modes=[dict(lam=HC / m['E'], Q=m['E'] / m['kappa'], A=m['A']) for m in f['modes']])
    ax[0].set_ylabel('Im G (normalised)'); ax[0].set_ylim(0, 450)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_d4_origin.png')); plt.close(fig)


def fig_position(out):
    b, _ = tri2.series(STEM); E0 = HC / b['lambda_nm']; o = np.argsort(E0)
    fig, ax = plt.subplots(1, 2, figsize=(14, 4.6))
    out['position'] = {}
    labs = {'c': 'gap centre', 'px5': '5 nm towards R2 (x)', 'py10': '10 nm towards R3 (y)'}
    for (pos, c) in (('c', C['r']), ('px5', C['b']), ('py10', C['g'])):
        d = dict(E=E0[o], ImG=np.asarray(b[f'ImG_x_{pos}'])[o], ReG=np.asarray(b[f'ReG_x_{pos}'])[o])
        f = gmodes.fit(d, 2, EE); cp = gmodes.couplings(f)
        ax[0].plot(HC / d['E'], d['ImG'], 'o', c=c, ms=3.5)
        Ef = np.linspace(d['E'].min(), d['E'].max(), 400)
        ax[0].plot(HC / Ef, gmodes.model_im(f['p'], Ef, EE), c=c, lw=1.8, label=f'{labs[pos]} (fit error {100*f["rms_im"]:.1f} %)')
        out['position'][pos] = dict(rms=f['rms_im'], ImG_1550=float(np.interp(EE, d['E'], d['ImG'])),
                                    modes=[dict(lam=HC / m['E'], Q=m['E'] / m['kappa'], g_meV=1e3 * m['g']) for m in cp])
    ax[0].axvline(1550, c='0.5', ls=':'); ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('Im G (normalised)'); ax[0].legend(fontsize=9)
    ax[0].set_title('(a) Im G for three emitter positions (dots BEM, lines 2 modes)', fontsize=12)
    xs = np.arange(3); w = 0.36
    for j, (c, nm) in enumerate(((C['b'], 'sharp mode (1440 nm)'), (C['g'], 'broad mode (~1510 nm)'))):
        vals = [sorted(out['position'][p]['modes'], key=lambda m: -m['Q'])[j]['g_meV'] for p in ('c', 'px5', 'py10')]
        ax[1].bar(xs + (j - 0.5) * w, vals, w, color=c, label=nm)
        for x, v in zip(xs + (j - 0.5) * w, vals): ax[1].text(x, v + 0.03, f'{v:.2f}', ha='center', fontsize=9.5)
    ax[1].set_xticks(xs); ax[1].set_xticklabels([labs[p] for p in ('c', 'px5', 'py10')]); ax[1].set_ylabel(r'ħg (meV), $\tau_0$ = 2 ns')
    ax[1].set_title('(b) coupling to each mode', fontsize=12); ax[1].legend(fontsize=9.5); ax[1].grid(axis='x')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_d5_position.png')); plt.close(fig)


def main():
    out = {}
    fig_geometry(); fig_spectra(out); fig_nmodes(out); fig_origin(out); fig_position(out)
    json.dump(out, open(os.path.join(ROOT, 'results', 'modes_detail.json'), 'w'), indent=1, default=float)
    print(json.dumps(out, indent=1, default=lambda x: round(float(x), 4)))


if __name__ == '__main__':
    main()
