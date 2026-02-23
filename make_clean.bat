@echo off
setlocal

echo ===============================
echo Cleaning build artifacts...
echo ===============================

if exist build (
    rmdir /s /q build
    echo Removed build\
)

if exist dist (
    rmdir /s /q dist
    echo Removed dist\
)

if exist ChromaLyric.spec (
    del /q ChromaLyric.spec
    echo Removed ChromaLyric.spec
)

echo.
echo Clean complete.
echo ===============================
echo.
pause
