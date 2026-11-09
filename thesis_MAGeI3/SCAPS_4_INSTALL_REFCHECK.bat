@echo off
REM Copies the refcheck .def files and script into SCAPS (uses scaps_path.txt)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item scaps\def\0?_REF_*.def (Join-Path $d 'def') -Force; Copy-Item scaps\def\MAGeI3_refcheck.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. Open SCAPS with Run as administrator, then: Script set-up  -^>  MAGeI3_refcheck.script  -^>  Execute script
pause
