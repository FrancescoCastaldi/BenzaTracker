"""SQLite persistence for BenzaTracker.

Drop-in replacement for :class:`JsonStore` using a local SQLite database.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from . import config
from .models import DATE_FORMAT, RefuelEntry


class SqliteStore:
    """Persist refuel entries in a local SQLite database."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or config.get_default_sqlite_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._migrate()

    # ── schema ──────────────────────────────────────────────────────────────

    def _migrate(self) -> None:
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS refuels ("
            "  id            INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  refuel_date   TEXT    NOT NULL,"
            "  liters        REAL    NOT NULL,"
            "  amount_paid   REAL    NOT NULL,"
            "  price_per_liter REAL  NOT NULL,"
            "  station       TEXT,"
            "  odometer_km   REAL"
            ")"
        )
        self._conn.commit()

    # ── public API ──────────────────────────────────────────────────────────

    def load_entries(self) -> List[RefuelEntry]:
        rows = self._conn.execute(
            "SELECT * FROM refuels ORDER BY rowid"
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def save_entries(self, entries: Iterable[RefuelEntry]) -> None:
        self._conn.execute("DELETE FROM refuels")
        self._insert_many(entries)
        self._conn.commit()

    def append_entry(self, entry: RefuelEntry) -> List[RefuelEntry]:
        self._insert_one(entry)
        self._conn.commit()
        return self.load_entries()

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

    def close(self) -> None:
        self._conn.close()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _row_to_entry(self, row: sqlite3.Row) -> RefuelEntry:
        return RefuelEntry(
            refuel_date=datetime.strptime(row["refuel_date"], DATE_FORMAT).date(),
            liters=row["liters"],
            amount_paid=row["amount_paid"],
            price_per_liter=row["price_per_liter"],
            station=row["station"],
            odometer_km=row["odometer_km"],
        )

    def _insert_one(self, entry: RefuelEntry) -> None:
        self._conn.execute(
            "INSERT INTO refuels "
            "(refuel_date, liters, amount_paid, price_per_liter, station, odometer_km) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                entry.refuel_date.strftime(DATE_FORMAT),
                entry.liters,
                entry.amount_paid,
                entry.price_per_liter,
                entry.station,
                entry.odometer_km,
            ),
        )

    def _insert_many(self, entries: Iterable[RefuelEntry]) -> None:
        rows = [
            (
                e.refuel_date.strftime(DATE_FORMAT),
                e.liters,
                e.amount_paid,
                e.price_per_liter,
                e.station,
                e.odometer_km,
            )
            for e in entries
        ]
        self._conn.executemany(
            "INSERT INTO refuels "
            "(refuel_date, liters, amount_paid, price_per_liter, station, odometer_km) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
