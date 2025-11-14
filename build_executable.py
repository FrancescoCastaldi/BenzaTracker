"""Utility per creare l'eseguibile standalone di BenzaTracker con PyInstaller."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    display = " ".join(command)
    print(f"$ {display}")
    subprocess.run(command, check=True, cwd=cwd)


def _ensure_dependencies(python: str) -> None:
    """Install required dependencies and PyInstaller itself."""

    _run([python, "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
    _run([python, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], cwd=ROOT)
    _run([python, "-m", "pip", "install", "pyinstaller>=6.0"], cwd=ROOT)


def _build_executable(python: str, mode: str) -> None:
    """Invoke PyInstaller to generate the application executable."""

    command = [
        python,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "BenzaTracker",
    ]

    if mode == "gui":
        command.append("--windowed")
    else:
        command.append("--console")

    command.append(str(ROOT / "main.py"))
    _run(command, cwd=ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera l'eseguibile di BenzaTracker con PyInstaller")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Percorso dell'interprete Python da utilizzare (default: quello corrente)",
    )
    parser.add_argument(
        "--mode",
        choices=("gui", "console"),
        default="gui",
        help="Tipologia di eseguibile da generare (GUI windowed o console).",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Salta l'installazione preventiva delle dipendenze e di PyInstaller.",
    )

    args = parser.parse_args()

    try:
        if not args.skip_deps:
            _ensure_dependencies(args.python)
        _build_executable(args.python, args.mode)
        target = ROOT / "dist" / "BenzaTracker"
        if os.name == "nt":
            target = target.with_suffix(".exe")
        print(f"Eseguibile generato in: {target}")
    except subprocess.CalledProcessError as exc:  # pragma: no cover - flusso eccezioni
        print(f"Comando fallito con codice {exc.returncode}.")
        sys.exit(exc.returncode)


if __name__ == "__main__":  # pragma: no cover - script manuale
    main()
