function bemx_csv(fname, header, M, meta)
%  BEMX_CSV - write matrix M with a header line (and optional '# meta' line) to a CSV file.
fid = fopen(fname, 'w');
if nargin > 3 && ~isempty(meta), fprintf(fid, '# %s\n', meta); end
fprintf(fid, '%s\n', header);
fmt = [repmat('%.7g,', 1, size(M, 2) - 1), '%.7g\n'];
fprintf(fid, fmt, M.');
fclose(fid);
