# BenzaTracker

<p align="center">
  <img src="docs/logo.png" alt="BenzaTracker logo" width="220"/>
</p>

<p align="center">
  <a href="https://github.com/FrancescoCastaldi/BenzaTracker/actions/workflows/python-app.yml">
    <img src="https://github.com/FrancescoCastaldi/BenzaTracker/actions/workflows/python-app.yml/badge.svg" alt="CI"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"/>
  </a>
  <a href="https://docs.astral.sh/ruff/">
    <img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code style: ruff"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/BenzaTracker/pulls">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"/>
  </a>
</p>

> Desktop, CLI and Web application to track fuel refuels, compute spending KPIs and export PDF reports.
> Now using **src/ layout** with SQLite + JSON persistence and Docker support.

---

## Features

| Feature | Description |
|---|---|
| Refuel logging | Date, liters, amount paid, price per liter, station, odometer |
| KPI dashboard | Total spent, total liters, average price, monthly average |
| Monthly chart | Interactive bar chart via matplotlib |
| PDF export | Full report with table via ReportLab |
| Persistence | JSON file **or** SQLite (configurable via `DATA_DIR` env) |
| GUI + CLI + Web | ttkbootstrap GUI, terminal CLI, Flask web UI |

---

## Quick Start (Docker)

```bash
docker compose up -d
# Open http://localhost:5000
```

Data persists in `./data/` (SQLite, gitignored).

---

## Traditional Installation

### Prerequisites

- Python **3.10+**
- `pip`

### macOS / Linux

```bash
git clone https://github.com/FrancescoCastaldi/BenzaTracker.git
cd BenzaTracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
git clone https://github.com/FrancescoCastaldi/BenzaTracker.git
cd BenzaTracker
install_and_run.bat
```

---

## Usage

### Web interface (Flask)

```bash
DATA_DIR=./data python -m benzatracker.web
# → http://localhost:5000
```

### Graphical interface (ttkbootstrap)

```bash
python -m benzatracker.gui
```

### Command-line interface

```bash
python -m benzatracker.cli
```

Or use the unified entry point:

```bash
python -m benzatracker          # runs CLI by default
BENZA_MODE=gui python -m benzatracker
BENZA_MODE=web python -m benzatracker
```

---

## Tests

```bash
pip install pytest pytest-cov
pytest -v --tb=short
```

Tests cover JSON store, SQLite store, KPI computation, CLI windows, and Flask routes.

---

## Project Structure

```
BenzaTracker/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml              # Build config + ruff/mypy/pytest
├── requirements.txt
├── install_and_run.bat
├── src/
│   └── benzatracker/
│       ├── __init__.py
│       ├── __main__.py         # Entry point (CLI / GUI / Web dispatch)
│       ├── config.py           # Environment variables, paths
│       ├── models.py           # RefuelEntry, KPIReport dataclasses
│       ├── store.py            # Store protocol + create_store() factory
│       ├── json_store.py       # JSON persistence (atomic write)
│       ├── sqlite_store.py     # SQLite persistence
│       ├── kpi.py              # KPI computation
│       ├── cli.py              # Command-line interface
│       ├── gui.py              # ttkbootstrap graphical interface
│       ├── web.py              # Flask web application
│       ├── pdf.py              # PDF export via ReportLab
│       └── templates/          # Jinja2 HTML templates
│           ├── base.html
│           ├── index.html
│           └── entries.html
├── tests/
│   ├── test_data_store.py
│   ├── test_kpi.py
│   ├── test_cli_windows.py
│   ├── test_database.py
│   └── test_web.py
└── data/                       # SQLite database (Docker volume, gitignored)
```

---

## Contributing

1. Fork the repo
2. Branch: `git checkout -b feat/your-feature`
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`
4. Open a Pull Request

```bash
# Optional: pre-commit hooks
pip install pre-commit
pre-commit install
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## License

Distributed under the **MIT** license. See [LICENSE](LICENSE) for details.
