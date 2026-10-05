"""Analysis of the additional MNPBEM studies (isi/bem/extra, workflow bem-extra.yml).
  modes      : quasistatic plasmon-mode decomposition -> resonant vs background (geometric) anisotropy
  offset     : tolerance to the emitter position on a spacer shell around the tip
  shapes     : other diameters, silver, prolate spheroid
  excitation : local-field enhancement at the emitter positions (rod vs equal-volume sphere)
  substrate  : rod lying on glass
  nonlocal   : hydrodynamic correction (Luo et al. cover layer)
  emitters   : design table for real emitters, from the aspect-ratio sweep (isi/results/bem_raw)
usage: python isi/analysis/ingest_extra.py [extra_dir] [raw_dir]   (run from repo root)"""
import sys, os, re, glob
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

EX = sys.argv[1] if len(sys.argv) > 1 else 'isi/results/bem_extra'
RAW = sys.argv[2] if len(sys.argv) > 2 else 'isi/results/bem_raw'
FIG = 'isi/figures'; OUT = 'isi/results/bem_extra_summary.md'
C = ['#1f4e9c', '#c0392b', '#2a9d5c', '#8a5a00', '#7b3fa0', '#5f6b73']   # same fixed order as make_figures*.py
plt.rcParams.update({'font.family': 'serif', 'font.size': 8, 'axes.linewidth': 0.8, 'lines.linewidth': 1.4,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'figure.dpi': 150})


def load(path):
    if not os.path.exists(path): return None
    L = open(path).read().splitlines()
    i = 0
    while L[i].startswith('#'): i += 1
    hdr = L[i].split(',')
    d = np.loadtxt(path, delimiter=',', skiprows=i + 1, ndmin=2)
    return {k: d[:, j] for j, k in enumerate(hdr)}


def eta(T, F, q0):
    return T / (F + (1 - q0) / q0)


lines = ['# Additional BEM studies', '']

# ------------------------------------------------------------------ modes
specs = [s for s in ['rodL40', 'rodL60', 'rodL80', 'rodL100', 'sphere'] if os.path.exists(f'{EX}/modes_{s}.csv')]
if specs:
    lines += ['## Plasmon-mode decomposition (quasistatic)', '',
              'At the peak of the axial Fp: share of Fp-1 carried by the longitudinal dipolar mode; background = full - mode;',
              'geometric ratio = background_axial / Fp_transverse; total ratio = Fp_axial / Fp_transverse.', '',
              '| particle | gap | lambda_peak | Fp_z | mode share | background_z | Fp_x | geometric ratio | total ratio |',
              '|---|---|---|---|---|---|---|---|---|']
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5))
    share = {}
    for ci, s in enumerate(specs):
        d = load(f'{EX}/modes_{s}.csv')
        rows = []
        for g in sorted(set(d['gap'])):
            m = d['gap'] == g
            lam, Fz, Fx, dL = d['lambda_nm'][m], d['Fp_z'][m], d['Fp_x'][m], d['dFz_L'][m]
            # peak of the mode term = resonance (the full Fp can peak at the interband edge for tiny gaps)
            i = np.argmax(dL)
            bg = Fz[i] - dL[i]
            rows.append((g, lam[i], Fz[i], dL[i] / (Fz[i] - 1), bg, Fx[i], bg / Fx[i], Fz[i] / Fx[i]))
            if g in (3, 5, 10, 20):
                lines.append(f'| {s} | {g:g} | {lam[i]:.0f} | {Fz[i]:.0f} | {100*dL[i]/(Fz[i]-1):.0f}% | {bg:.1f} | {Fx[i]:.1f} | {bg/Fx[i]:.2f} | {Fz[i]/Fx[i]:.0f} |')
            if s == 'rodL60' and g == 5:
                ax[0].plot(lam, Fz, color=C[0], label='axial, full')
                ax[0].plot(lam, dL, color=C[1], ls='--', label='longitudinal mode')
                ax[0].plot(lam, Fz - dL, color=C[2], label='axial, background')
                ax[0].plot(lam, Fx, color=C[3], label='transverse')
        r = np.array(rows); share[s] = r
        lab = 'sphere' if s == 'sphere' else f'L = {s[4:]} nm'
        ax[1].plot(r[:, 0], 100 * r[:, 3], 'o-', ms=3, color=C[ci], label=lab)
        ax[2].plot(r[:, 0], r[:, 7], 'o-', ms=3, color=C[ci], label=lab)
        ax[2].plot(r[:, 0], r[:, 6], ':', color=C[ci])
    ax[0].set_yscale('log'); ax[0].set_xlabel('Wavelength (nm)'); ax[0].set_ylabel(r'$F_p$ (5 nm gap)')
    ax[0].legend(fontsize=6, loc='lower left')
    ax[1].set_xlabel('Gap (nm)'); ax[1].set_ylabel('Dipolar-mode share (%)'); ax[1].legend(fontsize=6, loc='center right', bbox_to_anchor=(1.0, 0.42))
    ax[2].set_xlabel('Gap (nm)'); ax[2].set_ylabel('Axial / transverse $F_p$'); ax[2].set_yscale('log')
    for a, t in zip(ax, 'abc'): a.text(-0.02, 1.04, f'({t})', transform=a.transAxes, fontweight='bold')
    fig.tight_layout(w_pad=1.5); fig.savefig(f'{FIG}/fig_modes.pdf'); plt.close(fig)
    # gap at which the dipolar mode carries half of Fp-1
    for s, r in share.items():
        sh = r[:, 3]
        if sh.min() < 0.5 < sh.max():
            k = np.where(np.diff(np.sign(sh - 0.5)))[0][0]
            g50 = np.interp(0.5, sh[k:k + 2], r[k:k + 2, 0])
            lines.append(f'- {s}: dipolar mode carries half of Fp-1 at a gap of {g50:.1f} nm; total ratio max {r[:,7].max():.0f} at {r[np.argmax(r[:,7]),0]:g} nm')
    for s in specs:
        info = open(f'{EX}/modes_info_{s}.csv').read().splitlines()[0]
        lines.append(f'- {s}: {info.lstrip("# ")}')

