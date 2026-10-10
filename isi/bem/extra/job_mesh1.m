function job_mesh1(spec, outdir)
%  JOB_MESH1 - finest mesh (h = 1 nm) of the 60 x 20 nm rod in air, split into wavelength chunks so that each chunk
%  fits into the six-hour limit of a CI job (the single run of bem-runs.yml stopped at 808 nm).
%    spec : 'c1' ... 'c4'  (500-596, 600-696, 700-796, 800-900 nm in steps of 4 nm)
k = sscanf(spec, 'c%d');  edges = [500 600 700 800 904];
lam = edges(k):4:(edges(k + 1) - 4);
op = bemoptions('sim', 'ret', 'interp', 'curv');
[p0, ztop] = bemx_rod(20, 60, 1, op);
p = comparticle({epsconst(1), epstable('gold.dat')}, {p0}, [2, 1], 1, op);
gaps = [5 10 20];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
bem = bemsolver(p, op);
M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    [tot, rad] = decayrate(dip, bem \ dip(p, lam(il)));
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['mesh1_' spec '.csv']), hdr, M, sprintf('rod L60 D20 h=1 air, chunk %s, faces=%d', spec, p.n));
