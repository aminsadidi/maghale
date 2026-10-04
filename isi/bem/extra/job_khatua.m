function job_khatua(spec, outdir)
%  JOB_KHATUA - comparison with the single-molecule experiment of Khatua et al., ACS Nano 8, 4440 (2014):
%    crystal violet (q0 = 0.0228, emission maximum 640 nm) near gold nanorods of diameter 25 nm and lengths
%    39-70 nm in glycerol on glass (modelled as a homogeneous medium n = 1.47), excitation at 594 and 633 nm.
%    For a dipole on the rod axis at gap d from the tip, oriented along the axis (as in their calculations):
%      Fp, T (emission side) over 550-760 nm, extinction spectrum (SPR), and the local intensity |E_z|^2/|E_0|^2
%      for a plane wave polarised along the axis (excitation side).
%    spec : 'L39', 'L43', ...
L = sscanf(spec, 'L%d');  D = 25;  nb = 1.47;
op = bemoptions('sim', 'ret', 'interp', 'curv');
epstab = {epsconst(nb^2), epstable('gold.dat')};
[p0, ztop] = bemx_rod(D, L, 2, op);
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [3 5 7 10];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1], op);
exc = planewave([0 0 1], [1 0 0], op);
bem = bemsolver(p, op);
emesh = meshfield(p, zeros(ng, 1), zeros(ng, 1), ztop + gaps(:), op, 'nmax', 2000);
lam = 550:5:760;  M = zeros(numel(lam), 2 + 3 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    sw = bem \ exc(p, lam(il));
    ext = exc.ext(sw);
    e = emesh(sw) + emesh(exc.field(emesh.pt, lam(il)));
    row = [lam(il), ext];
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), abs(e(g, 3, 1))^2]; end %#ok<AGROW>
    M(il, :) = row;
end
%  excitation at the two laser lines
X = zeros(2, ng);
for iw = 1:2
    w = [594 633];  sw = bem \ exc(p, w(iw));
    e = emesh(sw) + emesh(exc.field(emesh.pt, w(iw)));
    X(iw, :) = abs(e(:, 3, 1)).^2;
end
hdr = 'lambda_nm,ext_nm2';
for g = gaps, hdr = [hdr, sprintf(',Fp_g%g,T_g%g,Ez2_g%g', g, g, g)]; end %#ok<AGROW>
meta = sprintf('Khatua comparison: rod D=%d L=%d in n=%.2f, faces=%d; Ez2 at 594 nm: %s; at 633 nm: %s', D, L, nb, p.n, ...
               sprintf('%.4g ', X(1, :)), sprintf('%.4g ', X(2, :)));
bemx_csv(fullfile(outdir, ['khatua_' spec '.csv']), hdr, M, meta);
