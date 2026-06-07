# BenzaTracker Launch Guide

A complete reference for installing and running BenzaTracker in any mode:
**Web**, **GUI** (desktop), or **CLI** (terminal).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Install (pip)](#quick-install-pip)
  - [Editable Install (development)](#editable-install-development)
  - [Docker (recommended for Web)](#docker-recommended-for-web)
- [Running the Application](#running-the-application)
  - [Web Interface (Flask)](#web-interface-flask)
  - [Graphical Interface (ttkbootstrap)](#graphical-interface-ttkbootstrap)
  - [Command-Line Interface](#command-line-interface)
  - [Unified Entry Point](#unified-entry-point)
- [Environment Variables](#environment-variables)
  - [DATA_DIR](#data_dir)
  - [BENZA_WEB](#benza_web)
- [Data Persistence](#data-persistence)
  - [JSON Mode (default)](#json-mode-default)
  - [SQLite Mode](#sqlite-mode)
- [Verifying the Installation](#verifying-the-installation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.10+** | Check with `python --version` or `python3 --version` |
| **pip** | Comes with Python 3.10+ |
| **Docker** | Only needed for the Docker method (optional) |

---

## Installation

Choose one of the following methods.

### Quick Install (pip)

```bash
# Clone the repository
git clone https://github.com/FrancescoCastaldi/BenzaTracker.git
cd BenzaTracker

# (Recommended) Create and activate a virtual environment
python -m venv .venv

# On macOS / Linux:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt
```

> **What gets installed:** `matplotlib`, `ttkbootstrap`, `reportlab`, `flask`.

### Editable Install (development)

This makes the `benzatracker` package importable from anywhere and picks up
changes automatically:

```bash
pip install -e .
```

After this, you can also use the entry-point shortcuts:

```bash
benzatracker       # runs CLI
benzatracker-gui   # runs GUI
benzatracker-web   # runs Web (Flask)
```

### Docker (recommended for Web)

```bash
# Build and start the container
docker compose up -d

# Open in your browser
# → http://localhost:5000
```

To stop:

```bash
docker compose down
```

Data persists in `./data/` (a SQLite database on your host machine).

---

## Running the Application

### Web Interface (Flask)

The web UI provides a full dashboard with KPI cards, a monthly spend chart,
a CRUD table for refuel entries, and one-click PDF export.

```bash
# Make sure you're in the project directory with dependencies installed
python -m benzatracker.web
```

Then open **http://localhost:5000** in your browser.

**With SQLite persistence:**

```bash
DATA_DIR=./data python -m benzatracker.web
```

**With a custom port:**

The Flask dev server defaults to port 5000. To change it, edit the
`app.run()` call in `src/benzatracker/web.py`, or set the environment
variable before launching:

```bash
# Windows PowerShell
$env:FLASK_RUN_PORT = 8080; python -m benzatracker.web

# macOS / Linux
FLASK_RUN_PORT=8080 python -m benzatracker.web
```

> **Note:** The web interface uses the `darkly` Bootstrap 5.3 theme and
> is mobile-responsive.

### Graphical Interface (ttkbootstrap)

The GUI provides a native desktop window with a form to add refuels, a
KPI summary panel, a sortable table of all entries, a matplotlib bar
chart, and a button to export a PDF report.

```bash
python -m benzatracker.gui
```

**Important:** The GUI requires a display server.

- **Windows / macOS:** works out of the box.
- **Linux:** requires `tkinter` and a display (X11/Wayland). On headless
  servers, use `xvfb`:

  ```bash
  sudo apt-get install xvfb
  xvfb-run python -m benzatracker.gui
  ```

> **Note:** The GUI persists data as JSON in
> `~/.benzatracker/refuels.json` by default (see
> [Data Persistence](#data-persistence)).

### Command-Line Interface

The CLI is text-based and reads from standard input. It supports adding
entries one at a time, listing all entries, showing KPI statistics, and
exporting a PDF report.

```bash
python -m benzatracker.cli
```

**CLI commands:**

| Prompt action | What happens |
|---|---|
| Add a refuel | Enter date, liters, amount, price, station |
| Show stats | Prints KPI summary (total spent, avg price, etc.) |
| List entries | Shows all refuel entries in a table |
| Export PDF | Generates a PDF report and saves it to disk |
| Quit | Exits the program |

### Unified Entry Point

The `__main__.py` module provides a single command that dispatches to the
right interface based on flags or environment variables:

```bash
# Run CLI (default)
python -m benzatracker

# Run GUI
python -m benzatracker --gui

# Run Web
BENZA_WEB=1 python -m benzatracker
```

This is the recommended way if you want one command that works everywhere.

---

## Environment Variables

### `DATA_DIR`

Controls the storage backend.

| Value | Backend | Database location |
|---|---|---|
| **unset / empty** | JSON | `~/.benzatracker/refuels.json` |
| **any path** | SQLite | `{DATA_DIR}/refuels.db` |

Examples:

```bash
# Use JSON (default)
python -m benzatracker.web

# Use SQLite, store database in ./data/
DATA_DIR=./data python -m benzatracker.web

# Use SQLite, store in /tmp/my_data/
DATA_DIR=/tmp/my_data python -m benzatracker.web
```

### `BENZA_WEB`

When set to any non-empty value, the unified entry point
(`python -m benzatracker`) launches the web interface instead of the CLI.

```bash
BENZA_WEB=1 python -m benzatracker
```

This is equivalent to `python -m benzatracker.web`.

---

## Data Persistence

### JSON Mode (default)

- **Storage:** `~/.benzatracker/refuels.json`
- **Safety:** Uses atomic writes (write to temp file, then rename) —
  no data loss if the process crashes mid-write.
- **When to use:** Local desktop use, manual backups, no Docker.

### SQLite Mode

- **Storage:** `{DATA_DIR}/refuels.db` (when `DATA_DIR` is set)
- **Safety:** SQLite transactional writes — ACID compliant.
- **When to use:** Docker deployments, multi-user web access, when you
  need concurrent reads/writes.

> **Migration:** There is no automatic migration path between JSON and
> SQLite. Choose one mode and stick with it.

---

## Verifying the Installation

Run the test suite to confirm everything is set up correctly:

```bash
pip install pytest
pytest -v --tb=short
```

Expected output:

```
tests/test_cli_windows.py::test_build_tenth_windows_mid_month PASSED
tests/test_cli_windows.py::test_build_tenth_windows_year_boundary PASSED
tests/test_cli_windows.py::test_build_tenth_windows_exact_tenth PASSED
tests/test_data_store.py::test_save_and_load_roundtrip PASSED
tests/test_data_store.py::test_append_entry PASSED
tests/test_data_store.py::test_delete_entry_removes_selected_item PASSED
tests/test_data_store.py::test_delete_entry_raises_on_invalid_index PASSED
tests/test_data_store.py::test_update_odometer_updates_value PASSED
tests/test_data_store.py::test_update_odometer_accepts_none PASSED
tests/test_data_store.py::test_update_odometer_raises_on_invalid_index PASSED
tests/test_data_store.py::test_from_dict_validates_negative_liters PASSED
tests/test_database.py::test_save_and_load PASSED
tests/test_database.py::test_append_entry PASSED
tests/test_database.py::test_delete_entry PASSED
tests/test_database.py::test_delete_entry_raises_on_invalid PASSED
tests/test_database.py::test_update_odometer PASSED
tests/test_database.py::test_update_odometer_to_none PASSED
tests/test_database.py::test_multiple_appends_preserve_order PASSED
tests/test_database.py::test_create_store_factory_returns_sqlite_store PASSED
tests/test_kpi.py::test_compute_kpis_basic PASSED
tests/test_kpi.py::test_monthly_spend_orders_by_month PASSED

==================== 21 passed in 0.26s =====================
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'benzatracker'"

The package isn't installed. Run:

```bash
pip install -e .
```

This adds `src/` to Python's module search path.

### "Import 'benzatracker.X' could not be resolved" (in IDE)

Your IDE's Python interpreter doesn't know about the `src/` layout.
Configure it to add `src/` to the Python path, or run:

```bash
pip install -e .
```

### "ttkbootstrap not found" / "flask not found"

Install missing dependencies:

```bash
pip install -r requirements.txt
```

### "tkinter not found" (Linux)

Install the `tkinter` system package:

```bash
# Debian / Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### "No display" when running the GUI (Linux headless)

Use a virtual framebuffer:

```bash
sudo apt-get install xvfb
xvfb-run python -m benzatracker.gui
```

Or use the web interface instead (no display needed):

```bash
DATA_DIR=./data python -m benzatracker.web
```

### Docker: "port 5000 already in use"

Either stop the existing process or change the port mapping:

```yaml
# docker-compose.yml
ports:
  - "8080:5000"   # host:8080 → container:5000
```

Then access **http://localhost:8080**.

### "No data" message in the web UI

You haven't added any refuel entries yet. Navigate to
**http://localhost:5000/entries** and use the form to add your first
refuel.

### PDF export fails with "reportlab not found"

Install ReportLab:

```bash
pip install reportlab>=4.0.0
```

### Data is lost between runs

- **JSON mode:** Check that `~/.benzatracker/refuels.json` exists.
- **SQLite mode:** Make sure `DATA_DIR` points to a persistent location
  (not a temporary directory). In Docker, verify the volume is mounted:
  `docker compose ps` should show the volume.

---

For further help, open an issue on
[GitHub](https://github.com/FrancescoCastaldi/BenzaTracker).
