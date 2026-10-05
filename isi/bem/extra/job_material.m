function job_material(spec, outdir)
%  JOB_MATERIAL - sensitivity of the main results (60 x 20 nm rod, axial and transverse dipole) to the gold
%  permittivity: Palik (MNPBEM goldpalik.dat), Olmon and McPeak (evaporated films), Johnson-Christy with reduced
%  Drude damping (cold1, cold2: cryogenic estimates) and with surface damping (surf). Tables: make_gold_tables.py.
op = bemoptions('sim', 'ret', 'interp', 'curv');
here = fileparts(mfilename('fullpath'));
switch spec
    case 'palik', metal = 'goldpalik.dat';
    case {'olmon', 'mcpeak', 'cold1', 'cold2', 'surf'}, metal = fullfile(here, ['gold_' spec '.dat']);
    otherwise, error('unknown spec %s', spec);
end
lam = 500:4:840;
[p0, ztop] = bemx_rod(20, 60, 2, op);
p = comparticle({epsconst(1), epstable(metal)}, {p0}, [2, 1], 1, op);
gaps = [3 5 10 20];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
bem = bemsolver(p, op);
M = zeros(numel(lam), 1 + 4 * ng);
for il = 1:numel(lam)
    sig = bem \ dip(p, lam(il));
    [tot, rad] = decayrate(dip, sig);
    row = lam(il);
    for g = 1:ng, row = [row, tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm';
for g = gaps, hdr = [hdr, sprintf(',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g)]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['material_' spec '.csv']), hdr, M, sprintf('rod 60x20 h2 %s faces=%d', spec, p.n));
