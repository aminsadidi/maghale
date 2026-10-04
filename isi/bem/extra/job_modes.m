function job_modes(spec, outdir)
%  JOB_MODES - quasistatic plasmon-eigenmode decomposition of the decay rate (MNPBEM bemstateig).
%    Gamma_tot/Gamma_0 - 1 = sum_k Im[...] / (Lambda(omega) + lambda_k): the contribution of the longitudinal
%    (and transverse) dipolar mode is computed exactly; the remainder (full - dipolar) is the non-resonant
%    "background" made of the high-order modes (lossy-surface / quenching channel).
%    spec : 'rodL60' (any L), 'sphere'
op = bemoptions('sim', 'stat', 'interp', 'curv');
epstab = {epsconst(1), epstable('gold.dat')};
if strncmp(spec, 'rod', 3)
    L = sscanf(spec, 'rodL%d');  [p0, ztop] = bemx_rod(20, L, 2, op);
else
    p0 = trisphere(784, 2 * 15.874);  ztop = 15.874;
end
p = comparticle(epstab, {p0}, [2, 1], 1, op);
gaps = [3 4 5 6 7 8 10 12 15 20 25 30];  ng = numel(gaps);
pt = compoint(p, [zeros(ng, 2), ztop + gaps(:)], op);
dip = dipole(pt, [0 0 1; 1 0 0], op);
bem = bemsolver(p, op);
nev = 40;
bemE = bemstateig(p, op, 'nev', nev);
ur = bemE.ur;  ul = bemE.ul;  ene = diag(bemE.ene);
%  oscillator strengths for uniform fields along z and x (scale-invariant): s = (dipole moment of ur_k) * (ul_k . n)
d = (bsxfun(@times, p.pos, p.area)).' * ur;            % 3 x nev
sz = d(3, :) .* (ul * p.nvec(:, 3)).';
sx = d(1, :) .* (ul * p.nvec(:, 1)).';
[~, kL] = max(abs(sz));  [~, kT] = max(abs(sx));
fprintf('%s: %d faces; longitudinal mode k=%d (ene %.4f), transverse k=%d (ene %.4f)\n', spec, p.n, kL, real(ene(kL)), kT, real(ene(kT)));
bemx_csv(fullfile(outdir, ['modes_info_' spec '.csv']), 'k,ene_re,ene_im,s_z,s_x', ...
         [(1:nev).', real(ene), imag(ene), real(sz(:)), real(sx(:))], sprintf('%s faces=%d kL=%d kT=%d', spec, p.n, kL, kT));
lam = 450:5:950;  M = [];
for il = 1:numel(lam)
    enei = lam(il);
    exc = dip(p, enei);
    sig = bem \ exc;
    tot = decayrate(dip, sig);                            % [ng, 2]
    epsin = epstab{2}(enei);  epsout = epstab{1}(enei);
    Lam = 2 * pi * (epsin + epsout) / (epsin - epsout);
    phip = reshape(exc.phip, p.n, []);
    part = zeros(ng, 2, 3);                              % modes: L, T, all nev
    sets = {kL, kT, 1:nev};
    for q = 1:3
        sk = zeros(p.n, size(phip, 2));
        for k = sets{q}
            sk = sk - ur(:, k) * ((ul(k, :) * phip) / (Lam + ene(k)));
        end
        tk = decayrate(dip, compstruct(p, enei, 'sig', reshape(sk, size(exc.phip))));
        part(:, :, q) = tk - 1;
    end
    for ig = 1:ng
        M(end + 1, :) = [enei, gaps(ig), tot(ig, 1), tot(ig, 2), squeeze(part(ig, 1, :)).', squeeze(part(ig, 2, :)).']; %#ok<AGROW>
    end
end
bemx_csv(fullfile(outdir, ['modes_' spec '.csv']), ...
    'lambda_nm,gap,Fp_z,Fp_x,dFz_L,dFz_T,dFz_all,dFx_L,dFx_T,dFx_all', M, ...
    sprintf('%s quasistatic MNPBEM; dF = contribution of mode(s) to Fp-1; L,T = dipolar modes; all = %d lowest modes', spec, nev));
