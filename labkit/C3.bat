@echo off
rem C3.bat - campaign 3 only: third rod 20-80 nm from the dimer, then rotated (Lumerical FDTD, resumes automatically)
cd /d "%~dp0"
title maghale campaign 3 - DO NOT CLOSE THIS WINDOW
set "PY="
if exist "%~dp0vendor\python\python.exe" set "PY=%~dp0vendor\python\python.exe"
if not defined PY if exist "vendor\python_path.txt" set /p PY=<"vendor\python_path.txt"
if not defined PY set "PY=python"
"%PY%" "lab\runner.py" run --redetect --tiers 5 --only lumerical %*
echo.
pause
