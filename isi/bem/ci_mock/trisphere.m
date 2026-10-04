function p = trisphere(nv, D, varargin)
  p.verts = [0 0 D/2; 0 0 -D/2; D/2 0 0]; p.faces = ones(2*nv, 4);
end
