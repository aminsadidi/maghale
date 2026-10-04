%% run_mnpbem.m  --  BEM (MNPBEM17) decay rates of a dipole near a gold nanorod / sphere
%
%  Purpose : converged Purcell factor Fp = P_tot/P_0 and radiative enhancement T = P_rad/P_0
%            for the ISI manuscript (rod L = 60 nm, D = 20 nm; equal-volume sphere R = 15.874 nm;
%            Johnson-Christy gold; dipole on the symmetry axis, axial (z) and transverse (x)).
%  Needs   : MATLAB R2016b or newer (no toolbox), MNPBEM17 toolbox (free, see README_fa.md).
%  Usage   : 1) set MODE = 'test' and run (5-20 min).  2) set MODE = 'full' and run (several hours).
%            The run can be stopped at any time (Ctrl+C) and restarted: finished wavelengths are kept.
%  Output  : folder results_bem/ next to this file (one CSV per case + log), and results_bem.zip.
%            Send results_bem.zip back.
%
%  CSV columns: lambda_nm, then for every gap g (nm):  Fp_z_g, T_z_g, Fp_x_g, T_x_g
%  (decay rates normalised to the same dipole in the homogeneous host medium).

%% ============================ SETTINGS (only these two lines may need editing) ============================
MODE       = 'test';     % 'test' first, then 'full'
MNPBEM_DIR = '';         % folder of MNPBEM17, e.g. 'C:\Users\name\Documents\MNPBEM17'  ('' = search automatically)
%% =========================================================================================================

here = fileparts(mfilename('fullpath'));
if isempty(here), here = pwd; end
setup_mnpbem(MNPBEM_DIR, here);
outdir = fullfile(here, 'results_bem');
if ~exist(outdir, 'dir'), mkdir(outdir); end
diary(fullfile(outdir, sprintf('log_%s.txt', MODE))); diary on
fprintf('\n=== run_mnpbem  mode=%s  %s ===\n', MODE, datestr(now));
fprintf('MATLAB %s | %s | cores: %d | RAM: %.1f GB\n', version, computer, num_cores(), ram_gb());

cases = define_cases(MODE);
stats = struct('name', {}, 'nfaces', {}, 'sec_per_lambda', {});
for k = 1:numel(cases)
    try
        s = run_case(cases(k), outdir);
        if ~isempty(s), stats(end+1) = s; end %#ok<SAGROW>
    catch err
        fprintf(2, '\n!!! case %s failed: %s\n', cases(k).name, err.message);
        for q = 1:min(3, numel(err.stack)), fprintf(2, '    at %s line %d\n', err.stack(q).name, err.stack(q).line); end
        fprintf(2, '    continuing with the next case.\n');
    end
end

if strcmp(MODE, 'test'), estimate_full_runtime(stats); end
zipname = fullfile(here, sprintf('results_bem_%s.zip', MODE));
zip(zipname, outdir);
fprintf('\n=== finished %s.  Send this file back:  %s ===\n', datestr(now), zipname);
diary off


