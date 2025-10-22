#!/usr/bin/env bash
set -euo pipefail

COMMAND="python3"
if ! command -v "$COMMAND" >/dev/null 2>&1; then
  echo "Python 3 non trovato. Installa Python 3 prima di procedere." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d .venv ]; then
  "$COMMAND" -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python -m benzatracker.gui
