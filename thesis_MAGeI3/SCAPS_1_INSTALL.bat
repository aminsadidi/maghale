@echo off
REM Copies the .def files and the script into the SCAPS folders
cd /d "%~dp0"
echo Searching for SCAPS (may take 1-3 minutes) ...
powershell -NoProfile -Command "$s = Get-ChildItem -Path C:\,D:\ -Filter 'scaps*.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1; if(-not $s){Write-Host 'SCAPS NOT FOUND'; exit 1}; $d=$s.DirectoryName; Set-Content -Path scaps_path.txt -Value $d; New-Item -ItemType Directory -Force -Path (Join-Path $d 'script') | Out-Null; Copy-Item scaps\def\*.def (Join-Path $d 'def') -Force; Copy-Item scaps\def\*.script (Join-Path $d 'script') -Force; Write-Host ('Installed into: ' + $d)"
if errorlevel 1 ( echo [ERROR] & pause & exit /b 1 )
echo.
echo DONE. Now in SCAPS:  Script set-up  ->  MAGeI3_all_steps.script  ->  Execute script
pause
