# Roadmap: from the course paper to an ISI paper

## Infrastructure audit (October 1405)

| Item | Status | Notes |
|---|---|---|
| Raw data for the 10 Lumerical runs | ✅ complete | `New folder (2)`, `New folder3`; every Table 3 value reproduces exactly from the spectra |
| Paper numbers | ✅ after correction | 3 errors found and fixed (ratio range 500–530 nm, ratio 24, Fp=69) |
| Mie validation | ✅ independently confirmed | separate implementation: Fp=772 @ 506 nm, T=6.58 @ 530 nm |
| Figure-generation scripts and Mie code | ❌ not in the repo | figures were made outside the repo; for ISI they must be rebuilt by scripts from the data |
| Folder layout | ⚠️ messy | names like `New folder3`; `simulation/README.md` is stale (450–800 nm range) |
| Python (numpy/scipy/matplotlib) | ✅ installable | not preinstalled in the container |
| Meep (FDTD) | ⚠️ installed, not calibrated | ~76 s per run at a 2 nm grid on 4 cores; first sphere benchmark disagrees with Mie |
| LaTeX | ⚠️ not installed | available via apt (texlive) |
| Lumerical | ⚠️ only on a friend's laptop | only for a few cross-check runs |
| Container | ⚠️ ephemeral | 4 cores, 15 GB RAM; Meep must be reinstalled each new session (`environment.yml`) |

## Phases

1. **Calibrate the solver (first step, mandatory):** sphere benchmark against Mie to within 3% (`meep_sphere_benchmark.py`).
   Likely causes of the current disagreement: Meep's built-in gold model (Rakić, not Johnson–Christy) and the
   free-space LDOS normalization at the edges of the broadband pulse.
2. **Mesh convergence of the main case (A):** cylindrical grids at 1, 0.5 and 0.25 nm until the peak changes by less than 5% → replaces the ±40%.
   Then the transverse cases (m=±1) and a comparison with the Lumerical results.
3. **New scientific contribution:** Fp/T/η maps vs gap and aspect ratio; intrinsic quantum yield q0;
   aqueous environment n=1.33; collection efficiency into the objective NA (far field).
4. **Writing:** English LaTeX in the target journal's template, all figures as vectors from scripts in the repo, Section 2 condensed.
5. **Submission package:** cover letter, highlights, data availability (Zenodo), suggested reviewers, similarity check, supervisor approval.
