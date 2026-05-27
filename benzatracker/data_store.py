"""Data persistence layer for BenzaTracker."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class RefuelEntry:
    """Represent a single refuel event."""

    refuel_date: date
    liters: float
    amount_paid: float
    price_per_liter: float
    station: str | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["refuel_date"] = self.refuel_date.strftime(DATE_FORMAT)
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> "RefuelEntry":
        liters = float(payload["liters"])
        amount_paid = float(payload["amount_paid"])
        price_per_liter = float(payload["price_per_liter"])

        if liters <= 0:
            raise ValueError(f"liters must be positive, got {liters}")
        if amount_paid < 0:
            raise ValueError(f"amount_paid must be non-negative, got {amount_paid}")
        if price_per_liter < 0:
            raise ValueError(
                f"price_per_liter must be non-negative, got {price_per_liter}"
            )

        return cls(
            refuel_date=datetime.strptime(payload["refuel_date"], DATE_FORMAT).date(),
            liters=liters,
            amount_paid=amount_paid,
            price_per_liter=price_per_liter,
            station=payload.get("station") or None,
        )


class DataStore:
    """Handle loading and storing refuel entries."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = (
            storage_path or Path.home() / ".benzatracker" / "refuels.json"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load_entries(self) -> List[RefuelEntry]:
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [RefuelEntry.from_dict(item) for item in payload]

    def save_entries(self, entries: Iterable[RefuelEntry]) -> None:
        """Persist entries using an atomic write to prevent data corruption.

        Writes to a temporary file in the same directory, then renames it
        over the target path. On POSIX systems os.replace() is atomic;
        on Windows it is best-effort (os.replace raises if the target is
        locked, so no silent data loss occurs).
        """
        serialised = [entry.to_dict() for entry in entries]
        dir_ = self.storage_path.parent
        fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(serialised, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.storage_path)
        except Exception:
            # Clean up the temp file if anything went wrong before the rename.
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
