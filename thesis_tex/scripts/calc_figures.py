"""Recompute the worked examples of chapter 5 and draw the thesis figures.

BBO: Sellmeier formula of Eimerl et al., J. Appl. Phys. 62, 1968 (1987), lambda in micrometres.
MgO:LiNbO3 (5 mol% MgO, congruent): Gayer et al., Appl. Phys. B 91, 343 (2008), extraordinary index.
MRR chart: values of table 5-6 (200-question evaluation of the live site, 26 Oct 2026).

Run:  python3 calc_figures.py
It prints every number used in sections 5-5-1 and 5-5-2 and writes the PNG figures next to main.tex.
"""
import os
import numpy as np

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


# ---------------------------------------------------------------- dispersion formulas
def bbo(lam):
    l2 = lam ** 2
    no = np.sqrt(2.7359 + 0.01878 / (l2 - 0.01822) - 0.01354 * l2)
    ne = np.sqrt(2.3753 + 0.01224 / (l2 - 0.01667) - 0.01516 * l2)
    return no, ne


def ne_theta(theta, no, ne):
    return 1.0 / np.sqrt(np.cos(theta) ** 2 / no ** 2 + np.sin(theta) ** 2 / ne ** 2)


def ln_e(lam, T):
    """Extraordinary index of 5% MgO congruent LiNbO3 (Gayer 2008)."""
    a1, a2, a3, a4, a5, a6 = 5.756, 0.0983, 0.2020, 189.32, 12.52, 1.32e-2
    b1, b2, b3, b4 = 2.860e-6, 4.700e-8, 6.113e-8, 1.516e-4
    f = (T - 24.5) * (T + 570.82)
    l2 = lam ** 2
    n2 = a1 + b1 * f + (a2 + b2 * f) / (l2 - (a3 + b3 * f) ** 2) + (a4 + b4 * f) / (l2 - a5 ** 2) - a6 * l2
    return np.sqrt(n2)


# ---------------------------------------------------------------- BBO type-I SHG at 1.064 um
lw, l2w = 1.064, 0.532
no_w, ne_w = bbo(lw)
no_2w, ne_2w = bbo(l2w)
s2 = (no_w ** -2 - no_2w ** -2) / (ne_2w ** -2 - no_2w ** -2)
th = np.arcsin(np.sqrt(s2))


def dk(theta):
    return 2 * np.pi / l2w * (ne_theta(theta, no_2w, ne_2w) - no_w)   # rad/um


dk0 = 2 * np.pi / l2w * (no_2w - no_w)
Lc = np.pi / abs(dk0)
rho = np.arctan((no_2w / ne_2w) ** 2 * np.tan(th)) - th
h = 1e-6
ddk = (dk(th + h) - dk(th - h)) / (2 * h)                              # rad/um per rad
acc = 2 * 2.78 / abs(ddk) * 1e-4 * 1e3                                 # (rad*um) -> mrad*cm
d22, d31 = 2.2, 0.1
deff_main = d22 * np.cos(th)
deff_small = d31 * np.sin(th)

print("BBO  no(1.064)=%.5f  no(0.532)=%.5f  ne(0.532)=%.5f" % (no_w, no_2w, ne_2w))
print("BBO  theta_pm=%.2f deg" % np.degrees(th))
print("BBO  dk(theta=0)=%.3f 1/um   Lc=%.1f um" % (dk0, Lc))
print("BBO  walk-off rho=%.2f deg = %.1f mrad; separation for 100 um beam = %.2f mm"
      % (np.degrees(rho), rho * 1e3, 0.1 / np.tan(rho)))
print("BBO  |d dk/d theta|=%.2f 1/(um rad)  acceptance=%.2f mrad cm" % (abs(ddk), acc))
print("BBO  d22 cos(theta)=%.2f pm/V   d31 sin(theta)=%.2f pm/V" % (deff_main, deff_small))

# ---------------------------------------------------------------- PPLN first-order QPM period
for T in (25.0, 100.0):
    n1, n2 = ln_e(lw, T), ln_e(l2w, T)
    print("PPLN T=%5.1f C  ne(1.064)=%.5f ne(0.532)=%.5f  Lambda=%.2f um"
          % (T, n1, n2, lw / (2 * (n2 - n1))))
print("PPLN deff=(2/pi)*25.0=%.1f pm/V" % (2 / np.pi * 25.0))

# ---------------------------------------------------------------- figures
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit("matplotlib not installed: numbers printed, figures skipped")

plt.rcParams.update({"font.size": 12, "axes.grid": True, "grid.alpha": 0.3,
                     "savefig.dpi": 200, "savefig.bbox": "tight"})

# 1. BBO dispersion
lam = np.linspace(0.40, 2.00, 400)
no, ne = bbo(lam)
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(lam, no, color="#1f5aa6", lw=2, label=r"$n_o$")
ax.plot(lam, ne, color="#c0392b", lw=2, ls="--", label=r"$n_e$")
for x in (l2w, lw):
    ax.axvline(x, color="gray", lw=0.8, ls=":")
ax.set_xlabel(r"wavelength $\lambda$ ($\mu$m)")
ax.set_ylabel("refractive index")
ax.legend()
fig.savefig(os.path.join(OUT, "fig_bbo_dispersion.png"))
plt.close(fig)

# 2. angular tuning curve, L = 1 cm
L = 1e4  # um
dth = np.linspace(-1.5e-3, 1.5e-3, 801)
x = dk(th + dth) * L / 2
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(dth * 1e3, np.sinc(x / np.pi) ** 2, color="#1f5aa6", lw=2)
ax.axhline(0.5, color="gray", lw=0.8, ls=":")
ax.set_xlabel(r"$\theta-\theta_{pm}$ (mrad)")
ax.set_ylabel(r"normalised SHG power  sinc$^2(\Delta k L/2)$")
fig.savefig(os.path.join(OUT, "fig_bbo_acceptance.png"))
plt.close(fig)

# 3. PPLN period versus temperature
T = np.linspace(20, 200, 200)
Lam = lw / (2 * (ln_e(l2w, T) - ln_e(lw, T)))
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(T, Lam, color="#1f5aa6", lw=2)
ax.set_xlabel(r"temperature ($^\circ$C)")
ax.set_ylabel(r"QPM period $\Lambda$ ($\mu$m)")
fig.savefig(os.path.join(OUT, "fig_ppln_period.png"))
plt.close(fig)

# 4. MRR@10 per question group (table 5-6)
groups = ["gen (76)", "ri (110)", "dij (7)", "thermo (4)", "paper (3)", "all (200)"]
hyb = [0.754, 0.374, 0.386, 0.375, 0.333, 0.518]
sub = [0.781, 0.481, 0.482, 0.271, 0.417, 0.590]
xx = np.arange(len(groups))
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.bar(xx - 0.2, hyb, 0.4, color="#9db7d9", label="hybrid search")
ax.bar(xx + 0.2, sub, 0.4, color="#1f5aa6", label="with SubQ re-ranking")
for i in range(len(xx)):
    ax.text(xx[i] - 0.2, hyb[i] + 0.01, "%.3f" % hyb[i], ha="center", fontsize=8)
    ax.text(xx[i] + 0.2, sub[i] + 0.01, "%.3f" % sub[i], ha="center", fontsize=8)
ax.set_xticks(xx)
ax.set_xticklabels(groups)
ax.set_ylabel("MRR@10")
ax.set_ylim(0, 0.9)
ax.grid(axis="x")
ax.legend()
fig.savefig(os.path.join(OUT, "fig_mrr_groups.png"))
plt.close(fig)
print("figures written to", OUT)
