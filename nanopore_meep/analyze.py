"""Figures and summary numbers from runs/*.npz. Usage: python analyze.py"""
import glob
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import distance_transform_edt

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("figures", exist_ok=True)
L785 = 0.785
summary = {}


def load(name):
    f = f"runs/{name}.npz"
    return np.load(f) if os.path.exists(f) and os.path.getsize(f) else None   # 0-byte = skipped run


def ref_name(name, res):
    """Incident-field run for a case: fit_* cases use the Gaussian-beam reference fit_empty_r*."""
    return f"{'fit_' if name.startswith('fit_') else ''}empty_r{res}"


def I0_cyl(res, name=""):
    e = load(ref_name(name, res))
    return np.abs(e["Er"]).mean(axis=(1, 2)) ** 2      # |E_inc|^2 per wavelength


def hotspot(d, I0, dmin_nm=0.0):
    """Max |E|^2/|E0|^2 in water (phi = 0 plane) per wavelength, optionally >= dmin_nm from gold."""
    water = d["eps"] == 0                           # labels: 0 water, 1 gold, 2 SiN
    h = (d["rs"][1] - d["rs"][0]) * 1e3
    dist = distance_transform_edt(d["eps"] != 1, sampling=h)   # nm to the nearest gold pixel
    mask = water & (dist >= dmin_nm)
    I = (np.abs(d["Er"]) ** 2 + np.abs(d["Ez"]) ** 2) / I0[:, None, None]
    return np.where(mask[None], I, 0).max(axis=(1, 2)), I


# ---------- bowl / conventional pores: every case found in runs/ ----------
SPECTRA = {"fit_bowl_R10_h3_r1000": ("bowl R = 10, h3 = 3, rounded, Gaussian", "k-"),"rf_bowl_R10_r1000": ("bowl R = 10, h3 = 5", "C0-"), "rf_bowl_R10_h2.5_r1000": ("bowl R = 10, h3 = 2.5", "C0--"),
           "rf_bowl_R2.5_r1500": ("bowl R = 2.5, h3 = 5", "C2-"), "rf_bowl_R1_r1500": ("bowl R = 1, h3 = 5", "C1-"),
           "rf_conv_R10_r1000": ("conventional R = 10, Au 5", "C3-"), "rf_conv_R2.5_r1500": ("conventional R = 2.5, Au 5", "C4-")}
fig, ax = plt.subplots(figsize=(5.5, 3.8))
for f in sorted(glob.glob("runs/bowl_*.npz") + glob.glob("runs/conv_*.npz") + glob.glob("runs/rf_*.npz")
                + glob.glob("runs/fit_bowl_*.npz") + glob.glob("runs/fit_conv_*.npz")):
    name = os.path.basename(f)[:-4]
    d = load(name)
    res = int(name.rsplit("_r", 1)[1])
    if d is None or load(ref_name(name, res)) is None:
        continue
    I0 = I0_cyl(res, name)
    mx, _ = hotspot(d, I0)
    lam = d["lam"] * 1e3
    i785 = np.argmin(np.abs(lam - 785))
    summary[name] = dict(args=str(d["args"]), grid_nm=round(1e3 / res, 2), lam_res_nm=float(lam[mx.argmax()]),
                         max_at_res=float(mx.max()), max_at_785=float(mx[i785]))
    if name in SPECTRA:
        ax.semilogy(lam, mx, SPECTRA[name][1], label=SPECTRA[name][0])
ax.set_xlabel("wavelength (nm)"); ax.set_ylabel(r"max $|E|^2/|E_0|^2$ in water")
ax.axvline(785, color="0.6", ls=":"); ax.legend(fontsize=7); fig.tight_layout()
fig.savefig("figures/hotspot_spectra.png", dpi=200); plt.close(fig)


