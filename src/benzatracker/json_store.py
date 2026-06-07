"""JSON-file persistence for BenzaTracker.

Writes to ``~/.benzatracker/refuels.json`` using atomic write semantics.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, List

from . import config
from .models import DATE_FORMAT, RefuelEntry


class JsonStore:
    """Load / save refuel entries to a local JSON file with atomic writes."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or config.get_default_db_path()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_entries(self) -> List[RefuelEntry]:
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [RefuelEntry.from_dict(item) for item in payload]

    def save_entries(self, entries: Iterable[RefuelEntry]) -> None:
        serialised = [entry.to_dict() for entry in entries]
        dir_ = self.storage_path.parent
        fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(serialised, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.storage_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def append_entry(self, entry: RefuelEntry) -> List[RefuelEntry]:
        entries = self.load_entries()
        entries.append(entry)
        self.save_entries(entries)
        return entries

    def delete_entry(self, index: int) -> List[RefuelEntry]:
        entries = self.load_entries()
        try:
            entries.pop(index)
        except IndexError:
            raise IndexError(
                f"Entry index {index} out of range (0-{len(entries) - 1})"
            )
        self.save_entries(entries)
        return entries

    def update_odometer(
        self, index: int, odometer: float | None
    ) -> RefuelEntry:
        entries = self.load_entries()
        try:
            entry = entries[index]
        except IndexError:
            raise IndexError(
                f"Entry index {index} out of range (0-{len(entries) - 1})"
            )
        entry.odometer_km = odometer
        self.save_entries(entries)
        return entry
