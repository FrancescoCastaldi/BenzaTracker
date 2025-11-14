@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist .venv\Scripts\python.exe (
    echo Creazione dell'ambiente virtuale...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt >nul

python -m benzatracker.cli %*

endlocal
