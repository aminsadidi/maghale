"""Compare the Meep cylindrical solver with exact Mie theory (scattnlay) for an Au sphere in water."""
import sys
import numpy as np
from meep.materials import Au
from scattnlay import fieldnlay

run, ref, Rnm = sys.argv[1], sys.argv[2], float(sys.argv[3])
d, e = np.load(run), np.load(ref)
n_w = 1.33
iz = np.argmin(np.abs(d["zs"]))                     # z = 0 plane, phi = 0 -> x axis
print("lam_nm  gap_nm  Meep  Mie  err%")
for lam in (0.53, 0.60, 0.785):
    i = np.argmin(np.abs(d["lam"] - lam))
    I0 = np.abs(e["Er"][i]).mean() ** 2
    I = (np.abs(d["Er"][i, :, iz]) ** 2 + np.abs(d["Ez"][i, :, iz]) ** 2) / I0
    m = np.sqrt(Au.epsilon(1 / d["lam"][i])[0, 0]) / n_w
    k = 2 * np.pi * n_w / d["lam"][i]
    for g in (1, 2, 5, 10):
        r = (Rnm + g) * 1e-3
        j = np.argmin(np.abs(d["rs"] - r))
        x = np.array([k * Rnm * 1e-3]); mm = np.array([m])
        coords = np.array([[d["rs"][j], 0, 0]]) * k     # scattnlay: x-polarised, k along z
        _, E, _ = fieldnlay(x, mm, coords[:, 0], coords[:, 1], coords[:, 2])
        Imie = np.sum(np.abs(E[0]) ** 2)
        print(f"{d['lam'][i]*1e3:6.0f} {d['rs'][j]*1e3-Rnm:6.2f} {I[j]:7.2f} {Imie:7.2f} {100*(I[j]/Imie-1):6.1f}")
