@echo off
setlocal enabledelayedexpansion
color 0A
title BenzaTracker - Installation & Launcher

echo.
echo ==========================================
echo   BenzaTracker Installation & Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM Activate virtual environment
echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

REM Upgrade pip
echo.
echo [*] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip upgraded.

REM Install requirements
echo.
echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.

REM Install PyInstaller if not already installed
echo.
echo [*] Checking PyInstaller installation...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [*] Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller is ready.

REM Clean old build
echo.
echo [*] Cleaning old builds...
if exist "dist" rmdir /s /q dist >nul 2>&1
if exist "build" rmdir /s /q build >nul 2>&1
if exist "*.spec" del /q *.spec >nul 2>&1
echo [OK] Old builds cleaned.

REM Build executable
echo.
echo [*] Building executable with PyInstaller...
echo    (This may take a minute or two...)
echo.

pyinstaller -w -F main.py -n BenzaTracker --onefile --add-data "benzatracker:benzatracker" --icon=NONE

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to build executable.
    pause
    exit /b 1
)

echo.
echo [OK] Executable built successfully!

REM Check if executable was created
if not exist "dist\BenzaTracker.exe" (
    echo [ERROR] Executable was not created in dist folder.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo [*] Launching BenzaTracker...
echo.

REM Launch the application
cd dist
start "" "BenzaTracker.exe"
cd ..
echo [OK] Application launched!
echo.
echo To run BenzaTracker again in the future, double-click this file.
echo.
pause
endlocal
