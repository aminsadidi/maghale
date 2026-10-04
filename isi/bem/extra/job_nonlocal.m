function job_nonlocal(spec, outdir)
%  JOB_NONLOCAL - hydrodynamic nonlocal correction via the local-analogue cover layer of Luo et al., PRL 111, 093901 (2013):
%    a layer of thickness dd with eps_t = eps_m eps_b q_L dd / (eps_m - eps_b),  q_L = sqrt(wp^2/eps_inf - w(w+i g)) / beta.
%    Gold parameters: hbar wp = 9.02 eV, eps_inf = 9.84, hbar g = 0.071 eV, beta = sqrt(3/5) v_F, v_F = 1.40e6 m/s.
%    spec : 'local' or 'nonlocal' (same meshes)
op = bemoptions('sim', 'ret', 'interp', 'curv');
op = bemoptions(op, 'npol', 20, 'refine', 3);
dd = 0.05;  D = 20;  L = 60;
units;
beta = sqrt(3 / 5) * 1.40e6 / 2.998e8;
ql = @(w) 2 * pi * sqrt(9.02^2 / 9.84 - w .* (w + 1i * 0.071)) / (beta * eV2nm);
eb = epsconst(1);  em = epstable('gold.dat');
et = epsfun(@(enei) em(enei) .* eb(enei) ./ (em(enei) - eb(enei)) .* ql(eV2nm ./ enei) * dd);
[p2, ztop2] = bemx_rod(D - 2 * dd, L - 2 * dd, 2, op);
if strcmp(spec, 'nonlocal')
    p1 = coverlayer.shift(p2, dd);
    p = comparticle({eb, em, et}, {p1, p2}, [3, 1; 2, 3], 1, 2, op);
    bem = bemsolver(p, op, 'refun', coverlayer.refine(p, [1, 2]));
    ztop = ztop2 + dd;
else
    [p1, ztop] = bemx_rod(D, L, 2, op);
    p = comparticle({eb, em}, {p1}, [2, 1], 1, op);
    bem = bemsolver(p, op);
end
gaps = [3 5 10];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
lam = 500:5:800;  M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['nonlocal_' spec '.csv']), hdr, M, sprintf('rod L60 D20 %s, cover layer %.2f nm, faces=%d', spec, dd, p.n));
