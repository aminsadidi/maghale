@echo off
REM Copies the re-simulation (stage 1) files into SCAPS (uses scaps_path.txt from SCAPS_1_INSTALL.bat)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item rerun\full\def\10_RERUN_*.def (Join-Path $d 'def') -Force; Copy-Item rerun\full\def\MAGeI3_RERUN_stage1.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. Open SCAPS with Run as administrator: Script set-up  -^>  MAGeI3_RERUN_stage1.script  -^>  Execute script
pause
