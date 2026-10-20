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


def I0_cyl(res):
    e = load(f"empty_r{res}")
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
LABEL = {"bowl": "bowl", "conv": "conventional"}
fig, ax = plt.subplots(figsize=(5.5, 3.8))
for f in sorted(glob.glob("runs/bowl_*.npz") + glob.glob("runs/conv_*.npz")):
    name = os.path.basename(f)[:-4]
    d = load(name)
    res = int(name.rsplit("_r", 1)[1])
    if d is None or load(f"empty_r{res}") is None:
        continue
    I0 = I0_cyl(res)
    mx, _ = hotspot(d, I0)
    lam = d["lam"] * 1e3
    i785 = np.argmin(np.abs(lam - 785))
    summary[name] = dict(args=str(d["args"]), grid_nm=round(1e3 / res, 2), lam_res_nm=float(lam[mx.argmax()]),
                         max_at_res=float(mx.max()), max_at_785=float(mx[i785]))
    if name in ("bowl_R10_c25_r1500", "bowl_R2.5_r1500", "bowl_R1_r1500", "conv_R10_r1000", "conv_R2.5_r1500",
                "bowl_R10_jc_r1000"):
        ax.semilogy(lam, mx, label=name)
ax.set_xlabel("wavelength (nm)"); ax.set_ylabel(r"max $|E|^2/|E_0|^2$ in water")
ax.axvline(785, color="0.6", ls=":"); ax.legend(fontsize=7); fig.tight_layout()
fig.savefig("figures/hotspot_spectra.png", dpi=200); plt.close(fig)


def side_map(name, res, fname, title):
    d = load(name)
    if d is None:
        return
    i = 0
    I0 = I0_cyl(res)[np.argmin(np.abs(load(f"empty_r{res}")["lam"] - L785))]
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
    I0 = I0_cyl(res)[il]
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


main = next(n for n in ("bowl_R10_c25_r1500", "bowl_R10_c25_r1000", "bowl_R10_jc_r1500", "bowl_R10_jc_r1000")
            if load(n) is not None)                     # finest stable R = 10 nm run available
best = int(main.rsplit("_r", 1)[1])
summary["main_bowl_case"] = main
side_map(main, best, "bowl_R10_side.png", "bowl nanopore, R = 10 nm, Au 5 nm at the pore")
side_map("conv_R10_r1000", 1000, "conv_R10_side.png", "conventional pore, R = 10 nm, Au 5 nm")
top_map(main, best, "bowl_R10_top.png")

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
    for tag in ("g5", "hole"):
        d = load(f"pip_{tag}_r{res}")
        if d is None:
            continue
        water = d["eps_xz"].squeeze() == 0
        Ixz, Ixy = d["I_xz"] / I0, d["I_xy"] / I0
        summary[f"pip_{tag}_r{res}"] = dict(max_xz=float(Ixz[water].max()),
                                            max_xy=float(Ixy[d["eps_xy"].squeeze() == 0].max()))
        if res != 667 and load("pip_g5_r667") is not None:
            continue
        fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
        for ax, I, eps, a1, a2, lab in [(axs[0], Ixz, d["eps_xz"], d["x_xz"], d["z_xz"], "z"),
                                         (axs[1], Ixy, d["eps_xy"], d["x_xy"], d["y_xy"], "y")]:
            m = ax.pcolormesh(a1 * 1e3, a2 * 1e3, I.squeeze().T, norm=LogNorm(0.1, max(I.max(), 10)), cmap="inferno", shading="auto")
            ax.contour(a1 * 1e3, a2 * 1e3, (eps.squeeze() > 0).T, levels=[0.5], colors="c", linewidths=0.6)
            ax.set_aspect("equal"); ax.set_xlabel("x (nm)  [E along x]"); ax.set_ylabel(f"{lab} (nm)")
        axs[0].set_title("side view (y = 0)", fontsize=9); axs[1].set_title("top view (mid-height of Au)", fontsize=9)
        fig.colorbar(m, ax=axs, label=r"$|E|^2/|E_0|^2$ at 785 nm")
        fig.savefig(f"figures/pip_{tag}_maps.png", dpi=200, bbox_inches="tight"); plt.close(fig)

json.dump(summary, open("summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
