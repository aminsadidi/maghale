function [p0, ztop] = bemx_rod(D, L, h, varargin)
%  BEMX_ROD - capped gold nanorod (cylinder + hemispherical caps), axis z, centred at origin.
%    D, L : diameter and total length (nm);  h : target boundary-element size (nm)
n = [ceil(pi * D / h), 2 * ceil(pi * D / (4 * h)), ceil((L - D) / h) + 1];
p0 = trirod(D, L, n, varargin{:});              % MNPBEM17: height = total length (checked below)
ext = max(p0.verts(:, 3)) - min(p0.verts(:, 3));
if abs(ext - L) > 0.5, error('bemx_rod: length %.2f instead of %g', ext, L); end
zc = 0.5 * (max(p0.verts(:, 3)) + min(p0.verts(:, 3)));
if abs(zc) > 1e-6, p0 = shift(p0, [0, 0, -zc]); end
ztop = max(p0.verts(:, 3));
