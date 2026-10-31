@echo off
rem START.bat - the only file to run: checks MATLAB / Lumerical, runs short tests, then all simulations (offline, resumes).
cd /d "%~dp0"
title maghale simulations - DO NOT CLOSE THIS WINDOW
set "PY="
if exist "%~dp0vendor\python\python.exe" set "PY=%~dp0vendor\python\python.exe"
if not defined PY if exist "vendor\python_path.txt" set /p PY=<"vendor\python_path.txt"
if not defined PY set "PY=python"
"%PY%" "lab\runner.py" run --redetect %*
echo.
pause
