function job_tips(spec, outdir)
%  JOB_TIPS - sensitivity to the shape of the rod ends: L = 60 nm, D = 20 nm, end caps with axial semi-axis
%    c = r*R (r = 1: hemispherical, smaller r: flatter), dipole on the axis, axial (z) and transverse (x).
r = sscanf(spec, 'c%f');
op = bemoptions('sim', 'ret', 'interp', 'curv');
epstab = {epsconst(1), epstable('gold.dat')};
[p0, ztop] = bemx_tiprod(20, 60, r * 10, 2, op);
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [3 5 10 20];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
bem = bemsolver(p, op);
lam = 450:5:900;  M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['tips_' spec '.csv']), hdr, M, sprintf('rod L60 D20, end-cap semi-axis c = %.2f R, faces=%d', r, p.n));
