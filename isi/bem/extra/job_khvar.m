function job_khvar(spec, outdir)
%  JOB_KHVAR - variants of the comparison with Khatua et al. (2014) that test the origin of the broader dependence on
%  the resonance wavelength in the experiment:
%    'L47_surf' : homogeneous glycerol (n = 1.47), Johnson-Christy gold with surface (Kreibig) damping (gold_surf.dat)
%    'L47_sub'  : rod lying on glass (n = 1.52) 1 nm above it, covered by glycerol (n = 1.47); axis along x,
%                 dipole beyond the tip on the axis and parallel to it; excitation through the glass at normal
%                 incidence, polarised along the rod.
%  Rates are in units of the rate in bulk glycerol; E_exc = |E_x|^2 relative to the same position without the rod.
t = regexp(spec, 'L(\d+)_(\w+)', 'tokens', 'once');  L = str2double(t{1});  var = t{2};  D = 25;  nb = 1.47;
here = fileparts(mfilename('fullpath'));
gaps = [3 5 7 10];  ng = numel(gaps);  lam = 550:5:760;  wl = [594 633];
switch var
  case 'surf'
    epstab = {epsconst(nb^2), epstable(fullfile(here, 'gold_surf.dat'))};
    op = bemoptions('sim', 'ret', 'interp', 'curv');
    [p0, ztop] = bemx_rod(D, L, 2, op);
    p = comparticle(epstab, {p0}, [2, 1], 1, op);
    pos = [zeros(ng, 2), ztop + gaps(:)];  pt = compoint(p, pos, op);
    dip = dipole(pt, [0 0 1], op);  exc = planewave([0 0 1], [1 0 0], op);  ax = 3;
  case 'sub'
    epstab = {epsconst(nb^2), epstable('gold.dat'), epsconst(1.52^2)};
    layer = layerstructure(epstab, [1, 3], 0, layerstructure.options);
    op = bemoptions('sim', 'ret', 'interp', 'curv', 'layer', layer);
    [p0, ~] = bemx_rod(D, L, 2, op);
    p0 = rot(p0, 90, [0, 1, 0]);
    p0 = shift(p0, [0, 0, 1 - min(p0.verts(:, 3))]);
    xtip = max(p0.verts(:, 1));  zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
    p = comparticle(epstab, {p0}, [2, 1], 1, op);
    pos = [xtip + gaps(:), zeros(ng, 1), zc + zeros(ng, 1)];  pt = compoint(p, pos, op);
    tab = tabspace(layer, p, pt);
    greentab = compgreentablayer(layer, tab);
    greentab = set(greentab, linspace(540, 770, 12), op);
    op.greentab = greentab;
    dip = dipole(pt, [1 0 0], op);  exc = planewave([1 0 0], [0 0 1], op);  ax = 1;
  otherwise, error('unknown variant %s', var);
end
bem = bemsolver(p, op);
emesh = meshfield(p, pos(:, 1), pos(:, 2), pos(:, 3), op, 'nmax', 2000);
M = zeros(numel(lam), 1 + 3 * ng);
for il = 1:numel(lam)
    [tot, rad] = decayrate(dip, bem \ dip(p, lam(il)));
    if strcmp(var, 'sub'), tot = tot / nb; rad = rad / nb; end      % layer rates are in vacuum units
    sw = bem \ exc(p, lam(il));
    Ei = emesh(exc.field(emesh.pt, lam(il)));  e = emesh(sw) + Ei;
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), abs(e(g, ax, 1))^2 / abs(Ei(g, ax, 1))^2]; end %#ok<AGROW>
    M(il, :) = row;
end
X = zeros(2, ng);
for iw = 1:2
    sw = bem \ exc(p, wl(iw));  Ei = emesh(exc.field(emesh.pt, wl(iw)));  e = emesh(sw) + Ei;
    X(iw, :) = abs(e(:, ax, 1)).^2 ./ abs(Ei(:, ax, 1)).^2;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_g%g,T_g%g,Ez2_g%g', g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['khvar_' spec '.csv']), hdr, M, sprintf('Khatua variant %s: D=%d L=%d, faces=%d; Ez2 at 594 nm: %s; at 633 nm: %s', ...
    var, D, L, p.n, sprintf('%.4g ', X(1, :)), sprintf('%.4g ', X(2, :))));
