function job_telecom(spec, outdir)
%  JOB_TELECOM - gold nanorods (D = 20 nm) embedded in glass/polymer (n = 1.45) with longitudinal resonances from
%  the visible to the telecom O and C bands. Dipole on the axis, gaps 5, 10, 20 nm, axial (z) and transverse (x);
%  extinction for a plane wave polarised along the rod, and |E_z|^2/|E_0|^2 at the dipole positions.
%    spec : 'L60', 'L80', ... (D = 20 nm) or 'D40L300' (other diameters)
t = sscanf(spec, 'D%dL%d');  if numel(t) == 2, D = t(1); L = t(2); else, L = sscanf(spec, 'L%d'); D = 20; end
nb = 1.45;
op = bemoptions('sim', 'ret', 'interp', 'curv');
h = 2;  if L > 120, h = 2.5; end;  if D > 20, h = max(h, D / 10); end
[p0, ztop] = bemx_rod(D, L, h, op);
p = comparticle({epsconst(nb^2), epstable('gold.dat')}, {p0}, [2, 1], 1, op);
gaps = [5 10 20];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
exc = planewave([0 0 1], [1 0 0], op);
emesh = meshfield(p, zeros(ng, 1), zeros(ng, 1), ztop + gaps(:), op, 'nmax', 2000);
bem = bemsolver(p, op);
lam = 600:10:1800;  M = zeros(numel(lam), 2 + 5 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    sw = bem \ exc(p, lam(il));
    e = emesh(sw) + emesh(exc.field(emesh.pt, lam(il)));
    row = [lam(il), exc.ext(sw)];
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2), abs(e(g, 3, 1))^2]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm,ext_nm2';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g,Ez2_g%g', g, g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['telecom_' spec '.csv']), hdr, M, sprintf('rod D=%d L=%d in n=%.2f h=%g faces=%d', D, L, nb, h, p.n));