# ---------- bowl sweeps: lip thickness h3 and pore radius R (refitted Rakic gold) ----------
def sweep(cases, xs, xlabel, fname):
    pts = [(x, summary[c]) for x, c in zip(xs, cases) if c in summary]
    if len(pts) < 2:
        return
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    x = [p[0] for p in pts]
    ax.plot(x, [p[1]["lam_res_nm"] for p in pts], "o-", color="C0")
    ax.axhline(785, color="0.6", ls=":")
    ax.set_xlabel(xlabel); ax.set_ylabel("resonance wavelength (nm)", color="C0")
    ax2 = ax.twinx()
    ax2.semilogy(x, [p[1]["max_at_785"] for p in pts], "s--", color="C3")
    ax2.set_ylabel(r"max $|E|^2/|E_0|^2$ at 785 nm", color="C3")
    fig.tight_layout(); fig.savefig(f"figures/{fname}", dpi=200); plt.close(fig)


sweep(["rf_bowl_R10_h2.5_r1000", "rf_bowl_R10_r1000", "rf_bowl_R10_h7.5_r1000", "rf_bowl_R10_h10_r1000"],
      [2.5, 5, 7.5, 10], "Au thickness at the pore h3 (nm), R = 10 nm", "bowl_sweep_h3.png")
sweep(["rf_bowl_R1_r1500", "rf_bowl_R2.5_r1500", "rf_bowl_R10_r1000", "rf_bowl_R20_r1000"],
      [1, 2.5, 10, 20], "pore radius R (nm), h3 = 5 nm", "bowl_sweep_R.png")


def side_map(name, res, fname, title):
    d = load(name)
    if d is None:
        return
    i = 0
    I0 = I0_cyl(res, name)[np.argmin(np.abs(d["lam"] - L785))]
    Ixz = (np.abs(d["Erw"]) ** 2 + np.abs(d["Ezw"]) ** 2) / I0        # phi = 0 (along E)
    Iyz = np.abs(d["Epw"]) ** 2 / I0                                   # phi = 90 deg
    r, z = d["rw"] * 1e3, d["zw"] * 1e3
    full = np.concatenate([Iyz[::-1], Ixz], axis=0)                     # y-z | x-z halves
    rr = np.concatenate([-r[::-1], r])
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw=dict(width_ratios=[1.6, 1]))
    for k, (ax, xl, zl) in enumerate(zip(axs, [(-320, 320), (-40, 40)], [(-80, 180), (-15, 30)])):
        m = ax.pcolormesh(rr, z, full.T, norm=LogNorm(0.1, max(full.max(), 10)), cmap="inferno", shading="auto")
        ax.contour(rr, z, (np.concatenate([d["epw"][::-1], d["epw"]]) > 0).T, levels=[0.5], colors="c", linewidths=0.6)
        ax.set_xlim(xl); ax.set_ylim(zl); ax.set_aspect("equal")
        ax.set_xlabel("y (nm)  |  x (nm)  [E along x]"); ax.set_ylabel("z (nm)")
    fig.colorbar(m, ax=axs, label=r"$|E|^2/|E_0|^2$ at 785 nm")
    axs[0].set_title(title, fontsize=9)
    fig.savefig(f"figures/{fname}", dpi=200, bbox_inches="tight"); plt.close(fig)


