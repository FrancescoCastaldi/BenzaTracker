[CmdletBinding()]
param(
    [string]$ExecutableName = "BenzaTracker"
)

$ErrorActionPreference = "Stop"

function Resolve-Python {
    foreach ($candidate in @("py", "python", "python3")) {
        try {
            $command = Get-Command $candidate -ErrorAction Stop
            return $command.Source
        } catch {
            continue
        }
    }
    throw "Python non trovato. Installa Python 3 e riprova."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

try {
    $pythonExe = Resolve-Python
    Write-Host "Utilizzo l'interprete Python: $pythonExe"

    Write-Host "Aggiornamento di pip..."
    & $pythonExe -m pip install --upgrade pip | Write-Output

    if (Test-Path "requirements.txt") {
        Write-Host "Installazione delle dipendenze dell'applicazione..."
        & $pythonExe -m pip install -r requirements.txt | Write-Output
    }

    Write-Host "Installazione di PyInstaller..."
    & $pythonExe -m pip install --upgrade pyinstaller | Write-Output

    if (Test-Path "dist") {
        Write-Host "Rimozione della cartella dist esistente..."
        Remove-Item -Recurse -Force dist
    }
    if (Test-Path "build") {
        Write-Host "Rimozione della cartella build esistente..."
        Remove-Item -Recurse -Force build
    }
    if (Test-Path "$ExecutableName.spec") {
        Remove-Item -Force "$ExecutableName.spec"
    }

    Write-Host "Creazione dell'eseguibile standalone..."
    & $pythonExe -m pyinstaller --name $ExecutableName --onefile --clean --noconfirm --console main.py | Write-Output

    Write-Host "Operazione completata. Troverai l'eseguibile in dist\\$ExecutableName.exe"
} finally {
    Pop-Location
}