# ------------------------------------------------------------------ offset
off = {s: load(f'{EX}/offset_s{s}.csv') for s in (5, 10)}
if any(v is not None for v in off.values()):
    lines += ['', '## Emitter position on a spacer shell around the tip (rod L60)', '',
              '| shell s | theta | lateral offset (nm) | Fp_n | T_n | eta_n | Fp_t | T_t | T_y |', '|---|---|---|---|---|---|---|---|---|']
    fig, ax = plt.subplots(1, 2, figsize=(4.8, 2.2))
    for ci, (s, d) in enumerate(off.items()):
        if d is None: continue
        th = sorted({int(re.search(r'th(\d+)', k).group(1)) for k in d if k.startswith('Fp_n_th')})
        j = np.argmax(d['T_n_th0'])
        lr = d['lambda_nm'][j]
        Tn = np.array([d[f'T_n_th{t}'][j] for t in th]); Fn = np.array([d[f'Fp_n_th{t}'][j] for t in th])
        for t in th:
            x = (10 + s) * np.sin(np.radians(t))
            lines.append(f'| {s} | {t} | {x:.1f} | {d[f"Fp_n_th{t}"][j]:.0f} | {d[f"T_n_th{t}"][j]:.1f} | {100*d[f"T_n_th{t}"][j]/d[f"Fp_n_th{t}"][j]:.1f}% | '
                         f'{d[f"Fp_t_th{t}"][j]:.0f} | {d[f"T_t_th{t}"][j]:.2f} | {d[f"T_y_th{t}"][j]:.2f} |')
        rr = Tn / Tn[0]
        if rr.min() < 0.5:
            half = np.interp(0.5, rr[::-1], np.array(th)[::-1])
            lines.append(f'- s = {s} nm (lambda {lr:.0f} nm): T_n falls to half at theta = {half:.0f} deg, i.e. lateral offset {(10+s)*np.sin(np.radians(half)):.1f} nm')
        else:
            lines.append(f'- s = {s} nm (lambda {lr:.0f} nm): T_n stays above half over the whole cap; at theta = {th[-1]} deg it is {100*rr[-1]:.0f}% of the on-axis value, eta {100*Tn[-1]/Fn[-1]:.1f}% vs {100*Tn[0]/Fn[0]:.1f}%')
        ax[0].plot(th, Tn / Tn[0], 'o-', ms=3, color=C[ci], label=f'spacer {s} nm')
        ax[1].plot(th, 100 * Tn / Fn, 'o-', ms=3, color=C[ci], label=f'spacer {s} nm')
    ax[0].set_xlabel(r'Polar angle $\theta$ (deg)'); ax[0].set_ylabel(r'$T_n(\theta)/T_n(0)$'); ax[0].legend(fontsize=6, frameon=False)
    ax[1].set_xlabel(r'Polar angle $\theta$ (deg)'); ax[1].set_ylabel(r'$\eta_a$ (%)')
    for a, t in zip(ax, 'ab'): a.text(0.03, 0.93, f'({t})', transform=a.transAxes, fontweight='bold')
    fig.tight_layout(); fig.savefig(f'{FIG}/fig_offset.pdf'); plt.close(fig)

