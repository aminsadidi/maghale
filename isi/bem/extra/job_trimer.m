function job_trimer(spec, outdir)
%  JOB_TRIMER - quantum emitter in the gap of a gold-nanorod trimer for 1550 nm (supervisor's model M4), host n = 1.5.
%  Rods are capsules (D = 60 nm) in the plane z = 0:
%    R1: centre (-170,0,0), L = 300, along x       R2: centre (170,0,0), L = 300, along x   (gap g12 = 40 nm)
%    R3: centre (0,160,0), L = 240, rotated by theta3 about z (35 deg baseline)
%  spec : 'single' (R1 only), 'dimer' (R1 + R2), 'trimer' (R1 + R2 + R3 at 35 deg), 'tri90' (R3 at 90 deg, T shape),
%         followed by the wavelength chunk '_cK' (K = 1..8) of 1000:20:2200 nm (8 wavelengths per chunk).
%  Emitter positions: gap centre (0,0,0); 5 nm toward R2 (5,0,0); 10 nm toward R3 (0,10,0). Dipoles x, y, z.
%  Output per wavelength and position/dipole:
%    Fp, T            total and radiative rate in units of the rate in the host (MNPBEM decayrate)
%    ReG, ImG         reflected (scattered) Green function at the emitter, G = d* . E_ind(r0) / (0.5 nb 4/3 k0^3),
%                     normalised such that Fp = 1 + ImG and the photonic Lamb shift is dw / Gamma_0 = -ReG / 2
%    f_*              fraction of the radiated power in cones: +z NA 1.3 and NA 0.9 (objective in n = 1.5), and
%                     60 deg cones around +y (towards R3) and -y
%  Plane-wave extinction (normal incidence along z) for x and y polarisation.
n = 1.5;  D = 60;
cpos = strfind(spec, '_c');  chunk = str2double(spec(cpos(end) + 2:end));  geo = spec(1:cpos(end) - 1);
lall = 1000:20:2200;  nper = 8;  lam = lall((chunk - 1) * nper + 1:min(chunk * nper, numel(lall)));
pinf = trisphere(1444, 2);
op = bemoptions('sim', 'ret', 'interp', 'curv', 'pinfty', pinf);
gold = epstable('gold.dat');
rods = {};
[r, ~] = bemx_rod(D, 300, 5, op);  r = rot(r, 90, [0, 1, 0]);            % axis along x, finer mesh (5 nm) near the gap
rods{end + 1} = shift(r, [-170, 0, 0]);
if ~strcmp(geo, 'single'), rods{end + 1} = shift(r, [170, 0, 0]); end
if any(strcmp(geo, {'trimer', 'tri90'}))
    th = 35;  if strcmp(geo, 'tri90'), th = 90; end
    [r3, ~] = bemx_rod(D, 240, 7, op);  r3 = rot(r3, 90, [0, 1, 0]);  r3 = rot(r3, th, [0, 0, 1]);
    [~, i] = max(r3.verts(:, 1));                                            % the end with the largest x must point to +y
    if th < 90 && r3.verts(i, 2) < 0, r3 = rot(r3, -2 * th, [0, 0, 1]); end
    rods{end + 1} = shift(r3, [0, 160, 0]);
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
bemx_csv(fullfile(outdir, ['trimer_' spec '.csv']), hdr, M, sprintf('%s: rods D=%g, n=%.2f, faces=%d, pinfty 1444', ...
    spec, D, n, p.n));
