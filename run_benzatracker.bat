@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "PYTHON_CMD=python"
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo Python non trovato. Installa Python 3 e riprova.
        exit /b 1
    )
    set "PYTHON_CMD=py"
)

if not exist .venv\Scripts\python.exe (
    echo Creazione dell'ambiente virtuale...
    %PYTHON_CMD% -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul

python -m benzatracker.cli %*

endlocal