def top_map(name, res, fname):
    d = load(name)
    if d is None:
        return
    il = np.argmin(np.abs(d["lam"] - L785))
    I0 = I0_cyl(res, name)[il]
    z = d["zs"]; iz = np.argmin(np.abs(z - 0.005 + 0.0005))       # just below the rim plane
    best = None
    for k in range(len(z)):   # plane of the hot spot
        v = (np.abs(d["Er"][il, :, k]) ** 2 + np.abs(d["Ez"][il, :, k]) ** 2).max()
        best = (v, k) if best is None or v > best[0] else best
    iz = best[1]
    r = d["rs"]
    x = np.linspace(-r.max(), r.max(), 401)
    X, Y = np.meshgrid(x, x, indexing="ij")
    R, P = np.hypot(X, Y), np.arctan2(Y, X)
    f = lambda c: np.interp(R, r, np.abs(d[c][il, :, iz]) ** 2)
    I = ((f("Er") + f("Ez")) * np.cos(P) ** 2 + f("Ep") * np.sin(P) ** 2) / I0
    I[R > r.max()] = np.nan
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    m = ax.pcolormesh(x * 1e3, x * 1e3, I.T, cmap="inferno", shading="auto")
    ax.set_aspect("equal"); ax.set_xlabel("x (nm)  [E along x]"); ax.set_ylabel("y (nm)")
    ax.set_title(f"top view, z = {z[iz]*1e3:.1f} nm (hot-spot plane), 785 nm", fontsize=8)
    fig.colorbar(m, label=r"$|E|^2/|E_0|^2$"); fig.tight_layout()
    fig.savefig(f"figures/{fname}", dpi=200); plt.close(fig)


main = next(n for n in ("fit_bowl_R10_h3_r1500", "fit_bowl_R10_h3_r1000", "rf_bowl_R10_r1500", "rf_bowl_R10_r1000", "bowl_R10_jc_r1500", "bowl_R10_jc_r1000")
            if load(n) is not None)                     # finest stable R = 10 nm run available
best = int(main.rsplit("_r", 1)[1])
summary["main_bowl_case"] = main
args = eval(str(load(main)["args"]))   # the run's own argparse namespace, written by bowl_cyl.py
side_map(main, best, "bowl_R10_side.png",
         f"bowl nanopore, R = {args['R']:g} nm, Au {args['h3']:g} nm at the pore"
         + (f", rim rounded {args['round']:g} nm" if args.get("round") else ""))
side_map("conv_R10_r1000", 1000, "conv_R10_side.png", "conventional pore, R = 10 nm, Au 5 nm")
top_map(main, best, "bowl_R10_top.png")

# ---------- hot-spot size at 785 nm (Nano Lett. 2023: ~3 nm hot spot, field drops within 2 nm) ----------
def half_width(x, y):
    """Distance from x[0] at which y (falling from y[0]) first drops below y[0]/2, linearly interpolated."""
    k = np.argmax(y < y[0] / 2)
    if k == 0:
        return float("nan")
    return float(x[k - 1] + (y[k - 1] - y[0] / 2) / (y[k - 1] - y[k]) * (x[k] - x[k - 1]))


def hotspot_size(name):
    """Half-intensity extents of the rim hot spot: radial (into the pore), vertical, azimuthal."""
    res = int(name.rsplit("_r", 1)[1])
    d = load(name)
    il = np.argmin(np.abs(d["lam"] - L785))
    A = np.abs(d["Er"][il]) ** 2 + np.abs(d["Ez"][il]) ** 2          # phi = 0 (plane of E)
    B = np.abs(d["Ep"][il]) ** 2                                      # phi = 90 deg
    water = d["eps"] == 0
    i0, j0 = np.unravel_index(np.where(water, A, 0).argmax(), A.shape)
    r, z = d["rs"] * 1e3, d["zs"] * 1e3
    col = np.arange(i0, -1, -1)
    col = col[: np.argmax(~water[col, j0]) or len(col)]               # stay in the water of the pore
    radial = half_width(r[i0] - r[col], A[col, j0])
    up, dn = np.arange(j0, len(z)), np.arange(j0, -1, -1)
    up = up[: np.argmax(~water[i0, up]) or len(up)]
    dn = dn[: np.argmax(~water[i0, dn]) or len(dn)]
    a, b = A[i0, j0], B[i0, j0]
    zz = np.r_[z[dn][::-1], z[up][1:]]
    prof = np.r_[A[i0, dn][::-1], A[i0, up][1:]] / a
    near = np.abs(zz - z[j0]) <= 8
    vertical = float((prof[near] >= 0.5).sum() * (z[1] - z[0]))     # length of the pore wall above half maximum
    phi = 2 * np.arccos(np.sqrt(max(0.0, (a / 2 - b) / (a - b)))) if a > 2 * b else float("nan")
    return dict(grid_nm=round(1e3 / res, 2), r_nm=float(r[i0]), z_nm=float(z[j0]), radial_half_nm=radial,
                vertical_above_half_nm=vertical,
                at_2nm_from_wall=float(np.interp(2.0, r[i0] - r[col], A[col, j0] / a)), azimuthal_fwhm_deg=float(np.degrees(phi)),
                azimuthal_fwhm_nm=float(phi * r[i0])), (r[i0] - r[col], A[col, j0] / a), \
        (zz - z[j0], prof)


