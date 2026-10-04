function job_collection(spec, outdir)
%  JOB_COLLECTION - fraction of the radiated power collected by an objective (cone of half-angle asin(NA/n)).
%    spec 'free'  : rod in air, axis z; dipole on the axis along z (axial) or x; cones around +z (rod along the
%                   optical axis) and around +x (rod lying in the focal plane, viewed from the side).
%    spec 'glass' : rod lying on glass (n = 1.52) along x, 1 nm above it; dipole beyond the tip along x, y, z;
%                   cones around +z in air (dry objective) and around -z in the glass (oil objective).
%  The far field is sampled on a fine unit sphere; per-direction power from MNPBEM's scattering().
gaps = [5 10 20];  ng = numel(gaps);  lam = 500:10:900;
pinf = trisphere(1444, 2);
if strcmp(spec, 'free')
    op = bemoptions('sim', 'ret', 'interp', 'curv', 'pinfty', pinf);
    epstab = {epsconst(1), epstable('gold.dat')};
    [p0, ztop] = bemx_rod(20, 60, 2, op);
    p = comparticle(epstab, {p0}, [2, 1], 1, op);
    pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
    dirs = [0 0 1; 1 0 0];  dn = {'z', 'x'};
    cones = {'up_NA0.5', [0 0 1], asin(0.5);  'up_NA0.9', [0 0 1], asin(0.9);
             'side_NA0.9', [1 0 0], asin(0.9); 'side_NA0.5', [1 0 0], asin(0.5)};
else
    epstab = {epsconst(1), epstable('gold.dat'), epsconst(1.52^2)};
    layer = layerstructure(epstab, [1, 3], 0, layerstructure.options);
    op = bemoptions('sim', 'ret', 'interp', 'curv', 'layer', layer, 'pinfty', pinf);
    [p0, ~] = bemx_rod(20, 60, 2, op);
    p0 = rot(p0, 90, [0, 1, 0]);
    p0 = shift(p0, [0, 0, 1 - min(p0.verts(:, 3))]);
    xtip = max(p0.verts(:, 1));  zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
    p = comparticle(epstab, {p0}, [2, 1], 1, op);
    pt = compoint(p, [xtip + gaps(:), zeros(ng, 1), zc + zeros(ng, 1)], op);
    tab = tabspace(layer, p, pt);
    greentab = compgreentablayer(layer, tab);
    greentab = set(greentab, linspace(480, 920, 23), op);
    op.greentab = greentab;
    dirs = [1 0 0; 0 1 0; 0 0 1];  dn = {'x', 'y', 'z'};
    cones = {'air_NA0.9', [0 0 1], asin(0.9);  'air_hemisphere', [0 0 1], pi / 2;
             'glass_NA1.3', [0 0 -1], asin(1.3 / 1.52);  'glass_NA1.45', [0 0 -1], asin(1.45 / 1.52);
             'glass_hemisphere', [0 0 -1], pi / 2};
end
dip = dipole(pt, dirs, op);
bem = bemsolver(p, op);
nd = size(dirs, 1);  nc = size(cones, 1);
M = zeros(numel(lam), 1 + ng * nd * (1 + nc));
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    f = farfield(dip.spec, sig) + farfield(dip, dip.spec, lam(il));   % induced + direct (and reflected) far field
    [~, dsca] = scattering(f);                       % power per unit solid angle on pinfty: [nface, npos, ndip]
    w = bsxfun(@times, dsca.dsca, pinf.area(:));     % power per face
    tot = squeeze(sum(w, 1));                        % [npos, ndip]
    row = lam(il);
    for g = 1:ng
        for k = 1:nd
            row = [row, tot(g, k)]; %#ok<AGROW>
            for c = 1:nc
                in = pinf.nvec * cones{c, 2}(:) >= cos(cones{c, 3}) - 1e-9;
                row = [row, sum(w(in, g, k)) / tot(g, k)]; %#ok<AGROW>
            end
        end
    end
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, for k = 1:nd
    hdr = [hdr, sprintf(',Prad_%s_g%g', dn{k}, g)]; %#ok<AGROW>
    for c = 1:nc, hdr = [hdr, sprintf(',f_%s_%s_g%g', cones{c, 1}, dn{k}, g)]; end %#ok<AGROW>
end, end
bemx_csv(fullfile(outdir, ['collection_' spec '.csv']), hdr, M, ...
    sprintf('collection fractions, spec=%s, pinfty 1444 vertices, faces=%d', spec, p.n));
