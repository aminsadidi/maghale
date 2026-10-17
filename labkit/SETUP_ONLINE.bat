@echo off
rem SETUP_ONLINE.bat - one-time setup while connected to the internet
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "scripts\setup_online.ps1"
pause
