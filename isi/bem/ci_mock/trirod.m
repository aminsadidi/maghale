function p = trirod(D, H, n, varargin)
  conv = getenv('MOCK_CONV');                 % 'excl' -> height excludes caps
  if strcmp(conv, 'excl'), Ltot = H + D; else, Ltot = H; end
  nf = n(1) * (n(2) + n(3));
  z = linspace(-Ltot/2, Ltot/2, 50)' + 3;     % deliberately off-centre
  p.verts = [D/2*ones(50,1), zeros(50,1), z]; p.faces = ones(nf, 4);
end
