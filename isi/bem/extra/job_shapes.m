function job_shapes(spec, outdir)
%  JOB_SHAPES - generality of the anisotropy: other diameters (aspect ratio 3), silver rod, prolate spheroid.
op = bemoptions('sim', 'ret', 'interp', 'curv');
metal = 'gold.dat';  lam = 450:5:1000;
switch spec
    case 'Ag60',      metal = 'silver.dat';  [p0, ztop] = bemx_rod(20, 60, 2, op);  lam = 350:5:900;
    case 'D15',       [p0, ztop] = bemx_rod(15, 45, 1.5, op);
    case 'D25',       [p0, ztop] = bemx_rod(25, 75, 2, op);
    case 'D30',       [p0, ztop] = bemx_rod(30, 90, 2.5, op);
    case 'spheroid60'
        p0 = scale(trisphere(1444, 1), [20, 20, 60]);  ztop = 30;
    otherwise, error('unknown spec %s', spec);
end
epstab = {epsconst(1), epstable(metal)};
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [3 5 10 20];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
bem = bemsolver(p, op);
M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['shape_' spec '.csv']), hdr, M, sprintf('%s %s faces=%d apex_z=%.3f', spec, metal, p.n, ztop));
