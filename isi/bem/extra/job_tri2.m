function job_tri2(spec, outdir)
%  JOB_TRI2 - parametrised version of job_trimer (model M4, host n = 1.5, rods D = 60 nm in the plane z = 0, gap 40 nm).
%  spec: tokens separated by '_':
%    L<nm>   length of R1 and R2 (default 300); centres at -/+(20 + L/2) on the x axis
%    R<nm>   length of R3 (no R token: no R3);  A<deg> angle of R3 (default 35);  X<nm>, Y<nm> centre of R3 (0, 160)
%    S       single rod (R1 only);  H<nm> mesh size of R1/R2 (default 5; R3 uses 1.4 H)
%    M       mesh-test wavelengths 1310, 1480, 1550, 1660 nm;  otherwise c<K> = chunk K of 1100:20:1900 nm (7 per chunk)
%  e.g. 'L270_c3' (dimer), 'L270_R300_A35_Y160_c2' (trimer), 'S_L300_H3_M' (single rod, 3 nm mesh)
%  Output columns as in job_trimer.
n = 1.5;  D = 60;  L = 300;  L3 = 0;  A = 35;  X3 = 0;  Y3 = 160;  single = false;  h = 5;  mtest = false;  chunk = 0;
tok = strsplit(spec, '_');
for k = 1:numel(tok)
    t = tok{k};  v = str2double(t(2:end));
    switch t(1)
        case 'L', L = v;   case 'R', L3 = v;  case 'A', A = v;  case 'X', X3 = v;  case 'Y', Y3 = v;
        case 'S', single = true;  case 'H', h = v;  case 'M', mtest = true;  case 'c', chunk = v;
        otherwise, error('job_tri2: unknown token %s', t);
    end
end
if mtest, lam = [1310 1480 1550 1660];
else, lall = 1100:20:1900;  nper = 7;  lam = lall((chunk - 1) * nper + 1:min(chunk * nper, numel(lall))); end
pinf = trisphere(1444, 2);
op = bemoptions('sim', 'ret', 'interp', 'curv', 'pinfty', pinf);
gtab = 'gold.dat';  if max(lam) > 1937, gtab = fullfile(fileparts(mfilename('fullpath')), 'gold_jcx.dat'); end
gold = epstable(gtab);
[r, ~] = bemx_rod(D, L, h, op);  r = rot(r, 90, [0, 1, 0]);
xc = 20 + L / 2;  rods = {shift(r, [-xc, 0, 0])};
if ~single, rods{end + 1} = shift(r, [xc, 0, 0]); end
if L3 > 0
    [r3, ~] = bemx_rod(D, L3, 1.4 * h, op);  r3 = rot(r3, 90, [0, 1, 0]);  r3 = rot(r3, A, [0, 0, 1]);
    [~, i] = max(r3.verts(:, 1));
    if A < 90 && r3.verts(i, 2) < 0, r3 = rot(r3, -2 * A, [0, 0, 1]); end
    r3 = shift(r3, [X3, Y3, 0]);
    for k = 1:numel(rods)                                                     % surface separation must stay >= 8 nm
        dv = permute(r3.verts, [1 3 2]) - permute(rods{k}.verts, [3 1 2]);  dmin = sqrt(min(sum(dv.^2, 3), [], 'all'));
        if dmin < 8, error('job_tri2: R3 is %.1f nm from rod %d', dmin, k); end
    end
    rods{end + 1} = r3;
end
nr = numel(rods);
cl = num2cell(1:nr);
p = comparticle({epsconst(n^2), gold}, rods, repmat([2, 1], nr, 1), cl{:}, op);
pos = [0 0 0; 5 0 0; 0 10 0];  plab = {'c', 'px5', 'py10'};  np = size(pos, 1);
pt = compoint(p, pos, op);
if pt.n ~= np, error('compoint lost points (%d of %d)', pt.n, np); end
dirs = eye(3);  dlab = {'x', 'y', 'z'};  nd = 3;
dip = dipole(pt, dirs, op);
exc = planewave([1 0 0; 0 1 0], [0 0 1; 0 0 1], op);
bem = bemsolver(p, op);
g = compgreenret(pt, p, op);
cones = {'zNA1.3', [0 0 1], asin(1.3 / n);  'zNA0.9', [0 0 1], asin(0.9 / n);
         'py60', [0 1 0], pi / 3;  'my60', [0 -1 0], pi / 3};  nc = size(cones, 1);
M = zeros(numel(lam), 3 + np * nd * (4 + nc));
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    e = field(g, sig);  e = e.e;                                             % [npt, 3, npos, ndip]
    k0 = 2 * pi / lam(il);  nb = n;  gam = 4 / 3 * k0^3;
    f = farfield(dip.spec, sig) + farfield(dip, dip.spec, lam(il));
    [~, dsca] = scattering(f);  w = bsxfun(@times, dsca.dsca, pinf.area(:));
    ptot = squeeze(sum(w, 1));
    ext = exc.ext(bem \ exc(p, lam(il)));
    row = [lam(il), ext(1), ext(2)];
    for ip = 1:np
        for k = 1:nd
            G = (squeeze(e(ip, :, ip, k)) * dirs(k, :)') / (0.5 * nb * gam);
            row = [row, tot(ip, k), rad(ip, k), real(G), imag(G)]; %#ok<AGROW>
            for c = 1:nc
                in = pinf.nvec * cones{c, 2}(:) >= cos(cones{c, 3}) - 1e-9;
                row = [row, sum(w(in, ip, k)) / ptot(ip, k)]; %#ok<AGROW>
            end
        end
    end
    M(il, :) = row;
    fprintf('%s lambda %g done\n', spec, lam(il));
end
hdr = 'lambda_nm,ext_x,ext_y';
for ip = 1:np, for k = 1:nd
    s = [dlab{k} '_' plab{ip}];
    hdr = [hdr, sprintf(',Fp_%s,T_%s,ReG_%s,ImG_%s', s, s, s, s)]; %#ok<AGROW>
    for c = 1:nc, hdr = [hdr, sprintf(',f_%s_%s', cones{c, 1}, s)]; end %#ok<AGROW>
end, end
bemx_csv(fullfile(outdir, ['tri2_' spec '.csv']), hdr, M, sprintf('%s: L=%g L3=%g A=%g X3=%g Y3=%g h=%g D=%g n=%.2f faces=%d pinfty 1444 %s', ...
    spec, L, L3, A, X3, Y3, h, D, n, p.n, gtab));