SIZE_CASES = {"fit_bowl_R10_h3_r1500": "R = 10, h3 = 3, rounded", "fit_bowl_R10_h5_r1500": "R = 10, h3 = 5, rounded",
              "rf_bowl_R10_r2000": "R = 10, h3 = 5, sharp (0.5 nm grid)",
              "fit_bowl_R2.5_h3_r1500": "R = 2.5, h3 = 3, rounded", "fit_bowl_R1_h3_r1500": "R = 1, h3 = 3, rounded"}
fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.2))
summary["hotspot_size"] = {}
for k, (name, lab) in enumerate(SIZE_CASES.items()):
    if load(name) is None:
        continue
    sz, (xr, yr), (xz_, yz) = hotspot_size(name)
    summary["hotspot_size"][name] = sz
    if name.startswith("fit_bowl_R10") or name.startswith("rf_"):
        axs[0].plot(xr, yr, f"C{k}.-", ms=3, label=lab)
        axs[1].plot(xz_, yz, f"C{k}.-", ms=3, label=lab)
for ax, xl in zip(axs, ("distance from the Au wall into the pore (nm)", "z - z_hot (nm), along the pore wall")):
    ax.axhline(0.5, color="0.6", ls=":"); ax.set_xlabel(xl); ax.set_ylabel(r"$|E|^2 / |E|^2_{max}$ at 785 nm")
axs[0].set_xlim(0, 10); axs[1].set_xlim(-8, 8); axs[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig("figures/hotspot_profiles.png", dpi=200); plt.close(fig)


# ---------- schematic of the modelled bowl geometry ----------
def schematic(R=10, h3=3, rho=1, h1=100, h2=30, D=250, fname="figures/geometry.png"):
    H = h1 - h3
    u = ((D / 2) ** 2 - R ** 2 - H ** 2) / (2 * H)
    Rs = np.hypot(D / 2, u)
    bowl = lambda r: h1 + u - np.sqrt(Rs ** 2 - r ** 2)
    rc = R + rho
    zt = bowl(rc)
    t = np.linspace(0, np.pi / 2, 20)
    rr = np.linspace(rc, D / 2, 200)
    gold = np.r_[np.c_[rc - rho * np.sin(t), rho - rho * np.cos(t)],                         # lower rounded corner
                 np.c_[[R, R], [rho, zt - rho]],
                 np.c_[rc - rho * np.cos(t), zt - rho + rho * np.sin(t)],                   # upper rounded corner
                 np.c_[rr, bowl(rr)], [[220, h1], [220, 0], [rc, 0]]]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2), gridspec_kw=dict(width_ratios=[2.2, 1]))
    for ax in axs:
        ax.set_facecolor("#d6eaf8")
        for sgn in (1, -1):
            ax.fill(sgn * gold[:, 0], gold[:, 1], color="#e8b730", lw=0)
            ax.fill(sgn * np.array([R, 220, 220, R]), [0, 0, -h2, -h2], color="#9e9e9e", lw=0)
        ax.set_aspect("equal"); ax.set_xlabel("x (nm)"); ax.set_ylabel("z (nm)")
    a = axs[0]
    a.set_xlim(-170, 170); a.set_ylim(-45, 135)
    a.annotate("", (-D / 2, 112), (D / 2, 112), arrowprops=dict(arrowstyle="<->"))
    a.text(0, 116, f"D = {D} nm", ha="center", fontsize=8)
    a.annotate("", (150, 0), (150, h1), arrowprops=dict(arrowstyle="<->")); a.text(153, 50, f"h1 = {h1}", fontsize=8)
    a.annotate("", (150, -h2), (150, 0), arrowprops=dict(arrowstyle="<->")); a.text(153, -20, f"h2 = {h2}", fontsize=8)
    a.text(-150, 60, "Au", fontsize=9); a.text(-150, -22, "Si$_3$N$_4$", fontsize=8); a.text(-30, 60, "water", fontsize=9)
    a.annotate("", (40, 100), (40, 130), arrowprops=dict(arrowstyle="->")); a.text(44, 120, "light, E along x", fontsize=7)
    b = axs[1]
    b.set_xlim(0, 26); b.set_ylim(-6, 12)
    b.annotate("", (0, -3), (R, -3), arrowprops=dict(arrowstyle="<->")); b.text(R / 2, -2.4, f"R = {R}", ha="center", fontsize=8)
    b.annotate("", (R + 7, 0), (R + 7, bowl(R + 7)), arrowprops=dict(arrowstyle="<->"))
    b.text(R + 7.6, 1.2, f"h3 = {h3} nm", fontsize=7)
    b.set_title(f"rim (zoom), corners rounded by {rho} nm", fontsize=8)
    fig.tight_layout(); fig.savefig(fname, dpi=200); plt.close(fig)


