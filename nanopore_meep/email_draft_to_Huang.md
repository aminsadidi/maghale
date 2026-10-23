Subject: Re: Near-field simulations for your plasmonic nanopore SERS work

Dear Dr. Huang,

Thank you for suggesting the bowl-shaped nanopore. I have simulated it, together with the particle-in-nanohole case from your earlier message, using the open-source FDTD code Meep. A short technical report is attached; the main points are:

1. The solver reproduces exact Mie theory for a 50 nm Au sphere in water to within 1-2 % at 5-10 nm from the surface, and the conventional-pore results of your Fig. S4 (e.g. 640 nm and |E|^2/|E0|^2 of about 10 for R = 2.5 nm).

2. For the bowl pore, the resonance is set mainly by the Au thickness at the rim: it moves from 650 to 800 nm as h3 goes from 10 to 2.5 nm. With h3 = 3 nm, a slightly rounded rim and the 500 nm Gaussian beam of your SI, I obtain 790, 710 and 700 nm for R = 10, 2.5 and 1 nm, against 785, 710 and 640 nm in Fig. S4.

3. The resonance positions are mesh-converged, but the peak enhancement at the rim is not, because the rim is a nearly sharp metal edge; absolute values depend on the edge radius and the mesh.

4. In the 200 nm nanohole, a 50 nm Au particle near the wall creates a gap hot spot as in Fig. 1e of your Nat. Commun. paper; the gap values need a finer local mesh to converge.

I also have hands-on experience with Ansys Lumerical FDTD and COMSOL Multiphysics from my earlier projects. Following your question about licences, I did this work entirely with open-source software, so that it raises no licensing issue for your group; if you can give me access to a licensed COMSOL or Lumerical installation, I can repeat or extend the calculations there directly.

To make the comparison fully quantitative, could you share the rim profile and mesh size used in your COMSOL model, and the illumination side? I would be glad to continue with the geometries that matter most for your current experiments, for example the clustering states of Au particles in the pore.

Best regards,
Amin Hossain Sadidi
University of Isfahan
