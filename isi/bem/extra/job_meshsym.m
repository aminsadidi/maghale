function job_meshsym(spec, outdir)
%  JOB_MESHSYM - wide-range mesh convergence of the decay rates at the gap centre, using mirror symmetry so that
%  fine meshes fit into the memory of a CI runner (host n = 1.5, rods D = 60 nm, gap 40 nm, uniform element size h).
%    'D_L285_H2'            dimer, arms L = 285 nm: symmetry 'xy', only the y >= 0 half of R2 is meshed (1/4 problem)
%    'T_L285_R315_Y160_H3'  trimer with a horizontal R3 (length 315 nm, centre (0, 160) nm): symmetry 'x', R2 and the
%                           x >= 0 half of R3 are meshed (1/2 problem)
%  Emitter at the gap centre, dipole along x. Output: Fp, T at 1310, 1450, 1550, 1650 nm, and the number of faces of the
%  meshed part and of the full structure.
n = 1.5;  D = 60;  g = 40;  L = 300;  L3 = 0;  Y3 = 160;  h = 5;  kind = spec(1);
tok = strsplit(spec(3:end), '_');
for k = 1:numel(tok)
    t = tok{k};  v = str2double(t(2:end));
    switch t(1)
        case 'L', L = v;  case 'R', L3 = v;  case 'Y', Y3 = v;  case 'H', h = v;
        otherwise, error('job_meshsym: unknown token %s', t);
    end
end
lam = [1310 1450 1550 1650];
if kind == 'D', sym = 'xy'; else, sym = 'x'; end
op = bemoptions('sim', 'ret', 'interp', 'curv', 'sym', sym);
gold = epstable('gold.dat');
xc = g / 2 + L / 2;
if kind == 'D'
    r2 = halfrod(D, L, h, 'side', op);                          % y >= 0 half of a rod along x
    parts = {shift(r2, [xc, 0, 0])};  mult = 4;
else
    r2 = fullrod(D, L, h, op);
    r3 = halfrod(D, L3, h, 'axial', op);                        % x >= 0 half of a rod along x
    parts = {shift(r2, [xc, 0, 0]), shift(r3, [0, Y3, 0])};  mult = 2;
end
np_ = numel(parts);  cl = num2cell(1:np_);
p = comparticlemirror({epsconst(n^2), gold}, parts, repmat([2, 1], np_, 1), cl{:}, op);
pt = compoint(p, [0 0 0], op);
dip = dipole(pt, [1 0 0], op);
bem = bemsolver(p, op);
nf = sum(cellfun(@(q) size(q.faces, 1), parts));
M = zeros(numel(lam), 5);
for il = 1:numel(lam)
    [tot, rad] = dip.decayrate(bem \ dip(p, lam(il)));
    M(il, :) = [lam(il), tot(1), rad(1), nf, mult * nf];
    fprintf('%s lambda %g: Fp %.2f T %.2f (faces %d, full %d)\n', spec, lam(il), tot(1), rad(1), nf, mult * nf);
end
bemx_csv(fullfile(outdir, ['meshsym_' spec '.csv']), 'lambda_nm,Fp_x,T_x,faces_meshed,faces_full', M, ...
    sprintf('%s: mirror symmetry %s, h=%g, n=%.2f', spec, sym, h, n));
end


function p = fullrod(D, L, h, op)
%  rod along x centred at the origin (as bemx_rod, rotated)
[p, ~] = bemx_rod(D, L, h, op);  p = rot(p, 90, [0, 1, 0]);
end


function p = halfrod(D, L, h, how, op)
%  half of a capsule rod (axis along x, centre at the origin), cut exactly on a mirror plane:
%    'side'  : y >= 0 half (cut along the axis)        'axial' : x >= 0 half (cut through the middle)
%  built along z as in MNPBEM's trirod and rotated by 90 deg about y (z -> x, y unchanged)
nphi = ceil(pi * D / h);  nth = 2 * ceil(pi * D / (4 * h));  nz = ceil((L - D) / h) + 1;
theta = linspace(0, 0.5 * pi, nth);
if strcmp(how, 'side')
    phi = linspace(0, pi, ceil(nphi / 2) + 1);                   % original y = sin(phi) >= 0
    z = 0.5 * linspace(-1, 1, nz) * (L - D);
    cap1 = shift(trispheresegment(phi, theta, D, op), [0, 0, 0.5 * (L - D)]);
    caps = [cap1; flip(cap1, 3)];
else
    phi = linspace(0, 2 * pi, nphi);
    z = linspace(0, 0.5 * (L - D), ceil(nz / 2));                 % z >= 0 only (x >= 0 after rotation)
    caps = shift(trispheresegment(phi, theta, D, op), [0, 0, 0.5 * (L - D)]);
end
[verts, faces] = fvgrid(phi, z, op);
cyl = particle([0.5 * D * cos(verts(:, 1)), 0.5 * D * sin(verts(:, 1)), verts(:, 2)], faces, op);
p = clean([caps; cyl]);
p = rot(p, 90, [0, 1, 0]);
v = p.verts;  tol = 1e-6;
if strcmp(how, 'side') && min(v(:, 2)) < -tol, error('halfrod: vertices below y = 0'); end
if strcmp(how, 'axial') && min(v(:, 1)) < -tol, error('halfrod: vertices below x = 0'); end
end