%% ============================================ cases ============================================
function C = define_cases(mode)
    C = struct('name', {}, 'shape', {}, 'L', {}, 'D', {}, 'h', {}, 'nv', {}, 'nhost', {}, 'gaps', {}, 'lam', {});
    R = 15.874;                       % equal-volume sphere radius (nm)
    if strcmp(mode, 'test')
        lam = 500:50:900;
        C(end+1) = mk('test_sph_n400_air', 'sphere', 0, 2*R, 0, 400, 1, 5, lam);
        C(end+1) = mk('test_rod_L60_h3_air', 'rod', 60, 20, 3, 0, 1, 5, lam);
        C(end+1) = mk('test_rod_L60_h2_air', 'rod', 60, 20, 2, 0, 1, 5, lam(1:3));
        return
    end
    lam  = 500:4:900;                 % 101 wavelengths
    lamL = 500:5:1100;                % long rods / water: resonance shifts to the red
    G    = [3 5 7 10 15 20];          % gaps (nm), all in one solve (almost free)
    % --- priority 1: validation against exact Mie theory + the main rod result
    C(end+1) = mk('sph_n400_air',   'sphere', 0, 2*R, 0, 400,  1, [5 10 20], lam);
    C(end+1) = mk('sph_n784_air',   'sphere', 0, 2*R, 0, 784,  1, [5 10 20], lam);
    C(end+1) = mk('rod_L60_h2_air', 'rod', 60, 20, 2,   0, 1, G, lam);
    C(end+1) = mk('rod_L60_h1.5_air','rod', 60, 20, 1.5, 0, 1, G, lam);
    C(end+1) = mk('rod_L60_h3_air', 'rod', 60, 20, 3,   0, 1, G, lam);
    % --- priority 2: finest meshes (mesh convergence)
    C(end+1) = mk('sph_n1444_air',  'sphere', 0, 2*R, 0, 1444, 1, [5 10 20], lam);
    C(end+1) = mk('rod_L60_h1_air', 'rod', 60, 20, 1,   0, 1, G, lam);
    % --- priority 3: aspect-ratio sweep (D = 20 nm) and water
    for L = [40 50 80 100]
        C(end+1) = mk(sprintf('rod_L%d_h2_air', L), 'rod', L, 20, 2, 0, 1, [5 10 20], lamL); %#ok<AGROW>
    end
    C(end+1) = mk('rod_L60_h2_water', 'rod', 60, 20, 2, 0, 1.33, [5 10 20], lamL);
    C(end+1) = mk('sph_n784_water', 'sphere', 0, 2*R, 0, 784, 1.33, [5 10 20], lam);
end

function c = mk(name, shape, L, D, h, nv, nhost, gaps, lam)
    c = struct('name', name, 'shape', shape, 'L', L, 'D', D, 'h', h, 'nv', nv, 'nhost', nhost, 'gaps', gaps, 'lam', lam);
end

%% ============================================ one case ============================================
function s = run_case(c, outdir)
    s = [];
    fcsv = fullfile(outdir, [c.name '.csv']);
    done = read_done(fcsv);
    todo = c.lam(~ismember(round(c.lam * 100), round(done * 100)));
    if isempty(todo), fprintf('\n--- %s: already complete, skipped\n', c.name); return; end

    op = bemoptions('sim', 'ret', 'interp', 'curv');
    epstab = {epsconst(c.nhost^2), epstable('gold.dat')};       % gold.dat = Johnson & Christy (ships with MNPBEM)
    [p0, ztop] = make_particle(c, op);
    p = comparticle(epstab, {p0}, [2, 1], 1, op);
    N = p.n;
    memgb = 250 * N^2 / 1e9;
    fprintf('\n--- %s: %d boundary elements, apex at z = %.3f nm, est. memory %.1f GB, %d wavelengths to do\n', ...
            c.name, N, ztop, memgb, numel(todo));
    ram = ram_gb();
    if ~isnan(ram) && memgb > 0.7 * ram
        fprintf(2, '    skipped: needs ~%.1f GB but the computer has %.1f GB RAM.\n', memgb, ram); return
    end

    pos = [zeros(numel(c.gaps), 2), ztop + c.gaps(:)];
    pt = compoint(p, pos, op);
    if pt.n ~= numel(c.gaps), error('compoint kept %d of %d dipole positions', pt.n, numel(c.gaps)); end
    [dip, bem] = make_solver(p, pt, op);

    if isempty(done)                                             % header
        fid = fopen(fcsv, 'w');
        fprintf(fid, '# %s shape=%s L=%g D=%g h=%g nverts=%g n_host=%g faces=%d apex_z=%.4f MNPBEM ret curv\n', ...
                c.name, c.shape, c.L, c.D, c.h, c.nv, c.nhost, N, ztop);
        fprintf(fid, 'lambda_nm');
        for g = c.gaps, fprintf(fid, ',Fp_z_g%g,T_z_g%g,Fp_x_g%g,T_x_g%g', g, g, g, g); end
        fprintf(fid, '\n'); fclose(fid);
    end

    t = zeros(size(todo));
    for i = 1:numel(todo)
        t0 = tic;
        enei = todo(i);
        sig = bem \ dip(p, enei);
        [tot, rad] = dip.decayrate(sig);                         % size [n_gaps, 2]: column 1 = z, column 2 = x
        row = zeros(1, 4 * numel(c.gaps));
        for g = 1:numel(c.gaps)
            row(4*g-3:4*g) = [tot(g, 1), rad(g, 1), tot(g, 2), rad(g, 2)];
        end
        fid = fopen(fcsv, 'a'); fprintf(fid, '%.2f', enei); fprintf(fid, ',%.6g', row); fprintf(fid, '\n'); fclose(fid);
        t(i) = toc(t0);
        if i == 1 || mod(i, 5) == 0 || i == numel(todo)
            left = mean(t(1:i)) * (numel(todo) - i);
            fprintf('    %s  lambda=%6.1f nm  Fp_z(%g nm)=%9.1f  T_z=%7.2f  | %5.1f s/lambda, %3d/%d, case done in ~%s\n', ...
                    c.name, enei, c.gaps(min(2, end)), row(4*min(2, numel(c.gaps))-3), row(4*min(2, numel(c.gaps))-2), ...
                    t(i), i, numel(todo), fmt_time(left));
        end
    end
    s = struct('name', c.name, 'nfaces', N, 'sec_per_lambda', median(t));
