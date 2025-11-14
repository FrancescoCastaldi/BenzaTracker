"""Data persistence layer for BenzaTracker."""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List
import json
import shutil
import uuid

DATE_FORMAT = "%Y-%m-%d"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
EXAMPLE_TIMESTAMP_DISPLAY = datetime(2024, 7, 15, 18, 42).strftime(TIMESTAMP_FORMAT)


@dataclass
class RefuelEntry:
    """Represent a single refuel event."""

    refuel_date: date
    liters: float
    amount_paid: float
    price_per_liter: float
    station: str | None = None
    odometer_km: float | None = None
    photo_path: str | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["refuel_date"] = self.refuel_date.strftime(DATE_FORMAT)
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> "RefuelEntry":
        odometer_value = payload.get("odometer_km")
        return cls(
            refuel_date=datetime.strptime(payload["refuel_date"], DATE_FORMAT).date(),
            liters=float(payload["liters"]),
            amount_paid=float(payload["amount_paid"]),
            price_per_liter=float(payload["price_per_liter"]),
            station=payload.get("station") or None,
            odometer_km=float(odometer_value) if odometer_value is not None else None,
            photo_path=payload.get("photo_path") or None,
        )


class DataStore:
    """Handle loading and storing refuel entries."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or Path.home() / ".benzatracker" / "refuels.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.photos_dir = self.storage_path.parent / "photos"
        self.photos_dir.mkdir(parents=True, exist_ok=True)

    def load_entries(self) -> List[RefuelEntry]:
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [RefuelEntry.from_dict(item) for item in payload]

    def save_entries(self, entries: Iterable[RefuelEntry]) -> None:
        serialised = [entry.to_dict() for entry in entries]
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(serialised, handle, ensure_ascii=False, indent=2)

    def append_entry(self, entry: RefuelEntry) -> List[RefuelEntry]:
        entries = self.load_entries()
        entries.append(entry)
        self.save_entries(entries)
        return entries

    def delete_entry(self, index: int) -> List[RefuelEntry]:
        entries = self.load_entries()
        if index < 0 or index >= len(entries):
            raise IndexError("Indice fuori dall'intervallo disponibile")
        removed = entries.pop(index)
        if removed.photo_path:
            self._delete_photo_file(removed.photo_path)
        self.save_entries(entries)
        return entries

    def update_odometer(self, index: int, odometer_km: float | None) -> RefuelEntry:
        entries = self.load_entries()
        if index < 0 or index >= len(entries):
            raise IndexError("Indice fuori dall'intervallo disponibile")
        updated = replace(entries[index], odometer_km=odometer_km)
        entries[index] = updated
        self.save_entries(entries)
        return updated

    def last_updated_at(self) -> datetime | None:
        """Return the last modification timestamp of the storage file."""

        if not self.storage_path.exists():
            return None
        return datetime.fromtimestamp(self.storage_path.stat().st_mtime)

    # ------------------------------------------------------------------
    # Photo management
    # ------------------------------------------------------------------
    def import_photo(self, source: str | Path) -> str:
        """Copy a photo into the managed directory and return its identifier."""

        source_path = Path(source).expanduser()
        if not source_path.exists():
            raise FileNotFoundError(f"Foto non trovata: {source_path}")

        extension = source_path.suffix.lower()
        name = f"{uuid.uuid4().hex}{extension}"
        destination = self.photos_dir / name
        shutil.copy2(source_path, destination)
        return name

    def resolve_photo_path(self, identifier: str) -> Path:
        """Return the absolute path for a stored photo identifier."""

        return (self.photos_dir / identifier).resolve()

    def _delete_photo_file(self, identifier: str) -> None:
        """Remove the stored photo if it still exists on disk."""

        photo_path = self.photos_dir / identifier
        try:
            photo_path.unlink()
        except FileNotFoundError:
            pass
