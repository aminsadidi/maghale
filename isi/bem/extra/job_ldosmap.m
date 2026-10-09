function job_ldosmap(spec, outdir)
%  JOB_LDOSMAP - maps of the partial local density of states (Fp for x, y, z dipoles) and of the local intensity
%  |E|^2/|E_0|^2 (plane wave polarised along the rod, incident along x) in the xz plane around the rod
%  (one quadrant, x >= 0, z >= 0; points closer than 1.5 nm to the surface are skipped).
%    spec : 'air_L60_608'  (medium, rod length, wavelength) or 'glass_L140_1310' etc.
t = regexp(spec, '(\w+)_L(\d+)_(\d+)', 'tokens', 'once');
nb = 1;  if strcmp(t{1}, 'glass'), nb = 1.45; end
L = str2double(t{2});  lam = str2double(t{3});  D = 20;  R = D / 2;
op = bemoptions('sim', 'ret', 'interp', 'curv');
h = 2;  if L > 120, h = 2.5; end
[p0, ztop] = bemx_rod(D, L, h, op);
p = comparticle({epsconst(nb^2), epstable('gold.dat')}, {p0}, [2, 1], 1, op);
[X, Z] = meshgrid(0:2:(R + 30), 0:2:(ztop + 30));
zc = ztop - R;
dist = sqrt(X.^2 + max(Z - zc, 0).^2) - R;          % distance to the capsule surface
keep = dist >= 1.5;
x = X(keep);  z = Z(keep);  n = numel(x);
pt = compoint(p, [x, 0 * x, z], op);
dip = dipole(pt, [1 0 0; 0 1 0; 0 0 1], op);
bem = bemsolver(p, op);
sig = bem \ dip(p, lam);
[tot, rad] = decayrate(dip, sig);
exc = planewave([0 0 1], [1 0 0], op);
emesh = meshfield(p, x, 0 * x, z, op, 'nmax', 2000);
sw = bem \ exc(p, lam);
e = emesh(sw) + emesh(exc.field(emesh.pt, lam));
E2 = sum(abs(e(:, :, 1)).^2, 2);  Ez2 = abs(e(:, 3, 1)).^2;
M = [x, z, dist(keep), tot, rad, E2, Ez2];
bemx_csv(fullfile(outdir, ['ldosmap_' spec '.csv']), 'x,z,dist,Fp_x,Fp_y,Fp_z,T_x,T_y,T_z,E2,Ez2', M, ...
    sprintf('LDOS map %s: n=%.2f L=%d D=%d lambda=%g faces=%d', spec, nb, L, D, lam, p.n));