schematic()


# ---------- resonance vs pore radius: paper (Fig. S4) vs Meep ----------
PAPER = {10: 785, 2.5: 710, 1: 640}
fig, ax = plt.subplots(figsize=(4.6, 3.4))
ax.plot(list(PAPER), list(PAPER.values()), "ko-", label="Zhao et al. 2023, Fig. S4 (COMSOL)")
for cases, style, lab in (
        ({10: "rf_bowl_R10_r1500", 2.5: "rf_bowl_R2.5_r1500", 1: "rf_bowl_R1_r1500"}, "C3s--",
         "Meep: h3 = 5 nm, sharp rim, plane wave"),
        ({10: "fit_bowl_R10_h3_r1500", 2.5: "fit_bowl_R2.5_h3_r1500", 1: "fit_bowl_R1_h3_r1500"}, "C0^-",
         "Meep: h3 = 3 nm, rim rounded 1 nm, Gaussian beam")):
    pts = [(R_, summary[c]["lam_res_nm"]) for R_, c in cases.items() if c in summary]
    if pts:
        ax.plot(*zip(*pts), style, label=lab)
ax.set_xlabel("pore radius R (nm)"); ax.set_ylabel("resonance wavelength (nm)")
ax.legend(fontsize=7); fig.tight_layout(); fig.savefig("figures/resonance_vs_R_paper.png", dpi=200); plt.close(fig)


