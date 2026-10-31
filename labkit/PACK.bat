@echo off
rem PACK.bat - zip the results for transfer (works offline). Extra options are passed on, e.g.  PACK.bat --tiers 1,2 --max-days 5
cd /d "%~dp0"
set "PY="
if exist "%~dp0vendor\python\python.exe" set "PY=%~dp0vendor\python\python.exe"
if not defined PY if exist "vendor\python_path.txt" set /p PY=<"vendor\python_path.txt"
if not defined PY set "PY=python"
"%PY%" "lab\runner.py" pack %*
pause
