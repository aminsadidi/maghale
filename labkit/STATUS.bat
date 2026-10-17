@echo off
rem STATUS.bat - open the live status page (refreshes every 30 s)
cd /d "%~dp0"
if exist "output\status.html" (start "" "output\status.html") else (echo no status yet - start RUN.bat first & pause)
