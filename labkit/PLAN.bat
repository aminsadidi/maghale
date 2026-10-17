@echo off
rem PLAN.bat - show the plan and the predicted time (works offline). Extra options are passed on, e.g.  PLAN.bat --tiers 1,2 --max-days 5
cd /d "%~dp0"
set PY=python
if exist "vendor\python_path.txt" set /p PY=<"vendor\python_path.txt"
"%PY%" "lab\runner.py" plan %*
pause
