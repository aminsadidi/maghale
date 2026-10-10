function job_nshell(spec, outdir)
%  JOB_NSHELL - quantum emitter INSIDE a rod-shaped gold nanoshell (silica core, n = 1.45, in a host of n = 1.45),
%  compared with a spherical nanoshell and with a solid rod of the same outer size (emitter outside the tip).
%    spec : 'L60_t7'   core = capsule of total length 60 nm and diameter 20 nm, gold shell 7 nm thick
%           'sph_t7'   core = sphere of diameter 20 nm, gold shell 7 nm
%           'solid_L60_t7'  solid gold rod with the outer size of 'L60_t7', emitter 4 nm beyond the tip (reference)
%  Emitter positions (shells): centre; on the axis 4 nm from the inner cap; on the side 4 nm from the inner wall.
%  Dipoles along z (rod axis) and x. Rates are in units of the rate in the host (n = 1.45); extinction for plane
%  waves polarised along z (incidence x) and along x (incidence z).
n = 1.45;  Din = 20;
op = bemoptions('sim', 'ret', 'interp', 'curv');
gold = epstable('gold.dat');
solid = strncmp(spec, 'solid_', 6);  s = spec;  if solid, s = spec(7:end); end
parts = strsplit(s, '_t');  t = str2double(parts{2});
issph = strcmp(parts{1}, 'sph');
if issph, Lin = Din; else, Lin = str2double(parts{1}(2:end)); end
if solid
    [p0, ztop] = bemx_rod(Din + 2 * t, Lin + 2 * t, 2, op);
    p = comparticle({epsconst(n^2), gold}, {p0}, [2, 1], 1, op);
    pos = [0, 0, ztop + 4];  lab = {'tip_out'};
else
    if issph
        pin = trisphere(400, Din);  pout = trisphere(576, Din + 2 * t);
    else
        [pin, ~] = bemx_rod(Din, Lin, 2, op);  [pout, ~] = bemx_rod(Din + 2 * t, Lin + 2 * t, 2, op);
    end
    p = comparticle({epsconst(n^2), gold, epsconst(n^2)}, {pin, pout}, [3, 2; 2, 1], 1, 2, op);
    pos = [0, 0, 0;  0, 0, Lin / 2 - 4;  Din / 2 - 4, 0, 0];  lab = {'centre', 'axis_cap4', 'side4'};
end
pt = compoint(p, pos, op);
if pt.n ~= size(pos, 1), error('compoint lost points (%d of %d)', pt.n, size(pos, 1)); end
dip = dipole(pt, [0 0 1; 1 0 0], op);
exc = planewave([0 0 1; 1 0 0], [1 0 0; 0 0 1], op);
bem = bemsolver(p, op);
lam = 500:10:1800;  np = size(pos, 1);
M = zeros(numel(lam), 3 + 4 * np);
for il = 1:numel(lam)
    [tot, rad] = decayrate(dip, bem \ dip(p, lam(il)));
    ext = exc.ext(bem \ exc(p, lam(il)));
    row = [lam(il), ext(1), ext(2)];
    for k = 1:np, row = [row, tot(k, 1), rad(k, 1), tot(k, 2), rad(k, 2)]; end %#ok<AGROW>
    M(il, :) = row;
end
hdr = 'lambda_nm,ext_z,ext_x';
for k = 1:np, hdr = [hdr, sprintf(',Fp_z_%s,T_z_%s,Fp_x_%s,T_x_%s', lab{k}, lab{k}, lab{k}, lab{k})]; end %#ok<AGROW>
bemx_csv(fullfile(outdir, ['nshell_' spec '.csv']), hdr, M, sprintf('%s: core L=%g D=%g, shell t=%g, n=%.2f, faces=%d, solid=%d', ...
    spec, Lin, Din, t, n, p.n, solid));