# ---------- Mie validation (and grid convergence) ----------
from meep.materials import Au
from scattnlay import fieldnlay
mie_rows, fig, ax = [], None, None
for res in (1000, 1500, 2000):
    d, e = load(f"sphere_r{res}"), load(f"empty_r{res}")
    if d is None or e is None:
        continue
    iz = np.argmin(np.abs(d["zs"]))
    for lam in (0.53, 0.785):
        i = np.argmin(np.abs(d["lam"] - lam))
        I0 = np.abs(e["Er"][i]).mean() ** 2
        r = d["rs"]; sel = r > 0.0259     # skip the staircased surface pixel
        I = (np.abs(d["Er"][i, sel, iz]) ** 2 + np.abs(d["Ez"][i, sel, iz]) ** 2) / I0
        k = 2 * np.pi * 1.33 / d["lam"][i]
        m = np.sqrt(complex(Au.epsilon(1 / d["lam"][i])[0, 0])) / 1.33
        _, E, _ = fieldnlay(np.array([k * 0.025]), np.array([m]), k * r[sel], 0 * r[sel], 0 * r[sel])
        Im = np.sum(np.abs(E) ** 2, axis=1)
        g = (r[sel] - 0.025) * 1e3
        for gg in (1, 2, 5, 10):
            j = np.argmin(np.abs(g - gg))
            mie_rows.append(dict(res_nm=round(1e3 / res, 2), lam_nm=float(d["lam"][i] * 1e3), dist_nm=float(g[j]),
                                 meep=float(I[j]), mie=float(Im[j]), err_pct=float(100 * (I[j] / Im[j] - 1))))
        if fig is None:
            fig, ax = plt.subplots(figsize=(5, 3.6))
        c = "C0" if lam < 0.6 else "C3"
        if res == 1000:
            ax.semilogy(g, Im, c, label=f"Mie, {d['lam'][i]*1e3:.0f} nm")
        ax.semilogy(g, I, c, ls="", marker={1000: "o", 1500: "s", 2000: "^"}[res], ms=3, mfc="none",
                    label=f"Meep {1e3/res:.2g} nm grid, {d['lam'][i]*1e3:.0f} nm")
if fig is not None:
    ax.set_xlim(0, 25); ax.set_xlabel("distance from Au sphere surface along E (nm)")
    ax.set_ylabel(r"$|E|^2/|E_0|^2$"); ax.legend(fontsize=7)
    ax.set_title("50 nm Au sphere in water: Meep vs exact Mie", fontsize=9)
    fig.tight_layout(); fig.savefig("figures/mie_validation.png", dpi=200); plt.close(fig)
    summary["mie_validation"] = mie_rows

# ---------- particle in pore (3D) ----------
for res in (667, 500):
    e = load(f"pip_empty_r{res}")
    if e is None:
        continue
    I0 = e["I_xz"].mean()
    for tag in ("g5", "g10", "hole"):
        d = load(f"pip_{tag}_r{res}")
        if d is None:
            continue
        water = d["eps_xz"].squeeze() == 0
        Ixz, Ixy = d["I_xz"] / I0, d["I_xy"] / I0
        ix = np.argmin(np.abs(d["x_xz"] - (d["xp"] + d["Rp"] + 0.5e-3 * float(d["gap"]))))
        iz = np.argmin(np.abs(d["z_xz"] - d["zp"]))
        summary[f"pip_{tag}_r{res}"] = dict(gap_centre=float(Ixz.squeeze()[ix, iz]), max_xz=float(Ixz[water].max()),
                                            max_xy=float(Ixy[d["eps_xy"].squeeze() == 0].max()))
        if res != 667 and load("pip_g5_r667") is not None:
            continue
        fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
        vmax = max(Ixz.max(), Ixy.max(), 10)   # one colour scale for both panels
        for ax, I, eps, a1, a2, lab in [(axs[0], Ixz, d["eps_xz"], d["x_xz"], d["z_xz"], "z"),
                                         (axs[1], Ixy, d["eps_xy"], d["x_xy"], d["y_xy"], "y")]:
            m = ax.pcolormesh(a1 * 1e3, a2 * 1e3, I.squeeze().T, norm=LogNorm(0.1, vmax), cmap="inferno", shading="auto")
            ax.contour(a1 * 1e3, a2 * 1e3, (eps.squeeze() > 0).T, levels=[0.5], colors="c", linewidths=0.6)
            ax.set_aspect("equal"); ax.set_xlabel("x (nm)  [E along x]"); ax.set_ylabel(f"{lab} (nm)")
        axs[0].set_title("side view (y = 0)", fontsize=9); axs[1].set_title("top view (mid-height of Au)", fontsize=9)
        fig.colorbar(m, ax=axs, label=r"$|E|^2/|E_0|^2$ at 785 nm")
        fig.savefig(f"figures/pip_{tag}_maps.png", dpi=200, bbox_inches="tight"); plt.close(fig)

json.dump(summary, open("summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
