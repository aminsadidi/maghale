function job_trimap(spec, outdir)
%  JOB_TRIMAP - field and LDOS maps in the plane z = 0 of the gold-nanorod dimer/trimer (host n = 1.5, D = 60 nm,
%  gap 40 nm, mesh 5 nm as in job_tri2).
%    (1) local intensity |E|^2/|E0|^2 for a plane wave at normal incidence (along z), polarised along x and along y,
%        on a 6 nm grid over the whole structure                                  -> trimap_<spec>_field.csv
%    (2) partial LDOS (Fp for x, y, z dipoles) and radiative enhancement T_x on a 2 nm grid in the gap region
%        x = -16 ... 16, y = -40 ... 40 nm                                         -> trimap_<spec>.csv
%  Points closer than 3 nm to a metal surface are skipped (they are not resolved by the 5 nm mesh).
%  spec: 'L270_w1550' (dimer) or 'L270_R300_A0_Y160_w1520' (trimer); tokens as in job_tri2, w<nm> = wavelength.
n = 1.5;  D = 60;  L = 300;  L3 = 0;  A = 35;  X3 = 0;  Y3 = 160;  g = 40;  h = 5;  lam = 1550;
tok = strsplit(spec, '_');
for k = 1:numel(tok)
    t = tok{k};  v = str2double(t(2:end));
    switch t(1)
        case 'L', L = v;   case 'R', L3 = v;  case 'A', A = v;  case 'X', X3 = v;  case 'Y', Y3 = v;  case 'w', lam = v;
        otherwise, error('job_trimap: unknown token %s', t);
    end
end
op = bemoptions('sim', 'ret', 'interp', 'curv');
gold = epstable('gold.dat');
[r, ~] = bemx_rod(D, L, h, op);  r = rot(r, 90, [0, 1, 0]);
xc = g / 2 + L / 2;  rods = {shift(r, [-xc, 0, 0]), shift(r, [xc, 0, 0])};
segs = [-xc - (L - D) / 2, 0, -xc + (L - D) / 2, 0;  xc - (L - D) / 2, 0, xc + (L - D) / 2, 0];   % rod axes (capsules)
if L3 > 0
    [r3, ~] = bemx_rod(D, L3, 1.4 * h, op);  r3 = rot(r3, 90, [0, 1, 0]);  r3 = rot(r3, A, [0, 0, 1]);
    [~, i] = max(r3.verts(:, 1));
    if A < 90 && r3.verts(i, 2) < 0, r3 = rot(r3, -2 * A, [0, 0, 1]); end
    rods{end + 1} = shift(r3, [X3, Y3, 0]);
    u = [cosd(A), sind(A)] * (L3 - D) / 2;  segs(end + 1, :) = [X3 - u(1), Y3 - u(2), X3 + u(1), Y3 + u(2)];
end
nr = numel(rods);  cl = num2cell(1:nr);
p = comparticle({epsconst(n^2), gold}, rods, repmat([2, 1], nr, 1), cl{:}, op);
bem = bemsolver(p, op);
dsurf = @(x, y) min(cell2mat(arrayfun(@(k) segdist(x, y, segs(k, :)), 1:size(segs, 1), 'UniformOutput', false)), [], 2) - D / 2;

%  (1) plane-wave intensity map
[X, Y] = meshgrid(-(xc + L / 2 + 30):6:(xc + L / 2 + 30), -100:6:(Y3 + 100 * (L3 > 0) + 60 * (L3 == 0)));
x = X(:);  y = Y(:);  ds = dsurf(x, y);  keep = ds >= 3;  x = x(keep);  y = y(keep);
exc = planewave([1 0 0; 0 1 0], [0 0 1; 0 0 1], op);
emesh = meshfield(p, x, y, 0 * x, op, 'nmax', 2000);
sw = bem \ exc(p, lam);
e = emesh(sw) + emesh(exc.field(emesh.pt, lam));
E2x = sum(abs(e(:, :, 1)).^2, 2);  E2y = sum(abs(e(:, :, 2)).^2, 2);
bemx_csv(fullfile(outdir, ['trimap_' spec '_field.csv']), 'x,y,dist,E2_xpol,E2_ypol', [x, y, ds(keep), E2x, E2y], ...
    sprintf('field map %s: lambda=%g n=%.2f faces=%d', spec, lam, n, p.n));

%  (2) LDOS map in the gap region
[X, Y] = meshgrid(-16:2:16, -40:2:40);
x = X(:);  y = Y(:);  ds = dsurf(x, y);  keep = ds >= 3;  x = x(keep);  y = y(keep);
pt = compoint(p, [x, y, 0 * x], op);
if pt.n ~= numel(x), error('compoint lost points (%d of %d)', pt.n, numel(x)); end
dip = dipole(pt, eye(3), op);
[tot, rad] = decayrate(dip, bem \ dip(p, lam));
bemx_csv(fullfile(outdir, ['trimap_' spec '.csv']), 'x,y,dist,Fp_x,Fp_y,Fp_z,T_x,T_y,T_z', [x, y, ds(keep), tot, rad], ...
    sprintf('LDOS map %s: lambda=%g n=%.2f faces=%d', spec, lam, n, p.n));
end


function d = segdist(x, y, s)
%  distance of the points (x, y) to the segment s = [x1 y1 x2 y2]
a = [s(1), s(2)];  b = [s(3), s(4)];  ab = b - a;
t = ((x - a(1)) * ab(1) + (y - a(2)) * ab(2)) / max(sum(ab.^2), eps);  t = min(max(t, 0), 1);
d = sqrt((x - a(1) - t * ab(1)).^2 + (y - a(2) - t * ab(2)).^2);
end
