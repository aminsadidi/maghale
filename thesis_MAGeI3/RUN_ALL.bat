@echo off
REM ======================================================================
REM  MAGeI3 thesis - one-click simulation + figures + Excel + Word chapter
REM  Usage:  double-click this file,  or in CMD:   RUN_ALL.bat
REM ======================================================================
setlocal
cd /d "%~dp0"
title MAGeI3 thesis - full simulation

set PY=
where python >nul 2>nul && set PY=python
if "%PY%"=="" ( where py >nul 2>nul && set PY=py -3 )
if "%PY%"=="" (
  echo.
  echo [ERROR] Python was not found.
  echo   1^) Install Python 3.11 or newer from https://www.python.org/downloads/
  echo   2^) In the installer TICK the box "Add python.exe to PATH"
  echo   3^) Close this window and run RUN_ALL.bat again.
  echo.
  pause
  exit /b 1
)

echo [1/6] Installing / checking Python packages ...
%PY% -m pip install --disable-pip-version-check -q -r requirements.txt || goto :fail

echo [2/6] Running the full simulation campaign (10-40 minutes) ...
%PY% -W ignore sim\run_all.py || goto :fail

echo [3/6] Solver validation (Shockley diode + mesh test) ...
%PY% -W ignore sim\validate.py || goto :fail

echo [4/6] Drawing figures (300 dpi) ...
%PY% sim\make_figures.py || goto :fail

echo [5/6] Writing Excel workbook for OriginPro ...
%PY% sim\make_excel.py || goto :fail

echo [6/6] Writing Chapter 4 into the Word template ...
%PY% word\make_chapter4.py || goto :fail

echo.
echo ======================================================================
echo  DONE.  Outputs:
echo    word\Thesis_with_Chapter4.docx      (Word, B Nazanin 12, spacing 1.2)
echo    figures\*.png                        (300 dpi figures)
echo    origin\Origin_Data_MAGeI3.xlsx       (data for OriginPro / Excel)
echo    results\*.csv                        (raw data)
echo ======================================================================
start "" "word\Thesis_with_Chapter4.docx"
pause
exit /b 0

:fail
echo.
echo [ERROR] A step failed. Send a screenshot of this window.
pause
exit /b 1
