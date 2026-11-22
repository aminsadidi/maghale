@echo off
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item rerun\full\def\MAGeI3_WOx_doping.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. SCAPS (Run as administrator): Script set-up  -^>  MAGeI3_WOx_doping.script  -^>  Execute script
pause
