@echo off
REM Copies the FAPbI3 feasibility-test files into SCAPS (needs scaps_path.txt from SCAPS_1_INSTALL.bat)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item fa_test\def\FA_*.def (Join-Path $d 'def') -Force; Copy-Item fa_test\def\FA_feasibility.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. Open SCAPS with Run as administrator: Script set-up  -^>  FA_feasibility.script  -^>  Execute script
pause
