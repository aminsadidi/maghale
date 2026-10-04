classdef mockbem
  properties, n, end
  methods
    function o = mockbem(n), o.n = n; end
    function sig = mldivide(o, exc)
      pause(0.01); sig = exc;
      if ~isempty(getenv('MOCK_FAIL')) && exc.enei > str2double(getenv('MOCK_FAIL')), error('simulated crash'); end
    end
  end
end
