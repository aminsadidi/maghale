"""offline validation of lab/farfield.py: exact fields of two x-dipoles (exp(-i w t)) phased for end-fire towards +y"""
import sys, numpy as np
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "lab")); import farfield as FF
n = 1.5; lam = np.array([1.4e-6, 1.55e-6, 1.7e-6]); eps = 8.854e-12 * n**2; c = 2.998e8
dsep = 300e-9
def fields(R, k, w):
    E = np.zeros(R.shape, complex); H = np.zeros(R.shape, complex)
    for y0, ph in ((-dsep/2, 0.0), (dsep/2, None)):
        p = np.array([1e-30, 0, 0]) * (np.exp(1j * k * dsep * 0.75) if ph is None else 1)
        rv = R - np.array([0, y0, 0]); r = np.linalg.norm(rv, axis=-1)[..., None]; u = rv / r
        g = np.exp(1j * k * r)
        E += (k**2 * np.cross(np.cross(u, p), u) / r + (3 * u * np.sum(u * p, -1)[..., None] - p) * (1 / r**3 - 1j * k / r**2)) * g / (4 * np.pi * eps)
        H += (w * k / (4 * np.pi)) * np.cross(u, p) / r * (1 - 1 / (1j * k * r)) * g
    return E, H
box = [(-400e-9, 400e-9), (-350e-9, 450e-9), (-250e-9, 250e-9)]
def grid(lo, hi, m): return np.linspace(lo, hi, m)
faces = []
for ax in range(3):
    for s, pos in ((-1, box[ax][0]), (1, box[ax][1])):
        cs = [grid(*box[a], 41) if a != ax else np.array([pos]) for a in range(3)]
        X, Y, Z = np.meshgrid(*cs, indexing='ij'); R = np.stack([X, Y, Z], -1)
        Es = []; Hs = []
        for l in lam:
            k = 2*np.pi*n/l; w = 2*np.pi*c/l; E, H = fields(R, k, w); Es.append(E); Hs.append(H)
        faces.append(FF.face(ax, s, cs, np.stack(Es, 3), np.stack(Hs, 3)))
d, U, Pb, ratio = FF.project(faces, lam, n, ndir=4000, sign=1)
# analytic far field: pattern |p x r^ x r^|^2 times |array factor|^2
for i, l in enumerate(lam):
    k = 2*np.pi*n/l; AF = 1 + np.exp(1j*k*dsep*0.75) * np.exp(-1j*k*d[:,1]*dsep)
    Ua = (1 - d[:,0]**2) * np.abs(AF)**2
    fa_p = Ua[d[:,1] >= 0.5].sum()/Ua.sum(); fa_m = Ua[d[:,1] <= -0.5].sum()/Ua.sum()
    f_p = FF.cone_fraction(d, U, [0,1,0], np.pi/3)[i]; f_m = FF.cone_fraction(d, U, [0,-1,0], np.pi/3)[i]
    corr = np.corrcoef(U[i], Ua)[0,1]
    print(f'{l*1e9:.0f} nm: P_ff/P_box = {ratio[i]:.4f} | f(+y) {f_p:.4f} (exact {fa_p:.4f}) f(-y) {f_m:.4f} (exact {fa_m:.4f}) | pattern corr {corr:.5f}')
d2, U2, _, _ = FF.project(faces, lam[1:2], n, ndir=4000, sign=-1)
print('wrong sign: f(+y) =', FF.cone_fraction(d2, U2, [0,1,0], np.pi/3)[0].round(4), '(mirrored, as expected)')
