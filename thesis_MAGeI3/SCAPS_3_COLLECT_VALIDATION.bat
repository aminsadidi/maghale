@echo off
REM Zips only the validation outputs (MG_VAL_*) to D:\work\payaname\validation_results.zip
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; $f = Get-ChildItem -Path $d -Recurse -Filter 'MG_VAL_*' -ErrorAction SilentlyContinue; Write-Host ('files found: ' + $f.Count); Compress-Archive -Path $f.FullName -DestinationPath D:\work\payaname\validation_results.zip -Force; Write-Host 'Created D:\work\payaname\validation_results.zip'"
pause
