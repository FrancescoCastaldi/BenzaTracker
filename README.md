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
python -m benzatracker --gui    # runs GUI
BENZA_WEB=1 python -m benzatracker  # runs Web (Flask)
```

> For a complete reference — including editable install, entry-point shortcuts,
> Docker, environment variables, data persistence modes, and troubleshooting —
> see **[LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)**.
>
> New contributors should read **[CONTRIBUTING.md](CONTRIBUTING.md)**.
> All participants must follow our **[Code of Conduct](CODE_OF_CONDUCT.md)**.

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
├── .editorconfig               # Editor-agnostic settings
├── .gitattributes              # Git attributes
├── .gitignore
├── .pre-commit-config.yaml     # Pre-commit hooks (ruff, mypy)
├── CODE_OF_CONDUCT.md          # Contributor Covenant 2.1
├── CONTRIBUTING.md             # Full contributing guide
├── SECURITY.md                 # Vulnerability reporting policy
├── SUPPORT.md                  # Where to get help
├── LAUNCH_GUIDE.md             # Detailed launch instructions
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml              # Build config + ruff/mypy/pytest + entry points
├── requirements.txt
├── install_and_run.bat
├── .github/
│   ├── workflows/
│   │   └── python-app.yml      # CI pipeline (3.10–3.12)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   └── PULL_REQUEST_TEMPLATE.md
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
│   ├── test_data_store.py      # JsonStore tests
│   ├── test_kpi.py             # KPI computation tests
│   ├── test_cli_windows.py     # CLI window tests
│   └── test_database.py        # SqliteStore tests
└── data/                       # SQLite database (Docker volume, gitignored)
```

---

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide (setup, coding style, testing, PR workflow).

Quick links:
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Bug Reports](.github/ISSUE_TEMPLATE/bug_report.yml)
- [Feature Requests](.github/ISSUE_TEMPLATE/feature_request.yml)
- [Security Policy](SECURITY.md)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## License

Distributed under the **MIT** license. See [LICENSE](LICENSE) for details.