# ------------------------------------------------------------------ shapes
shp = sorted(glob.glob(f'{EX}/shape_*.csv'))
if shp:
    lines += ['', '## Other shapes and metals (axial / transverse dipole)', '',
              '| case | gap | lambda_T | T_z max | Fp_z there | eta_a | Fp_z/Fp_x there | T_z/T_x there | Fp_z/Fp_x at 500 nm |', '|---|---|---|---|---|---|---|---|---|']
    for f in shp:
        d = load(f); name = os.path.basename(f)[6:-4]
        for g in (5, 10):
            if f'T_z_g{g}' not in d: continue
            j = np.argmax(d[f'T_z_g{g}']); k = np.argmin(abs(d['lambda_nm'] - 500))
            lines.append(f'| {name} | {g} | {d["lambda_nm"][j]:.0f} | {d[f"T_z_g{g}"][j]:.1f} | {d[f"Fp_z_g{g}"][j]:.0f} | '
                         f'{100*d[f"T_z_g{g}"][j]/d[f"Fp_z_g{g}"][j]:.1f}% | {d[f"Fp_z_g{g}"][j]/d[f"Fp_x_g{g}"][j]:.0f} | '
                         f'{d[f"T_z_g{g}"][j]/d[f"T_x_g{g}"][j]:.0f} | {d[f"Fp_z_g{g}"][k]/d[f"Fp_x_g{g}"][k]:.2f} |')

# ------------------------------------------------------------------ excitation
exc = {s: load(f'{EX}/excitation_{s}.csv') for s in ('rod', 'sphere')}
if any(v is not None for v in exc.values()):
    lines += ['', '## Excitation (local-field intensity) enhancement on the axis', '',
              '| particle | gap | max |E_z|^2 (pol. axial) | at lambda | 405 nm | 450 nm | 532 nm | 633 nm |', '|---|---|---|---|---|---|---|---|---|']
    fig, ax = plt.subplots(1, 1, figsize=(3.3, 2.3))
    for ci, (s, d) in enumerate(exc.items()):
        if d is None: continue
        for g in (5, 10, 20):
            y = d[f'Ez2_polz_g{g}']; j = np.argmax(y)
            at = [np.interp(w, d['lambda_nm'], y) for w in (405, 450, 532, 633)]
            lines.append(f'| {s} | {g} | {y[j]:.0f} | {d["lambda_nm"][j]:.0f} | ' + ' | '.join(f'{v:.1f}' for v in at) + ' |')
        ax.plot(d['lambda_nm'], d['Ez2_polz_g5'], color=C[ci], label=f'{s}, 5 nm')
        ax.plot(d['lambda_nm'], d['Ez2_polz_g10'], color=C[ci], ls='--', label=f'{s}, 10 nm')
    ax.set_yscale('log'); ax.set_xlabel('Wavelength (nm)'); ax.set_ylabel(r'$|E_z|^2/|E_0|^2$'); ax.legend(fontsize=6, frameon=False)
    fig.tight_layout(); fig.savefig(f'{FIG}/fig_excitation.pdf'); plt.close(fig)

