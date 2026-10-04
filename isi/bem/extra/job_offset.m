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
pos = zeros(np, 3);
for i = 1:np, pos(i, :) = c + (R + s) * [sin(th(i)), 0, cos(th(i))]; end
pt = compoint(p, pos, op);
if pt.n ~= np, error('compoint kept %d of %d points', pt.n, np); end
%  rates are quadratic forms in the (real) dipole direction u: rate(u) - 1 = u' G u, so five fixed directions
%  x, y, z, (x+z)/sqrt2, (x-z)/sqrt2 give the normal (n) and tangential (t) rates exactly
dip = dipole(pt, [1 0 0; 0 1 0; 0 0 1; [1 0 1] / sqrt(2); [1 0 -1] / sqrt(2)], op);
bem = bemsolver(p, op);
lam = 500:5:900;  M = zeros(numel(lam), 1 + 6 * np);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);                     % [np, 5]
    row = lam(il);
    for i = 1:np
        sn = sin(th(i));  cs = cos(th(i));
        Q = {tot(i, :) - 1, rad(i, :)};  out = zeros(1, 6);
        for q = 1:2
            v = Q{q};  gxz = (v(4) - v(5)) / 2;
            vn = sn^2 * v(1) + cs^2 * v(3) + 2 * sn * cs * gxz;
            vt = cs^2 * v(1) + sn^2 * v(3) - 2 * sn * cs * gxz;
            out([q, q + 2, q + 4]) = [vn, vt, v(2)];
        end
        out([1 3 5]) = out([1 3 5]) + 1;                  % back from (rate - 1) to rate for tot
        row = [row, out]; %#ok<AGROW>
    end
    M(il, :) = row;
end
hdr = 'lambda_nm';
for i = 1:np, a = round(th(i) * 180 / pi); hdr = [hdr, sprintf(',Fp_n_th%d,T_n_th%d,Fp_t_th%d,T_t_th%d,Fp_y_th%d,T_y_th%d', a, a, a, a, a, a)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, sprintf('offset_s%d.csv', s)), hdr, M, sprintf('rod L60 D20, spacer s=%d nm around the tip, faces=%d', s, p.n));
