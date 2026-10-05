function job_collection_glass(spec, outdir)
%  JOB_COLLECTION_GLASS - angular distribution and objective collection for the rod lying on glass (n = 1.52).
%    MNPBEM returns layer far fields on a re-ordered unit sphere (upper hemisphere first); every far-field array is
%    therefore mapped back to the original directions of PINF before the power per direction is formed, and the power
%    is computed here as dP/dOmega = 0.5 Re[ n . (E x H*) ] with H = (k/k0) n x E in the medium of that direction.
%    Checks written to the CSV: (i) the same quantities for the dipole alone above glass (compare with the analytic
%    solution in isi/analysis/glass_check.py); (ii) the integrated power versus MNPBEM's radiative decay rate.
%    spec : 'glass' (gold rod) or 'dielectric' (lossless rod, eps = 4: energy conservation, radiated power = total rate)
gaps = [5 10 20];  ng = numel(gaps);  lam = [600 610 620 630 640 650 660];
pinf = trisphere(1444, 2);
if strcmp(spec, 'dielectric'), mat = epsconst(4); else, mat = epstable('gold.dat'); end
epstab = {epsconst(1), mat, epsconst(1.52^2)};
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
greentab = set(greentab, linspace(560, 700, 15), op);
op.greentab = greentab;
dirs = [1 0 0; 0 1 0; 0 0 1];  dn = {'x', 'y', 'z'};  nd = 3;
dip = dipole(pt, dirs, op);
bem = bemsolver(p, op);
nv = pinf.nvec;  ar = pinf.area(:);  up = nv(:, 3) >= 0;
nmed = ones(size(ar));  nmed(~up) = 1.52;
cones = {'air_NA0.9', up & nv(:, 3) >= cos(asin(0.9));  'air_hemisphere', up;
         'glass_NA1.3', ~up & -nv(:, 3) >= cos(asin(1.3 / 1.52));  'glass_NA1.45', ~up & -nv(:, 3) >= cos(asin(1.45 / 1.52));
         'glass_hemisphere', ~up};
nc = size(cones, 1);
M = zeros(numel(lam), 1 + 2 * ng * nd * (3 + nc));
for il = 1:numel(lam)
    enei = lam(il);
    sig = bem \ dip(p, enei);
    [tot, rad] = decayrate(dip, sig);                     % tot from the near field (independent of the far field)
    E_ind = remap(farfield(dip.spec, sig), nv);           % field of the induced charges and currents
    E_dip = remap(farfield(dip, dip.spec, enei), nv);     % direct + reflected/transmitted dipole field
    row = enei;
    for which = 1:2
        if which == 1, E = E_ind + E_dip; else, E = E_dip; end
        %  power per direction: 0.5 Re[n.(E x H*)], H = n_med n x E  ->  0.5 n_med |E_perp|^2
        P = 0.5 * bsxfun(@times, nmed .* ar, squeeze(sum(abs(E).^2, 2)));   % [ndir, npos*ndip]
        P = reshape(P, [numel(ar), ng, nd]);
        for g = 1:ng
            for k = 1:nd
                Pt = sum(P(:, g, k));
                row = [row, Pt, rad(g, k), tot(g, k)]; %#ok<AGROW>
                for c = 1:nc, row = [row, sum(P(cones{c, 2}, g, k)) / Pt]; end %#ok<AGROW>
            end
        end
    end
    M(il, :) = row;
end
hdr = 'lambda_nm';  tag = {'rod', 'bare'};
for which = 1:2, for g = gaps, for k = 1:nd
    hdr = [hdr, sprintf(',P_%s_%s_g%g,raddecay_%s_%s_g%g,totdecay_%s_%s_g%g', tag{which}, dn{k}, g, tag{which}, dn{k}, g, tag{which}, dn{k}, g)]; %#ok<AGROW>
    for c = 1:nc, hdr = [hdr, sprintf(',f_%s_%s_%s_g%g', tag{which}, cones{c, 1}, dn{k}, g)]; end %#ok<AGROW>
end, end, end
bemx_csv(fullfile(outdir, ['collection_' spec '_v3.csv']), hdr, M, ...
    sprintf('rod on glass, far field remapped to pinfty order; dipole height %.3f nm above glass; faces=%d', zc, p.n));
end

function E = remap(f, nv)
%  far-field E of a compstruct whose (possibly re-ordered) direction set f.p is mapped onto the directions nv
fp = f.p;
try, fn = fp.nvec; catch, fn = fp.pos ./ sqrt(sum(fp.pos.^2, 2)); end
[ok, idx] = ismember(round(fn * 1e6), round(nv * 1e6), 'rows');
if ~all(ok)                                    % fall back to nearest direction
    for i = find(~ok)', [~, idx(i)] = max(fn(i, :) * nv'); end
end
E = zeros([size(nv, 1), size(f.e, 2), prod(size(f.e)) / (size(f.e, 1) * size(f.e, 2))]);
E(idx, :, :) = reshape(f.e, size(f.e, 1), size(f.e, 2), []);
E = E - bsxfun(@times, nv, sum(bsxfun(@times, nv, E), 2));   % keep the transverse part only
end