# ------------------------------------------------------------------ substrate
d = load(f'{EX}/substrate_glass.csv')
if d is not None:
    lines += ['', '## Rod on glass (n = 1.52), axial dipole x; rates in units of the vacuum rate', '',
              '| gap | lambda_T | T_x | Fp_x | eta_a | T_x / T0_x (vs bare glass) | Fp_x / tot0_x | T_y max | T_z max |', '|---|---|---|---|---|---|---|---|---|']
    for g in (5, 10, 20):
        j = np.argmax(d[f'rad_x_g{g}'])
        lines.append(f'| {g} | {d["lambda_nm"][j]:.0f} | {d[f"rad_x_g{g}"][j]:.1f} | {d[f"tot_x_g{g}"][j]:.0f} | '
                     f'{100*d[f"rad_x_g{g}"][j]/d[f"tot_x_g{g}"][j]:.1f}% | {d[f"rad_x_g{g}"][j]/d[f"rad0_x_g{g}"][j]:.1f} | '
                     f'{d[f"tot_x_g{g}"][j]/d[f"tot0_x_g{g}"][j]:.0f} | {d[f"rad_y_g{g}"].max():.2f} | {d[f"rad_z_g{g}"].max():.2f} |')

# ------------------------------------------------------------------ nonlocal
a, b = load(f'{EX}/nonlocal_local.csv'), load(f'{EX}/nonlocal_nonlocal.csv')
if a is not None and b is not None:
    lines += ['', '## Nonlocal correction (hydrodynamic, cover-layer model)', '',
              '| gap | Fp_z peak local | nonlocal | change | lambda shift | T_z peak local | nonlocal | change |', '|---|---|---|---|---|---|---|---|']
    for g in (3, 5, 10):
        i, k = np.argmax(a[f'Fp_z_g{g}']), np.argmax(b[f'Fp_z_g{g}'])
        i2, k2 = np.argmax(a[f'T_z_g{g}']), np.argmax(b[f'T_z_g{g}'])
        lines.append(f'| {g} | {a[f"Fp_z_g{g}"][i]:.0f} | {b[f"Fp_z_g{g}"][k]:.0f} | {100*(b[f"Fp_z_g{g}"][k]/a[f"Fp_z_g{g}"][i]-1):+.1f}% | '
                     f'{b["lambda_nm"][k]-a["lambda_nm"][i]:+.0f} nm | {a[f"T_z_g{g}"][i2]:.1f} | {b[f"T_z_g{g}"][k2]:.1f} | {100*(b[f"T_z_g{g}"][k2]/a[f"T_z_g{g}"][i2]-1):+.1f}% |')

# ------------------------------------------------------------------ emitters
EMIT = [  # name, emission peak (nm), intrinsic quantum yield, source
    ('hBN defect', 580, 0.87, 'Nikolay et al., Optica 6, 1084 (2019)'),
    ('crystal violet', 640, 0.02, 'Khatua et al., ACS Nano 8, 4440 (2014)'),
    ('NV, 25 nm nanodiamond', 690, 0.10, 'Mohtashami & Koenderink, NJP 15, 043017 (2013)'),
    ('NV, 100 nm nanodiamond', 690, 0.70, 'Mohtashami & Koenderink, NJP 15, 043017 (2013)'),
    ('CsPbI3 nanocrystal', 690, 0.90, 'Protesescu et al., Nano Lett. 15, 3692 (2015)'),
]
rods = {}
for f in glob.glob(f'{RAW}/rod_L*_h2_air.csv'):
    rods[int(re.search(r'rod_L(\d+)_', f).group(1))] = load(f)
if rods:
    lines += ['', '## Design table for real emitters (axial dipole, rod D = 20 nm in air, resonance-matched length)', '',
              '| emitter | lambda_e | q0 | best L (nm) | gap | T (saturated brightness) | Fp | rate speed-up | eta(q0) | eta/q0 |',
              '|---|---|---|---|---|---|---|---|---|---|']
    for name, le, q0, src in EMIT:
        best = None
        for L, d in rods.items():
            T5 = np.interp(le, d['lambda_nm'], d['T_z_g5'])
            if best is None or T5 > best[1]: best = (L, T5)
        L = best[0]; d = rods[L]
        for g in (5, 10, 20):
            T = np.interp(le, d['lambda_nm'], d[f'T_z_g{g}']); F = np.interp(le, d['lambda_nm'], d[f'Fp_z_g{g}'])
            e = eta(T, F, q0)
            lines.append(f'| {name} | {le} | {q0} | {L} | {g} | {T:.1f} | {F:.0f} | {q0*F+1-q0:.0f} | {100*e:.1f}% | {e/q0:.2f} |')
    lines += ['', 'Sources: ' + '; '.join(sorted({e[3] for e in EMIT}))]

