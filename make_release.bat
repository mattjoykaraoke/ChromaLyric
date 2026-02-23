@echo off
setlocal enableextensions enabledelayedexpansion

REM ==========================================
REM One-stop release: build + Inno Setup compile
REM ==========================================

set "ROOT=%~dp0"
cd /d "%ROOT%"

call "%ROOT%make_build.bat"
if errorlevel 1 (
  echo.
  echo Release aborted: build failed.
  exit /b 1
)

REM Find Inno Setup compiler (ISCC.exe)
set "ISCC="

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
  echo.
  echo ERROR: Could not find ISCC.exe (Inno Setup 6).
  echo Install Inno Setup 6, then re-run.
  exit /b 1
)

REM Ensure output folder exists
if not exist "%ROOT%release" mkdir "%ROOT%release"

"%ISCC%" "%ROOT%ISSRunLast.iss"
if errorlevel 1 (
  echo.
  echo Release failed: Inno Setup compile failed.
  exit /b 1
)

echo.
echo RELEASE OK. Check the "release" folder for the installer.
exit /b 0