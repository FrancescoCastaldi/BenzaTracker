"""Storage abstraction layer.

Defines the ``Store`` protocol and the ``create_store`` factory.
Use ``create_store()`` to get a store backed by either JSON or SQLite.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Protocol

from . import config
from .models import RefuelEntry


class Store(Protocol):
    """Interface shared by all persistence backends."""

    def load_entries(self) -> List[RefuelEntry]:
        ...

    def save_entries(self, entries: Iterable[RefuelEntry]) -> None:
        ...

    def append_entry(self, entry: RefuelEntry) -> List[RefuelEntry]:
        ...

    def delete_entry(self, index: int) -> List[RefuelEntry]:
        ...

    def update_odometer(self, index: int, odometer: float | None) -> RefuelEntry:
        ...


def create_store(data_dir: str | None = None) -> Store:
    """Return a :class:`Store` backed by JSON or SQLite.

    When *data_dir* is set, a :class:`.SqliteStore` is returned with the
    database file stored under *data_dir*.  Otherwise a
    :class:`.JsonStore` (JSON file under ``~/.benzatracker/``) is returned.
    """
    if data_dir is not None:
        from .sqlite_store import SqliteStore

        db_path = Path(data_dir) / "benzatracker.db"
        return SqliteStore(db_path)
    return JsonStore()


# ── Import here to avoid circular deps ──────────────────────────────────────
from .json_store import JsonStore  # noqa: E402
from .sqlite_store import SqliteStore  # noqa: E402
