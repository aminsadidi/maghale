function job_absorption(spec, outdir)
%  JOB_ABSORPTION - absorption and scattering cross-sections (nm^2) of the 60 x 20 nm gold rod and the equal-volume
%  sphere for plane waves polarised along (z) and across (x) the rod; used for the gold-photoluminescence background.
op = bemoptions('sim', 'ret', 'interp', 'curv');
switch spec
    case 'rod',    [p0, ~] = bemx_rod(20, 60, 2, op);
    case 'sphere', p0 = trisphere(784, 2 * 15.874);
    otherwise, error('unknown spec %s', spec);
end
p = comparticle({epsconst(1), epstable('gold.dat')}, {p0}, [2, 1], 1, op);
bem = bemsolver(p, op);
exc = planewave([0 0 1; 1 0 0], [1 0 0; 0 0 1], op);
lam = 400:5:900;
M = zeros(numel(lam), 5);
for il = 1:numel(lam)
    sig = bem \ exc(p, lam(il));
    a = exc.abs(sig);  s = exc.sca(sig);
    M(il, :) = [lam(il), a(1), s(1), a(2), s(2)];
end
bemx_csv(fullfile(outdir, ['absorption_' spec '.csv']), 'lambda_nm,abs_z,sca_z,abs_x,sca_x', M, sprintf('%s faces=%d', spec, p.n));