end

%% ============================================ geometry ============================================
function [p0, ztop] = make_particle(c, op)
    if strcmp(c.shape, 'sphere')
        p0 = with_op(@() trisphere(c.nv, c.D, op), @() trisphere(c.nv, c.D));   % sphere of diameter D at origin
        ztop = c.D / 2;
        return
    end
    % rod: cylinder + hemispherical caps, axis z; target element size c.h (nm)
    n = [ceil(pi * c.D / c.h), 2 * ceil(pi * c.D / (4 * c.h)), ceil((c.L - c.D) / c.h) + 1];
    p0 = with_op(@() trirod(c.D, c.L, n, op), @() trirod(c.D, c.L, n));
    ext = max(p0.verts(:, 3)) - min(p0.verts(:, 3));
    if abs(ext - c.L) > 0.5                                       % other 'height' convention -> correct it
        fprintf('    note: trirod(D, %g) gave total length %.2f nm; correcting\n', c.L, ext);
        H = c.L - (ext - c.L);
        p0 = with_op(@() trirod(c.D, H, n, op), @() trirod(c.D, H, n));
        ext = max(p0.verts(:, 3)) - min(p0.verts(:, 3));
    end
    if abs(ext - c.L) > 0.5, error('rod length %.2f nm instead of %g nm', ext, c.L); end
    zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
    if abs(zc) > 1e-6, p0 = shift(p0, [0, 0, -zc]); end
    ztop = max(p0.verts(:, 3));
    rmax = max(sqrt(p0.verts(:, 1).^2 + p0.verts(:, 2).^2));
    fprintf('    rod mesh n = [%d %d %d]: length %.2f nm, diameter %.2f nm\n', n, ext, 2 * rmax);
end

function [dip, bem] = make_solver(p, pt, op)
    dirs = [0 0 1; 1 0 0];                                       % axial (z) and transverse (x) dipole
    if exist('bemsolver', 'file') && exist('dipole', 'file')     % MNPBEM17
        dip = dipole(pt, dirs, op);
        bem = bemsolver(p, op);
    else                                                         % older MNPBEM versions
        dip = dipoleret(pt, dirs, op);
        bem = bemret(p, [], op);
    end
end

%% ============================================ helpers ============================================
function p = with_op(f1, f2)
    % pass the options (curved interpolation) to the particle if this MNPBEM version accepts them
    try, p = f1(); catch, p = f2(); end
