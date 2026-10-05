function job_recip(spec, outdir)
%  JOB_RECIP - angular emission of the dipole near the rod on glass by RECIPROCITY: the power emitted into direction s
%    (medium j) is dP/dOmega = n_j sum_pol |p . E_loc(s, pol)|^2, where E_loc is the field at the dipole position of a
%    unit-amplitude plane wave incident from s (propagating along -s) with polarisation pol. Plane waves from the upper
%    (air) and lower (glass) half-space are standard MNPBEM layer excitations; no layer far field is needed.
%    Normalisation: a free dipole gives 8*pi/3, so sum(dP)/(8*pi/3) is the radiative rate in units of the vacuum rate.
%    'bare' columns use the plane-wave field without the particle (checked against isi/analysis/glass_check.py).
%    spec : 'glass' (gold rod) or 'dielectric' (eps = 4; then the radiative rate must equal the total rate)
lam = 640;  gaps = [5 10 20];  ng = numel(gaps);
if strcmp(spec, 'dielectric'), mat = epsconst(4); else, mat = epstable('gold.dat'); end
epstab = {epsconst(1), mat, epsconst(1.52^2)};
layer = layerstructure(epstab, [1, 3], 0, layerstructure.options);
op = bemoptions('sim', 'ret', 'interp', 'curv', 'layer', layer);
[p0, ~] = bemx_rod(20, 60, 2, op);
p0 = rot(p0, 90, [0, 1, 0]);
p0 = shift(p0, [0, 0, 1 - min(p0.verts(:, 3))]);
xtip = max(p0.verts(:, 1));  zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
p = comparticle(epstab, {p0}, [2, 1], 1, op);
pos = [xtip + gaps(:), zeros(ng, 1), zc + zeros(ng, 1)];
pt = compoint(p, pos, op);
tab = tabspace(layer, p, pt);
greentab = compgreentablayer(layer, tab);
greentab = set(greentab, linspace(600, 680, 5), op);
op.greentab = greentab;
bem = bemsolver(p, op);
%  total decay rate from the dipole near field (independent check)
dip = dipole(pt, eye(3), op);
tot = decayrate(dip, bem \ dip(p, lam));
%  directions: midpoint rule in theta (from +z for air, from -z for glass) and phi
nth = 24;  nph = 36;
th = ((1:nth) - 0.5) * (pi / 2) / nth;  ph = ((1:nph) - 0.5) * 2 * pi / nph;
[T, PH] = ndgrid(th, ph);  T = T(:);  PH = PH(:);  nd1 = numel(T);
s = [[sin(T) .* cos(PH), sin(T) .* sin(PH), cos(T)]; [sin(T) .* cos(PH), sin(T) .* sin(PH), -cos(T)]];
w = repmat(sin(T) * (pi / 2 / nth) * (2 * pi / nph), 2, 1);       % solid-angle weights
nj = [ones(nd1, 1); 1.52 * ones(nd1, 1)];
kdir = -s;                                                        % propagation direction of the incident wave
e1 = cross(repmat([0 0 1], 2 * nd1, 1), kdir, 2);  e1 = bsxfun(@rdivide, e1, sqrt(sum(e1.^2, 2)));
e2 = cross(kdir, e1, 2);
pol = [e1; e2];  dirs = [kdir; kdir];                            % 2 polarisations per direction
%  MNPBEM asserts dot(pol, dir) == 0 exactly; construct with an exactly orthogonal dummy (-dy, dx, 0) and then set the
%  (numerically orthogonal, |dot| ~ 1e-16) polarisation, which init stores without further use
exc = planewave([-dirs(:, 2), dirs(:, 1), 0 * dirs(:, 3)], dirs, op);
exc.pol = pol;
sig = bem \ exc(p, lam);
emesh = meshfield(p, pos(:, 1), pos(:, 2), pos(:, 3), op, 'nmax', 4000);
Einc = emesh(exc.field(emesh.pt, lam));                          % [ng, 3, 2*ndir] incident + reflected/transmitted
Etot = emesh(sig) + Einc;
NA = {'air_NA0.9', 1:nd1, asin(0.9);  'air_hemisphere', 1:nd1, pi / 2;  'glass_NA1.3', nd1 + (1:nd1), asin(1.3 / 1.52);
      'glass_NA1.45', nd1 + (1:nd1), asin(1.45 / 1.52);  'glass_hemisphere', nd1 + (1:nd1), pi / 2};
thall = [T; T];
row = [];  hdr = '';  dn = 'xyz';
for which = 1:2
    if which == 1, E = Etot; tag = 'rod'; else, E = Einc; tag = 'bare'; end
    for g = 1:ng
        for k = 1:3
            a = squeeze(E(g, k, :));                              % p . E_loc for p along axis k
            dP = nj .* w .* (abs(a(1:2 * nd1)).^2 + abs(a(2 * nd1 + 1:end)).^2);
            Ptot = sum(dP);
            row = [row, Ptot / (8 * pi / 3), tot(g, k)]; %#ok<AGROW>
            hdr = [hdr, sprintf(',T_%s_%s_g%g,tot_%s_%s_g%g', tag, dn(k), g, tag, dn(k), g)]; %#ok<AGROW>
            for c = 1:size(NA, 1)
                m = NA{c, 2};  m = m(thall(m) <= NA{c, 3} + 1e-12);
                row = [row, sum(dP(m)) / Ptot]; %#ok<AGROW>
                hdr = [hdr, sprintf(',f_%s_%s_%s_g%g', tag, NA{c, 1}, dn(k), g)]; %#ok<AGROW>
            end
        end
    end
end
bemx_csv(fullfile(outdir, ['recip_' spec '.csv']), ['lambda_nm', hdr], [lam, row], ...
    sprintf('reciprocity, rod on glass (%s), dipole height %.3f nm, %d x %d directions per half-space, faces=%d', spec, zc, nth, nph, p.n));
