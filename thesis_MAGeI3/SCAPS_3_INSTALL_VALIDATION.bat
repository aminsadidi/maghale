@echo off
REM Copies the validation .def and script into the SCAPS folders (uses scaps_path.txt from SCAPS_1_INSTALL.bat)
cd /d "%~dp0"
powershell -NoProfile -Command "$d = Get-Content scaps_path.txt; Copy-Item scaps\def\00_validation_Bhattarai2021.def (Join-Path $d 'def') -Force; Copy-Item scaps\def\MAGeI3_validation.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo DONE. In SCAPS: Script set-up  -^>  MAGeI3_validation.script  -^>  Execute script
pause
