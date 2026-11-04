@echo off
REM Zips all SCAPS outputs (MG_* files) to D:\work\payaname\scaps_results.zip
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; $f = Get-ChildItem -Path $d -Recurse -Filter 'MG_*' -ErrorAction SilentlyContinue; $f += Get-ChildItem -Path $d -Filter '*.log' -ErrorAction SilentlyContinue; Write-Host ('files found: ' + $f.Count); Compress-Archive -Path $f.FullName -DestinationPath D:\work\payaname\scaps_results.zip -Force; Write-Host 'Created D:\work\payaname\scaps_results.zip'"
pause
