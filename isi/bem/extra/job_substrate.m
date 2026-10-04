function job_substrate(spec, outdir)
%  JOB_SUBSTRATE - rod lying on a glass substrate (n = 1.52), 1 nm above it, emitter beyond the tip on the rod axis
%    (height = rod centre). Rates with the rod (tot, rad) and for the same dipole on bare glass (tot0, rad0),
%    all in units of the free-space (vacuum) rate.
epstab = {epsconst(1), epstable('gold.dat'), epsconst(1.52^2)};
layer = layerstructure(epstab, [1, 3], 0, layerstructure.options);
op = bemoptions('sim', 'ret', 'interp', 'curv', 'layer', layer);
D = 20;  L = 60;
[p0, ~] = bemx_rod(D, L, 2, op);
p0 = rot(p0, 90, [0, 1, 0]);
p0 = shift(p0, [0, 0, 1 - min(p0.verts(:, 3))]);           % 1 nm above the glass
xtip = max(p0.verts(:, 1));  zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [5 10 20];  ng = numel(gaps);
pt = compoint(p, [xtip + gaps(:), zeros(ng, 1), zc + zeros(ng, 1)], op);
lam = 500:5:900;
tab = tabspace(layer, p, pt);
greentab = compgreentablayer(layer, tab);
greentab = set(greentab, linspace(480, 920, 23), op);
op.greentab = greentab;
dip = dipole(pt, [1 0 0; 0 1 0; 0 0 1], op);                % axial, in-plane transverse, normal to substrate
bem = bemsolver(p, op);
M = zeros(numel(lam), 1 + 12 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    [tot0, rad0] = decayrate0(dip, lam(il));
    row = lam(il);
    for g = 1:ng
        for k = 1:3, row = [row, tot(g, k), rad(g, k), tot0(g, k), rad0(g, k)]; end %#ok<AGROW>
    end
    M(il, :) = row;
end
hdr = 'lambda_nm';  nm = 'xyz';
for g = gaps, for k = 1:3, hdr = [hdr, sprintf(',tot_%s_g%g,rad_%s_g%g,tot0_%s_g%g,rad0_%s_g%g', nm(k), g, nm(k), g, nm(k), g, nm(k), g)]; end, end %#ok<AGROW>
bemx_csv(fullfile(outdir, 'substrate_glass.csv'), hdr, M, sprintf('rod L60 D20 on glass n=1.52, 1 nm gap; axis along x; faces=%d; dipole height %.2f nm', p.n, zc));
