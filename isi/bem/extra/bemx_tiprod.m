function [p0, ztop] = bemx_tiprod(D, L, c, h, op)
%  BEMX_TIPROD - gold rod of total length L and diameter D whose end caps are half-spheroids with semi-axis c
%    along the rod axis (c = D/2: hemispherical caps; c < D/2: flatter ends). Built from a hemispherically capped
%    rod with cylinder length L - 2c by compressing the cap vertices along z; the curved-element midpoints are
%    then recomputed for the new shape.
R = D / 2;  Lc = L - 2 * c;
q = bemx_rod(D, Lc + D, h);                       % flat-element template, cylinder length Lc
v = q.verts;  z = v(:, 3);  cap = abs(z) > Lc / 2 + 1e-9;
v(cap, 3) = sign(z(cap)) .* (Lc / 2 + (abs(z(cap)) - Lc / 2) * c / R);
p0 = particle(v, q.faces, op);
ztop = max(p0.verts(:, 3));
if abs(ztop - L / 2) > 1e-6, error('bemx_tiprod: apex at %.3f instead of %.3f', ztop, L / 2); end
