@echo off
REM Zips ALL re-simulation outputs (MG_F_*) to D:\work\payaname\final_results.zip
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; $f = @(Get-ChildItem -Path $d, (Join-Path $env:LOCALAPPDATA 'VirtualStore') -Recurse -Force -Filter 'MG_F_*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Group-Object Name | ForEach-Object { $_.Group[0] }); Write-Host ('files found: ' + $f.Count + ' (expected 101)'); if ($f.Count -gt 0) { Compress-Archive -Path $f.FullName -DestinationPath D:\work\payaname\final_results.zip -Force; Write-Host 'Created D:\work\payaname\final_results.zip' }"
pause
