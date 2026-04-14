@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  CollisionDetector - Windows Build Script
echo ============================================
echo.

:: ── Check Python ─────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Found: %PYVER%
echo.

:: ── Install PyInstaller ───────────────────────────────────────────────────────
echo [1/3] Installing / upgrading PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)
echo.

:: ── Build ─────────────────────────────────────────────────────────────────────
echo [2/3] Building CollisionDetector.exe ...
pyinstaller --onefile --windowed --name CollisionDetector collision_detector.py
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
echo.

:: ── Cleanup ───────────────────────────────────────────────────────────────────
echo [3/3] Cleaning up build artefacts...
if exist build rmdir /s /q build
if exist CollisionDetector.spec del /q CollisionDetector.spec
echo.

:: ── Done ──────────────────────────────────────────────────────────────────────
echo ============================================
echo  Build successful!
echo  Output: dist\CollisionDetector.exe
echo ============================================
pause
