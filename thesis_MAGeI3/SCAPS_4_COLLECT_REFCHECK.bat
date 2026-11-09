@echo off
REM Zips the refcheck outputs (MG_REF_*) from the SCAPS folder or the VirtualStore copy
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; $f = @(Get-ChildItem -Path $d, (Join-Path $env:LOCALAPPDATA 'VirtualStore') -Recurse -Force -Filter 'MG_REF_*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Group-Object Name | ForEach-Object { $_.Group[0] }); Write-Host ('files found: ' + $f.Count); if ($f.Count -gt 0) { Compress-Archive -Path $f.FullName -DestinationPath D:\work\payaname\refcheck_results.zip -Force; Write-Host 'Created D:\work\payaname\refcheck_results.zip' }"
pause