end

function setup_mnpbem(userdir, here)
    if exist('bemoptions', 'file') && exist('trirod', 'file'), return; end
    cand = {userdir, fullfile(here, 'MNPBEM17'), fullfile(here, '..', 'MNPBEM17'), ...
            fullfile(getenv('USERPROFILE'), 'Documents', 'MNPBEM17'), fullfile(getenv('HOME'), 'MNPBEM17'), ...
            fullfile(getenv('HOME'), 'Documents', 'MNPBEM17')};
    try, cand{end+1} = fullfile(strtok(userpath, pathsep), 'MNPBEM17'); catch, end
    for k = 1:numel(cand)
        d = cand{k};
        if ~isempty(d) && exist(d, 'dir'), addpath(genpath(d)); fprintf('MNPBEM added from %s\n', d); break; end
    end
    if ~exist('bemoptions', 'file')
        error(['MNPBEM17 not found. Unzip mnpbem17.zip next to this file (folder name MNPBEM17) ', ...
               'or write its folder in MNPBEM_DIR at the top of the script.']);
    end
    if ~exist('gold.dat', 'file'), error('gold.dat (Johnson-Christy) not found on the MNPBEM path.'); end
end

function lam = read_done(fcsv)
    lam = [];
    if ~exist(fcsv, 'file'), return; end
    fid = fopen(fcsv, 'r');
    while true
        l = fgetl(fid);
        if ~ischar(l), break; end
        if isempty(l) || l(1) == '#' || l(1) == 'l', continue; end
        v = sscanf(l, '%f', 1);
        if ~isempty(v), lam(end+1) = v; end %#ok<AGROW>
    end
    fclose(fid);
end

function g = ram_gb()
    g = NaN;
    try
        if ispc
            [~, sys] = memory; g = sys.PhysicalMemory.Total / 1e9;
        elseif ismac
            [~, r] = system('sysctl -n hw.memsize'); g = str2double(r) / 1e9;
        else
            [~, r] = system('grep MemTotal /proc/meminfo'); g = sscanf(r, 'MemTotal: %f') / 1e6;
        end
    catch
    end
end

function n = num_cores()
    try, n = feature('numcores'); catch, n = nproc(); end
end

function s = fmt_time(sec)
    if sec < 90, s = sprintf('%.0f s', sec);
    elseif sec < 5400, s = sprintf('%.0f min', sec / 60);
    else, s = sprintf('%.1f h', sec / 3600);
    end
end

function estimate_full_runtime(stats)
    % scale the measured time per wavelength with the number of boundary elements N:
    % between N^2 (matrix assembly dominates) and N^3 (matrix inversion dominates)
    if isempty(stats), fprintf(2, '\nNo timing available (test cases failed). See the messages above.\n'); return; end
    [~, k] = max([stats.nfaces]); ref = stats(k);
    C = define_cases('full');
    op = bemoptions('sim', 'ret', 'interp', 'curv');
    lo = 0; hi = 0;
    fprintf('\n=== estimated run time of MODE = ''full'' (from %s: %d elements, %.1f s/lambda) ===\n', ...
            ref.name, ref.nfaces, ref.sec_per_lambda);
    for i = 1:numel(C)
        p0 = make_particle(C(i), op); N = size(p0.faces, 1);
        a = ref.sec_per_lambda * numel(C(i).lam) * (N / ref.nfaces)^2;
        b = ref.sec_per_lambda * numel(C(i).lam) * (N / ref.nfaces)^3;
        fprintf('  %-20s %5d elements  %s .. %s   (needs ~%.1f GB RAM)\n', C(i).name, N, fmt_time(a), fmt_time(b), 250 * N^2 / 1e9);
        lo = lo + a; hi = hi + b;
    end
    fprintf('  TOTAL: between %s and %s\n', fmt_time(lo), fmt_time(hi));
end
