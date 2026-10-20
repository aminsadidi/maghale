Subject: Re: Near-field simulations for your plasmonic nanopore SERS work

Dear Dr. Huang,

Thank you for suggesting the bowl-shaped nanopore. I have simulated it, together with the particle-in-pore case from your first message, using Meep (open-source FDTD, MIT). Code, data and figures are public: https://github.com/aminsadidi/maghale/tree/claude/blissful-tesla-koo9fh/nanopore_meep

1. Validation. For a 50 nm Au sphere in water the solver reproduces exact Mie theory to within 1-5 % at 2-10 nm from the surface on a 0.5 nm grid, and the error decreases with mesh refinement.

2. Bowl-shaped nanopore (Nano Lett. 2023, geometry of Fig. S2/Table S1, Rakic gold refitted with a stable 3-pole model, water 1.33, SiN 2.0, plane wave from the Au side). Because the structure is axisymmetric, I solve it exactly in cylindrical coordinates (m = +1 and its mirror image for linear polarisation), which allows 0.5-1 nm grids.
   - The bowl pore gives a single hot spot at the pore rim, about 25 times stronger at 785 nm than a conventional cylindrical pore with the same 5 nm Au edge (Fig. S3/S4).
   - The conventional pore agrees well with Fig. S4: resonance at 640 nm and |E|^2/|E0|^2 of about 10 for R = 2.5 nm; 880 nm (vs 840 nm) for R = 10 nm.
   - For the bowl with R = 10 nm and h3 = 5 nm I find the resonance at 710 nm instead of 785 nm. The resonance is very sensitive to the Au thickness at the rim: it moves from 650 nm (h3 = 10 nm) to 800 nm (h3 = 2.5 nm), so with h3 of about 3 nm, within the 2.5-10 nm range of Table S1, it falls at 785 nm. A 40 nm pore with h3 = 5 nm resonates at 750 nm.
   - The resonance position is mesh-converged, but the peak intensity at the sharp 90-degree rim is not (it keeps rising with refinement), so I would round the rim edge (e.g. 1 nm radius) before quoting absolute enhancement values.

3. Particle in the 200 nm Au nanohole (Nat. Commun. 2019), 50 nm Au sphere at 5 nm from the wall, 785 nm, full 3D.
   - The bare hole gives |E|^2/|E0|^2 of about 23 at its upper rim; the particle creates a gap hot spot along the polarisation, as in Fig. 1e.
   - In a 5 nm gap the intensity is not yet mesh-converged on 2 and 1.5 nm grids (74 and 41 at the maximum); a 10 nm gap is running for a converged reference, and sub-nanometre gaps or urchin tips would need a finer local mesh than a uniform 3D FDTD grid allows on our hardware.

The nanourchin was replaced by a smooth sphere, as you suggested the real shape is complicated; adding sharp tips would be the natural next step.

If you can share the exact bowl profile and the excitation (Gaussian beam from the Au side?) used in your COMSOL model, I can make the comparison quantitative, and I would be glad to continue with any geometry that is useful for your current experiments.

Best regards,
Amin Hossain Sadidi
