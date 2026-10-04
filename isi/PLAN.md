# Roadmap: from the course paper to an ISI paper — current status

## Done
- [x] Data audit: every Table 3 number reproduces from the raw spectra; 3 text errors fixed
- [x] Mie validation reproduced independently (`isi/sim/mie.py`)
- [x] All 44 DOIs checked against doi.org; one nonexistent reference (Chen 2009) replaced by Ni et al., ACS Nano 2008 (in both the course and ISI versions)
- [x] Johnson–Christy gold Drude–Lorentz fit, rms 1.6% (`isi/sim/fit_jc.py`, `gold_jc.py`)
- [x] Body-of-revolution Meep solver: Fp, T, eta, NA collection (`isi/sim/nanorod.py`); dielectric benchmark within 1% of Mie in the band centres at a 2-nm grid
- [x] Self-contained Colab notebook with Drive checkpointing (`isi/colab/meep_nanorod.ipynb`); MPI runner tested
- [x] Vector figures from raw data (`isi/analysis/make_figures.py`), including the new q0 analysis
- [x] English manuscript (`isi/paper/main.tex`, 11 pages, 37 refs), SI (`si.tex`), cover letter + highlights
- [x] Ingest script for Colab results (`isi/analysis/ingest_colab.py results.zip` -> `isi/results/summary.md`)
- [x] Raw data with clean names for Zenodo (`isi/data/`)

## Done (heavy runs)
- [x] 54 Meep runs on GitHub Actions (stages A, B), results in `isi/results/ci`, summary in `isi/results/summary.md`
- [x] T validated vs Mie: 7.2% at 1 nm, 4.4% extrapolated; rod radiative peak 125 @ 611 nm vs Lumerical 119 @ 616 nm
- [x] Collection efficiency converged (NA 0.9: 18.0%); antenna keeps the dipolar pattern -> lay rods in the focal plane
- [x] Fp in a 5-nm gap NOT converged in staircased FDTD at 1 nm -> Fp taken from Lumerical (conformal), BEM recommended

## Waiting on the user
- [~] MNPBEM run: script isi/bem/run_mnpbem.m + guide isi/bem/README_fa.md ready; waiting for results_bem_full.zip from friend laptop -> python isi/analysis/ingest_bem.py
- [ ] Supervisor approval + corresponding-author e-mail
- [ ] Target journal (template, word limit, reference style)

## After results arrive
1. `python isi/analysis/ingest_colab.py results.zip`
2. Fill every \TBD in main.tex / si.tex from `isi/results/summary.md`
3. Add the convergence figure and the design maps (air/water, NA collection) to the Results section
4. Move to the journal template; final language pass; Zenodo upload; similarity check
