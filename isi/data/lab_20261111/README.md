# Lab campaign 2 (2026-11-07 ... 11), supervisor PC (6 cores, 64 GB), Lumerical 2024 R1 + MATLAB R2018b / MNPBEM

- `lumerical/`: all FDTD runs (far field in the BEM definition: ff_py60, ff_my60, ff_zNA13, ff_zNA09; ff_check = P_ff/P_box).
  Selected design (automatic, `selected.json`): L = 275 nm, R3 = 295 nm, Y3 = 160 nm.
- BEM (job_tri2) of the selected design at h = 4 and 3 nm: `isi/results/bem_extra/tri2_L275_R295_A0_Y160_H{4,3}_c*.csv`.
- KNOWN ISSUE: `fdtd_sw_L270.csv` and `fdtd_sw_L275.csv` (dimers): the far-field sign check tied (symmetric structure) and took the
  wrong convention, ff_check = 1.5; their ff_* columns are invalid (Fp, T, eta are not affected). Fixed in labkit/lab/lumerical_fdtd.py.
