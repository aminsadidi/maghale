@echo off
REM Copies the WOx re-simulation files into SCAPS (uses scaps_path.txt from SCAPS_1_INSTALL.bat)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item rerun\wox\def\03b_WOx_Coatings2023.def (Join-Path $d 'def') -Force; Copy-Item rerun\wox\def\MAGeI3_WOx_rerun.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. Open SCAPS with Run as administrator: Script set-up  -^>  MAGeI3_WOx_rerun.script  -^>  Execute script
pause
