@echo off
REM Installs ALL re-simulation files into SCAPS (uses scaps_path.txt)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item rerun\full\def\1?_RERUN_*.def (Join-Path $d 'def') -Force; Copy-Item rerun\full\def\MAGeI3_RERUN_FULL.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. SCAPS (Run as administrator): Script set-up  -^>  MAGeI3_RERUN_FULL.script  -^>  Execute script
pause
