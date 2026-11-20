# Tamm plasmon device and SARS-CoV-2 VLPs: simulation plan

Experiment: Rossini, Marangi, Bertolotti, Scotognella, Lanzani, Paternò, "Tamm Plasmon Resonance Responsiveness to SARS-CoV-2
Virus-Like Particles" (arXiv:2601.03795; published version doi:10.1002/nap2.70138). Data: Zenodo 10.5281/zenodo.18064645 (CC-BY-4.0),
copied in `data/` (xlsx as published, csv extracted by us).

Device: glass / 5 x (SiO2 110 nm / TiO2 90 nm, spin-coated ~5 nm nanoparticles, annealed 420 C) / Ag 33 nm (thermal evaporation,
island-like film, grains ~50 +- 18 nm, Rms 8.7 nm, 14.4 % voids). Reflectance/transmittance 350-850 nm, Lambda 1050 + integrating sphere.
Tamm dip at 586-660 nm depending on the sample. Exposure: 100 uL drop of PBS (0.01 M) with VLPs (0-50 ng/mL), sample placed Ag side on the drop.

Observations from the data (data/*.csv):
* Every exposure, even PBS alone, red-shifts the dip by ~80-130 nm (Fig 2a: 84, 82, 105, 105, 88 nm for PBS).
* VLPs mainly reduce the dip depth: dR = +15 % at 10 ng/mL vs ~ +2 % for PBS; PS spheres (100 nm) and denatured VLPs: no extra change.
* Their metric alpha = atan(dR[%] / dlambda[nm]).

Questions for the simulations
* Q1  What produces the common ~85 nm red shift? (infiltration of water/salt into the porous nanoparticle DBR, change of the Ag film)
* Q2  Which change of the silver reproduces "shallower dip, little extra shift"? (Drude damping, free-electron density, thinning,
      void fraction / island morphology, thin oxide or sulfide shell, adsorbed protein layer)
* Q3  How large is the direct optical effect of the particles themselves (VLPs, PS spheres) at the real surface coverage?
* Q4  Map alpha (and dR, dlambda) onto the physical parameters of Q2, i.e. what alpha measures.

Steps
1. Data extraction and dip analysis (done: data/*.csv).
2. Transfer-matrix model (own code, tested against analytic limits and against the authors' TMM curve, Fig S6); fit of the DBR and
   Tamm-device spectra (layer indices with porosity, thicknesses, Ag model, incidence side) -> baseline model.
3. Q1 with the TMM model: water/PBS filling of the pores (Bruggeman), layer swelling, Ag changes; which reproduces 85 nm.
4. Q2 and Q4 with the TMM model + effective-medium Ag film: sweeps of Drude damping, plasma frequency, thickness, voids, shells;
   dR, dlambda, alpha maps; comparison with Fig 2 / Fig 3 statistics.
5. 3D FDTD (Meep, GitHub Actions matrix): (a) validation of the Meep stack against TMM; (b) realistic island Ag film (random grains,
   several realisations) vs the effective-medium film; (c) one VLP / PS sphere on the island film -> extinction per particle, scaled to
   the real coverage (Q3); (d) island-film changes of Q2 in 3D.
6. Report for Prof. Paternò (English, figures + methods), and a Persian summary for the supervisor.
