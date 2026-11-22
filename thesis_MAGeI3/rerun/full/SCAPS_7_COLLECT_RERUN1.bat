@echo off
REM Zips the stage-1 re-simulation outputs (MG_R1_*) to D:\work\payaname\rerun1_results.zip
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; $f = @(Get-ChildItem -Path $d, (Join-Path $env:LOCALAPPDATA 'VirtualStore') -Recurse -Force -Filter 'MG_R1_*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Group-Object Name | ForEach-Object { $_.Group[0] }); Write-Host ('files found: ' + $f.Count + ' (expected 46)'); if ($f.Count -gt 0) { Compress-Archive -Path $f.FullName -DestinationPath D:\work\payaname\rerun1_results.zip -Force; Write-Host 'Created D:\work\payaname\rerun1_results.zip' }"
pause
