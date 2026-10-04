function job_excitation(spec, outdir)
%  JOB_EXCITATION - local-field (excitation-rate) enhancement |E|^2/|E0|^2 at the emitter positions for
%    plane-wave illumination polarised along the rod axis (z, incidence along x) and across it (x, incidence along z).
op = bemoptions('sim', 'ret', 'interp', 'curv');
epstab = {epsconst(1), epstable('gold.dat')};
if strcmp(spec, 'rod'), [p0, ztop] = bemx_rod(20, 60, 2, op); else, p0 = trisphere(784, 2 * 15.874); ztop = 15.874; end
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [3 5 7 10 15 20];  ng = numel(gaps);
exc = planewave([0 0 1; 1 0 0], [1 0 0; 0 0 -1], op);
bem = bemsolver(p, op);
emesh = meshfield(p, zeros(ng, 1), zeros(ng, 1), ztop + gaps(:), op, 'nmax', 2000);
lam = 400:5:900;  M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    sig = bem \ exc(p, lam(il));
    e = emesh(sig) + emesh(exc.field(emesh.pt, lam(il)));    % [ng, 3, 2]
    row = lam(il);
    for g = 1:ng
        row = [row, abs(e(g, 3, 1))^2, sum(abs(e(g, :, 1)).^2), abs(e(g, 1, 2))^2, sum(abs(e(g, :, 2)).^2)]; %#ok<AGROW>
    end
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Ez2_polz_g%g,E2_polz_g%g,Ex2_polx_g%g,E2_polx_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['excitation_' spec '.csv']), hdr, M, sprintf('%s; |E|^2/|E0|^2 on the axis above the apex; faces=%d', spec, p.n));
