@echo off
rem RUN.bat - run all planned simulations, resumes automatically (works offline). Extra options are passed on, e.g.  RUN.bat --tiers 1,2 --max-days 5
cd /d "%~dp0"
set PY=python
if exist "vendor\python_path.txt" set /p PY=<"vendor\python_path.txt"
"%PY%" "lab\runner.py" run %*
pause
