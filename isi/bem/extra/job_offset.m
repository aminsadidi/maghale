function job_offset(spec, outdir)
%  JOB_OFFSET - tolerance to emitter position: dipole on a spacer shell of thickness s around the rod tip,
%    at polar angle theta from the axis (theta = 0: on axis), oriented normal (n), tangential (t) and along y.
op = bemoptions('sim', 'ret', 'interp', 'curv');
epstab = {epsconst(1), epstable('gold.dat')};
D = 20;  L = 60;  R = D / 2;
[p0, ztop] = bemx_rod(D, L, 2, op);
p = comparticle(epstab, {p0}, [2, 1], 1, op);
s = sscanf(spec, 's%d');
th = (0:10:90) * pi / 180;  np = numel(th);
c = [0, 0, ztop - R];
pos = zeros(np, 3);  dd = zeros(np, 3, 3);
for i = 1:np
    n = [sin(th(i)), 0, cos(th(i))];  t = [cos(th(i)), 0, -sin(th(i))];
    pos(i, :) = c + (R + s) * n;
    dd(i, :, 1) = n;  dd(i, :, 2) = t;  dd(i, :, 3) = [0, 1, 0];
end
pt = compoint(p, pos, op);
if pt.n ~= np, error('compoint kept %d of %d points', pt.n, np); end
dip = dipole(pt, dd, 'full', op);
bem = bemsolver(p, op);
lam = 500:5:900;  M = zeros(numel(lam), 1 + 6 * np);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);                     % [np, 3]
    row = lam(il);
    for i = 1:np, row = [row, tot(i, 1), rad(i, 1), tot(i, 2), rad(i, 2), tot(i, 3), rad(i, 3)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for i = 1:np, a = round(th(i) * 180 / pi); hdr = [hdr, sprintf(',Fp_n_th%d,T_n_th%d,Fp_t_th%d,T_t_th%d,Fp_y_th%d,T_y_th%d', a, a, a, a, a, a)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, sprintf('offset_s%d.csv', s)), hdr, M, sprintf('rod L60 D20, spacer s=%d nm around the tip, faces=%d', s, p.n));
