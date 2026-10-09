function job_lu(spec, outdir)
%  JOB_LU - comparison with Lu et al., ACS Photonics 7, 2498 (2020): NDI-2TEG-3T (q0 = 1.3e-4, emission maximum
%  ~730 nm) near gold nanorods (D = 25 nm) in toluene (n = 1.496), excitation at 671 nm. Dipole on the axis and
%  parallel to it: Fp, T over 600-860 nm, extinction (SPR), |E_z|^2/|E_0|^2 at 671 nm for a plane wave polarised
%  along the rod.   spec : 'L50', ...
L = sscanf(spec, 'L%d');  D = 25;  nb = 1.496;
op = bemoptions('sim', 'ret', 'interp', 'curv');
[p0, ztop] = bemx_rod(D, L, 2, op);
p = comparticle({epsconst(nb^2), epstable('gold.dat')}, {p0}, [2, 1], 1, op);
gaps = [1.5 2 3 5];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1], op);
exc = planewave([0 0 1], [1 0 0], op);
bem = bemsolver(p, op);
emesh = meshfield(p, zeros(ng, 1), zeros(ng, 1), ztop + gaps(:), op, 'nmax', 2000);
lam = 600:5:860;  M = zeros(numel(lam), 2 + 3 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    sw = bem \ exc(p, lam(il));
    e = emesh(sw) + emesh(exc.field(emesh.pt, lam(il)));
    row = [lam(il), exc.ext(sw)];
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), abs(e(g, 3, 1))^2]; end %#ok<AGROW>
    M(il, :) = row;
end
sw = bem \ exc(p, 671);  e = emesh(sw) + emesh(exc.field(emesh.pt, 671));  X = abs(e(:, 3, 1)).^2;
hdr = 'lambda_nm,ext_nm2';
for g = gaps, hdr = [hdr, sprintf(',Fp_g%g,T_g%g,Ez2_g%g', g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['lu_' spec '.csv']), hdr, M, sprintf('Lu comparison: rod D=%d L=%d in n=%.3f, faces=%d; Ez2 at 671 nm: %s', ...
    D, L, nb, p.n, sprintf('%.4g ', X)));