# ------------------------------------------------------------------ collection efficiency (BEM far field)
def bare_dipole_fraction(alpha, axial):
    """Fraction of a bare dipole's power inside a cone of half-angle alpha; axial: dipole along the cone axis."""
    th = np.linspace(0, alpha, 4001); ph = np.linspace(0, 2 * np.pi, 721)
    T, P = np.meshgrid(th, ph, indexing='ij')
    I = np.sin(T)**2 if axial else 1 - (np.sin(T) * np.cos(P))**2
    num = np.trapezoid(np.trapezoid(I * np.sin(T), ph, axis=1), th)
    return num / (8 * np.pi / 3)
cf, cg = load(f'{EX}/collection_free.csv'), load(f'{EX}/collection_glass.csv')
if cf is not None:
    lines += ['', '## Collection efficiency (BEM far field), rod in air, at the radiative peak', '',
              '| dipole | gap | lambda | rod along optical axis NA0.5 | NA0.9 | rod in focal plane NA0.5 | NA0.9 | bare dipole (axis/plane) NA0.9 |', '|---|---|---|---|---|---|---|---|']
    for dn in ('z', 'x'):
        for g in (5, 10, 20):
            j = np.argmax(cf[f'Prad_{dn}_g{g}'])
            lines.append(f'| {dn} | {g} | {cf["lambda_nm"][j]:.0f} | {100*cf[f"f_up_NA0.5_{dn}_g{g}"][j]:.1f}% | {100*cf[f"f_up_NA0.9_{dn}_g{g}"][j]:.1f}% | '
                         f'{100*cf[f"f_side_NA0.5_{dn}_g{g}"][j]:.1f}% | {100*cf[f"f_side_NA0.9_{dn}_g{g}"][j]:.1f}% | '
                         f'{100*bare_dipole_fraction(np.arcsin(0.9), True):.1f}% / {100*bare_dipole_fraction(np.arcsin(0.9), False):.1f}% |')
if cg is not None:
    lines += ['', '## Collection efficiency, rod on glass (axis x), at the radiative peak of the axial dipole', '',
              '| dipole | gap | lambda | into glass (total) | oil NA1.3 | oil NA1.45 | air hemisphere | dry NA0.9 from top |', '|---|---|---|---|---|---|---|---|']
    for dn in ('x', 'y', 'z'):
        for g in (5, 10, 20):
            j = np.argmax(cg[f'Prad_x_g{g}'])
            lines.append(f'| {dn} | {g} | {cg["lambda_nm"][j]:.0f} | {100*cg[f"f_glass_hemisphere_{dn}_g{g}"][j]:.1f}% | {100*cg[f"f_glass_NA1.3_{dn}_g{g}"][j]:.1f}% | '
                         f'{100*cg[f"f_glass_NA1.45_{dn}_g{g}"][j]:.1f}% | {100*cg[f"f_air_hemisphere_{dn}_g{g}"][j]:.1f}% | {100*cg[f"f_air_NA0.9_{dn}_g{g}"][j]:.1f}% |')

