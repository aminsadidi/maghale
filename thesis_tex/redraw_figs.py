"""Redraws the Lumerical screenshots of the thesis with large, clear axis labels (supervisor's request).
purcell_nm.png: from the original Lumerical data (isi/data/lumerical/G3_rod_axial_gap3_mesh1_spectra.tsv).
box_*_nm.png: the six transmission-box screenshots (box_*_T.png), read back pixel by pixel on their own grid lines
(checked: peaks 54.5 / 16.5 reproduced) and redrawn; wavelength in nm.
usage: python thesis_tex/redraw_figs.py"""
import os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({'font.family': ['Nazli', 'Vazirmatn'], 'font.size': 17, 'axes.linewidth': 1.1, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.labelsize': 16, 'ytick.labelsize': 16, 'axes.grid': True, 'grid.color': '#e5e5e5', 'savefig.bbox': 'tight', 'savefig.dpi': 220})
C = '#1f4e9c'


def digitize(path, xv, yv):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int); h, w, _ = a.shape; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = (b > 200) & (r < 170) & (b - r > 60)
    gray = (abs(r - g) < 8) & (abs(g - b) < 8) & (r > 150) & (r < 215)
    cols = np.where(gray.sum(0) > 0.5 * h)[0]; rows = np.where(gray.sum(1) > 0.5 * w)[0]
    assert len(cols) == len(xv) and len(rows) == len(yv), (path, len(cols), len(rows))
    fx = np.polyfit(cols, xv, 1); fy = np.polyfit(rows, yv, 1)
    xs, ys = [], []
    for c in range(w):
        rr = np.where(blue[:, c])[0]
        if len(rr): xs.append(np.polyval(fx, c)); ys.append(np.polyval(fy, rr.mean()))
    x, y = np.array(xs), np.array(ys); s = (x >= 500) & (x <= 900)
    return x[s], y[s]


X = np.arange(550, 851, 50)
specs = {'x1': np.arange(-5, -51, -5), 'x2': np.arange(50, 4, -5), 'y1': np.arange(-5, -51, -5), 'y2': np.arange(50, 4, -5),
         'z1': np.arange(-2, -17, -2), 'z2': np.arange(16, 1, -2)}
for k, yv in specs.items():
    x, y = digitize(os.path.join(D, f'box_{k}_T.png'), X, yv)
    i = np.argmax(abs(y)); print(f'box_{k}: extreme {y[i]:+.1f} at {x[i]:.0f} nm')
    fig, ax = plt.subplots(figsize=(5.6, 4.0)); ax.plot(x, y, c=C, lw=2.4); ax.set_xlim(500, 900)
    if y[i] < 0: ax.set_ylim(None, 0.5)
    else: ax.set_ylim(-0.5, None)
    ax.set_xlabel('طول موج (نانومتر)'); ax.set_ylabel('توان عبوری T')
    fig.savefig(os.path.join(D, f'box_{k}_nm.png')); plt.close(fig)
d = np.genfromtxt(os.path.join(D, '..', 'isi', 'data', 'lumerical', 'G3_rod_axial_gap3_mesh1_spectra.tsv'), delimiter='\t', names=True)
d = d[np.argsort(d['lambda_nm'])]
fig, ax = plt.subplots(figsize=(8.0, 3.9)); ax.plot(d['lambda_nm'], d['Fp'], c=C, lw=2.4); ax.set_xlim(500, 900); ax.set_ylim(0, 8000)
ax.set_xlabel('طول موج (نانومتر)'); ax.set_ylabel('فاکتور پورسل')
fig.savefig(os.path.join(D, 'purcell_nm.png')); plt.close(fig); print('purcell_nm.png')
