@echo off
setlocal enableextensions enabledelayedexpansion

REM ==========================================
REM ChromaLyric build script (PyInstaller one-dir)
REM ==========================================

REM Project root = this .bat location
set "ROOT=%~dp0"
cd /d "%ROOT%"

REM Output folders
set "DIST_DIR=%ROOT%dist"
set "BUILD_DIR=%ROOT%build"

REM Clean previous outputs (optional but recommended)
if exist "%DIST_DIR%\ChromaLyric" rmdir /s /q "%DIST_DIR%\ChromaLyric"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

REM Ensure PyInstaller exists
py -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
  echo PyInstaller not found. Installing...
  py -m pip install --upgrade pip
  py -m pip install pyinstaller
)

REM Ensure runtime deps exist (PySide6)
py -m pip show PySide6 >nul 2>&1
if errorlevel 1 (
  echo PySide6 not found. Installing...
  py -m pip install PySide6
)

REM Build (one-dir, windowed)
REM Note: --add-data uses "SRC;DEST" on Windows.
py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --windowed ^
  --name "ChromaLyric" ^
  --add-data "assets;assets" ^
  --add-data "assets\ChromaLyricLogo.png;." ^
  --add-data "assets\ChromaLyric.ico;." ^
  --add-data "licenses;licenses" ^
  --icon "assets\ChromaLyric.ico" ^
  "app.py"

if errorlevel 1 (
  echo.
  echo BUILD FAILED.
  exit /b 1
)

echo.
echo BUILD OK: "%DIST_DIR%\ChromaLyric\ChromaLyric.exe"
exit /b 0