# ------------------------------------------------------------------ comparison with Khatua et al. (2014)
kh = sorted(glob.glob(f'{EX}/khatua_L*.csv'), key=lambda f: int(re.search(r'_L(\d+)', f).group(1)))
if kh:
    q0 = 0.0228; lines += ['', '## Comparison with Khatua et al., ACS Nano 8, 4440 (2014): crystal violet, D = 25 nm rods in n = 1.47', '',
        'xi = E_exc(laser) x E_em; E_em = <eta(q0)>/q0 averaged over a Gaussian CV emission band (640 nm, FWHM 60 nm); speed-up = <q0 Fp + 1 - q0>', '',
        '| L (nm) | SPR (nm) | gap | E_exc 594 | E_exc 633 | E_em | xi(594) | xi(633) | speed-up |', '|---|---|---|---|---|---|---|---|---|']
    KH = []
    for f in kh:
        d = load(f); L = int(re.search(r'_L(\d+)', f).group(1))
        meta = open(f).readline()
        e594 = [float(x) for x in re.search(r'594 nm: ([\d.e+\- ]+);', meta).group(1).split()]
        e633 = [float(x) for x in re.search(r'633 nm: ([\d.e+\- ]+)', meta).group(1).split()]
        spr = d['lambda_nm'][np.argmax(d['ext_nm2'])]
        w = np.exp(-0.5 * ((d['lambda_nm'] - 640) / (60 / 2.355))**2); w /= w.sum()
        for gi, g in enumerate((3, 5, 7, 10)):
            F, T = d[f'Fp_g{g}'], d[f'T_g{g}']
            Eem = np.sum(w * T / (F + (1 - q0) / q0)) / q0
            sp = np.sum(w * (q0 * F + 1 - q0))
            KH.append((L, spr, g, e594[gi], e633[gi], Eem, e594[gi] * Eem, e633[gi] * Eem, sp))
            if g in (5, 3):
                lines.append(f'| {L} | {spr:.0f} | {g} | {e594[gi]:.0f} | {e633[gi]:.0f} | {Eem:.1f} | {e594[gi]*Eem:.0f} | {e633[gi]*Eem:.0f} | {sp:.1f} |')
    K = np.array(KH)
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    for g, mk in ((3, 's'), (5, 'o'), (10, '^')):
        m = K[:, 2] == g
        ax.semilogy(K[m, 1], K[m, 7], mk + '-', c=C[0], ms=3, lw=1, label=f'633 nm, {g} nm gap')
        ax.semilogy(K[m, 1], K[m, 6], mk + '--', c=C[1], ms=3, lw=1, label=f'594 nm, {g} nm gap')
    ax.axhspan(1000, 1300, color='0.85', zorder=0); ax.text(748, 1600, 'measured maximum, 633 nm (Khatua et al.)', fontsize=6, ha='right'); ax.set_ylim(0.3, 4000)
    ax.set_xlabel('SPR wavelength (nm)'); ax.set_ylabel(r'Fluorescence enhancement $\xi$'); ax.legend(fontsize=5, ncol=2, loc='lower center')
    fig.savefig(f'{FIG}/fig_khatua.pdf'); plt.close(fig)

# ------------------------------------------------------------------ end-cap shape (rod L60 D20)
tips = sorted(glob.glob(f'{EX}/tips_c*.csv'), key=lambda f: -float(re.search(r'tips_c([\d.]+?)\.csv', f).group(1)))
if tips:
    lines += ['', '## Shape of the rod ends (cap semi-axis c = r R), retarded BEM; background from quasistatic modes', '',
              '| r | gap | lambda_T | T_z max | Fp_z there | eta_a | Fp_z/Fp_x max | ratio at 500 nm | quasistatic background ratio | mode share (qs) |',
              '|---|---|---|---|---|---|---|---|---|---|']
    for f in tips:
        r = re.search(r'tips_c([\d.]+?)\.csv', f).group(1); d = load(f)
        mq = load(f'{EX}/modes_tipc{r}.csv')
        for g in (3, 5, 10, 20):
            T, F, Fx = d[f'T_z_g{g}'], d[f'Fp_z_g{g}'], d[f'Fp_x_g{g}']
            j = np.argmax(T); k = np.argmin(abs(d['lambda_nm'] - 500)); rat = F / Fx
            bgs = mf = np.nan
            if mq is not None:
                m = mq['gap'] == g
                if m.any():
                    i = np.argmax(mq['dFz_L'][m]); Fz = mq['Fp_z'][m][i]
                    bgs = (Fz - mq['dFz_L'][m][i]) / mq['Fp_x'][m][i]; mf = mq['dFz_L'][m][i] / (Fz - 1)
            lines.append(f'| {r} | {g} | {d["lambda_nm"][j]:.0f} | {T[j]:.1f} | {F[j]:.0f} | {100*T[j]/F[j]:.1f}% | {rat.max():.0f} | {rat[k]:.2f} | {bgs:.2f} | {100*mf:.0f}% |')

open(OUT, 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
