"""Central configuration, sourced from environment variables."""
from __future__ import annotations

import os
from pathlib import Path


def get_data_dir() -> str | None:
    """Return the ``DATA_DIR`` env var, or ``None`` to use the default path."""
    return os.environ.get("DATA_DIR")


def get_default_db_path() -> Path:
    """Return the default storage path under the user home directory."""
    return Path.home() / ".benzatracker" / "refuels.json"


def get_default_sqlite_path() -> Path:
    """Return the default SQLite path under the user home directory."""
    return Path.home() / ".benzatracker" / "refuels.db"
