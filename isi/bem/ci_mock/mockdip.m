classdef mockdip
  % stand-in for MNPBEM's dipole object: dip(p, enei) -> excitation, decayrate(dip, sig) -> rates
  properties, pt, end
  methods
    function o = mockdip(pt), o.pt = pt; end
    function varargout = subsref(o, s)
      if strcmp(s(1).type, '()')
        varargout{1} = struct('enei', s(1).subs{2});
      else
        [varargout{1:nargout}] = builtin('subsref', o, s);
      end
    end
    function [tot, rad] = decayrate(o, sig)
      g = o.pt.pos(:, 3);
      tot = [1000 * exp(-((sig.enei - 620) / 40)^2) ./ g, 10 ./ g];
      rad = tot / 10;
    end
  end
end
