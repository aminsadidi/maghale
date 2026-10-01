# Data (for Zenodo / data-availability statement)

`lumerical/` — raw spectra of the ten three-dimensional FDTD runs (Lumerical FDTD 2024 R1), one file per case:
columns `lambda_nm  Fp  T  eta  Ploss` (201 wavelengths, 500–900 nm, raw definitions: Fp = P_tot/P_0, T = P_rad/P_0).
`run_cases.lsf` builds and runs every case from scratch.

| file prefix | geometry | dipole | gap (nm) | mesh (nm) |
|---|---|---|---|---|
| A_rod_axial_gap5_mesh2 | rod L=60, D=20 | axial (z) | 5 | 2 |
| B_freespace | – | z | – | 2 |
| C_rod_transverse_gap5_mesh2 | rod | transverse (x) | 5 | 2 |
| D_sphere_radial_gap5_mesh2 | sphere R=15.874 | radial | 5 | 2 |
| Dperp_sphere_tangential_gap5_mesh2 | sphere | tangential | 5 | 2 |
| G3 / G10 / G20 | rod | axial | 3 / 10 / 20 | 1 / 2 / 2 |
| M3 / M1.5 | rod | axial | 5 | 3 / 1.5 |

Body-of-revolution (Meep) results from the Colab notebook go to `../results/` (see `../analysis/ingest_colab.py`).
