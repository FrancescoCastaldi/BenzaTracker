# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [2.0.0] — 2026-06-07

### Added
- `src/` layout with `pyproject.toml` setuptools discovery (`where = ["src"]`)
- `benzatracker-gui` and `benzatracker-web` entry points in `pyproject.toml`
- `config.py` — centralized environment variable handling (`DATA_DIR`, `BENZA_MODE`)
- `store.py` — `Store` protocol + `create_store()` factory with lazy imports
- `sqlite_store.py` — `SqliteStore` (SQLite persistence, ported from `database.py`)
- `json_store.py` — `JsonStore` (JSON persistence, ported from `data_store.py`)
- `models.py` — `RefuelEntry` and `KPIReport` dataclasses separated from store
- `__main__.py` — unified entry point dispatching CLI/GUI/Web via `BENZA_MODE`
- Flask web interface with dashboard, entries CRUD, chart, and PDF export
- Docker support with `Dockerfile` + `docker-compose.yml` (SQLite, port 5000)
- 3 Jinja2 templates (Bootstrap 5.3 dark theme)

### Changed
- Restructured from flat `benzatracker/` package to `src/benzatracker/` layout
- `DataStore` → `JsonStore` (same API, clearer name)
- `DatabaseStore` → `SqliteStore` (same API, clearer name)
- `pdf_report.py` → `pdf.py`, `ReportPDFGenerator` → `ReportGenerator`
- `compute_kpis()` → `compute()` (shorter name)
- `pytest.ini` removed, config moved to `pyproject.toml` with `pythonpath = ["src"]`
- `main.py` removed, replaced by `__main__.py` + module entry points
- `Dockerfile` now installs via `pip install .` with `src/` layout
- CI workflow (`python-app.yml`) now lints `src/benzatracker/` instead of `benzatracker/`
- All tests updated to import from new module paths

### Fixed
- `gui.py`: indent fix for `_on_delete` (was nested inside `_clear_form`)
- `gui.py`: indent fix for `_build_layout`

---

## [1.0.0] — 2025-10-01

### Added
- Initial release with GUI (ttkbootstrap), CLI, KPI dashboard, monthly spend
  chart and PDF export via ReportLab
- Persistent local storage at `~/.benzatracker/refuels.json`
- GitHub Actions CI workflow
