Subject: Re: Near-field simulations for your plasmonic nanopore SERS work

Dear Dr. Huang,

Thank you for suggesting the bowl-shaped nanopore. I have simulated it, together with the particle-in-pore case from your first message, using Meep (open-source FDTD, MIT). Code, data and figures are public: https://github.com/aminsadidi/maghale/tree/claude/blissful-tesla-koo9fh/nanopore_meep

1. Validation. The solver reproduces exact Mie theory for a 50 nm Au sphere in water to within 1-5 % at 2-10 nm from the surface (0.5 nm grid), and the error decreases with mesh refinement.

2. Bowl-shaped nanopore (Nano Lett. 2023, geometry of Fig. S2/Table S1, Rakic gold, water 1.33, SiN 2.0). Because the structure is axisymmetric, I solve it exactly in cylindrical coordinates (m = +1 and its mirror image for linear polarisation), which allows 0.5-1 nm grids.
BOWL_SUMMARY

3. Particle in the 200 nm Au nanohole (Nat. Commun. 2019), 50 nm Au sphere at 5 nm from the wall, 785 nm, full 3D.
PIP_SUMMARY

The nanourchin was replaced by a smooth sphere, as you suggested the real shape is complicated; adding sharp tips would be the natural next step.

If you can share the exact bowl profile and the excitation (Gaussian beam from the Au side?) used in your COMSOL model, I can make the comparison quantitative, and I would be glad to continue with any geometry that is useful for your current experiments.

Best regards,
Amin Hossain Sadidi
