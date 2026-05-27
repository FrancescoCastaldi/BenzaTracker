# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `pyproject.toml` with project metadata, `ruff` and `mypy` configuration
- `.pre-commit-config.yaml` with `ruff`, `mypy` and whitespace hooks
- `CHANGELOG.md` following Keep-a-Changelog format

### Changed
- `README.md`: full rewrite with CI/Python/License/ruff badges, feature table,
  installation instructions for macOS, Linux and Windows, project structure and
  contributing guide

### Fixed
- `data_store.py`: replaced direct `open("w")` write with atomic
  write-then-rename (`tempfile.mkstemp` + `os.replace`) to prevent JSON
  corruption if the process is interrupted mid-write
- `data_store.py`: added input validation in `RefuelEntry.from_dict` — raises
  `ValueError` for negative liters, negative amounts or negative price-per-liter

---

## [1.0.0] — 2025-10-01

### Added
- Initial release with GUI (ttkbootstrap), CLI, KPI dashboard, monthly spend
  chart and PDF export via ReportLab
- Persistent local storage at `~/.benzatracker/refuels.json`
- GitHub Actions CI workflow
