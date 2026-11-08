"""Slides 9 and 11 redrawn with larger, Persian axis labels.
  img/purcell_big.png : Purcell spectrum of the gap-3 run from the original Lumerical data (isi/data/lumerical/G3_rod_axial_gap3_mesh1_spectra.tsv)
  img/box_x2_big.png, img/box_z2_big.png : transmission through the +x and +z faces of the radiative box. Only the Lumerical screenshots
      exist for these (img/box_*_T.png); the curves are read back pixel by pixel on the screenshot's own grid lines and redrawn.
usage: python defense/make_figures3.py"""
import os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(D, 'img')
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 15, 'axes.linewidth': 1.0, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'axes.edgecolor': '#555555', 'xtick.color': '#333333', 'ytick.color': '#333333', 'savefig.bbox': 'tight', 'savefig.dpi': 220,
                     'axes.grid': True, 'grid.color': '#e7e5e4'})
ROD = '#D97706'


def digitize(path, xgrid_vals, ygrid_vals):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int); h, w, _ = a.shape; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = (b > 200) & (r < 170) & (b - r > 60)
    gray = (abs(r - g) < 8) & (abs(g - b) < 8) & (r > 150) & (r < 215)
    cols = np.where(gray.sum(0) > 0.5 * h)[0]; rows = np.where(gray.sum(1) > 0.5 * w)[0]
    assert len(cols) == len(xgrid_vals) and len(rows) == len(ygrid_vals), (cols, rows)
    fx = np.polyfit(cols, xgrid_vals, 1); fy = np.polyfit(rows, ygrid_vals, 1)
    xs, ys = [], []
    for c in range(w):
        rr = np.where(blue[:, c])[0]
        if len(rr): xs.append(np.polyval(fx, c)); ys.append(np.polyval(fy, rr.mean()))
    return np.array(xs), np.array(ys)


def face(src, out, xv, yv, ylab, peak_ref):
    x, y = digitize(os.path.join(IMG, src), xv, yv)
    sel = (x >= 500) & (x <= 900); x, y = x[sel], y[sel]
    i = np.argmax(y); print(f'{src}: peak {y[i]:.1f} at {x[i]:.0f} nm (reference {peak_ref})')
    fig, ax = plt.subplots(figsize=(5.6, 3.7))
    ax.plot(x, y, c=ROD, lw=2.4); ax.set_xlim(500, 900); ax.set_ylim(0, None)
    ax.annotate(f'{peak_ref}', (x[i], y[i]), (12, -4), textcoords='offset points', fontsize=16, color=ROD)
    ax.set_xlabel('طول موج (نانومتر)'); ax.set_ylabel(ylab)
    fig.savefig(os.path.join(IMG, out)); plt.close(fig)


def purcell():
    d = np.genfromtxt(os.path.join(D, '..', 'isi', 'data', 'lumerical', 'G3_rod_axial_gap3_mesh1_spectra.tsv'), delimiter='\t', names=True)
    d = d[np.argsort(d['lambda_nm'])]; lam, Fp = d['lambda_nm'], d['Fp']
    fig, ax = plt.subplots(figsize=(12.0, 3.5))
    ax.plot(lam, Fp, c=ROD, lw=2.4); ax.set_xlim(500, 900); ax.set_ylim(0, 8000)
    for l0, lab in ((515, '۷۲۰۰'), (607, '۴۲۱۱')):
        j = np.argmin(abs(lam - l0)); k = j - 3 + np.argmax(Fp[j - 3:j + 4])
        ax.plot(lam[k], Fp[k], 'o', c='#1C1917', ms=6); ax.annotate(lab, (lam[k], Fp[k]), (10, 2), textcoords='offset points', fontsize=16)
        print(f'Purcell peak near {l0}: {Fp[k]:.0f} at {lam[k]:.0f} nm')
    ax.set_xlabel('طول موج (نانومتر)'); ax.set_ylabel('فاکتور پورسل')
    fig.savefig(os.path.join(IMG, 'purcell_big.png')); plt.close(fig)


if __name__ == '__main__':
    purcell()
    face('box_x2_T.png', 'box_x2_big.png', np.arange(550, 851, 50), np.arange(50, 4, -5), 'توان عبوری / خلأ', '۵۴/۵')
    face('box_z2_T.png', 'box_z2_big.png', np.arange(550, 851, 50), np.arange(16, 1, -2), 'توان عبوری / خلأ', '۱۶/۵')
