"""Tests for the SQLite persistence layer."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from benzatracker.models import RefuelEntry
from benzatracker.sqlite_store import SqliteStore


@pytest.fixture()
def db_store(tmp_path: Path) -> SqliteStore:
    return SqliteStore(db_path=tmp_path / "test.db")


def _entry(day: int) -> RefuelEntry:
    return RefuelEntry(
        refuel_date=date(2024, 1, day),
        liters=40.0,
        amount_paid=72.0,
        price_per_liter=1.8,
        station="Test",
    )


def test_save_and_load(db_store: SqliteStore) -> None:
    db_store.save_entries([_entry(1), _entry(15)])
    loaded = db_store.load_entries()
    assert len(loaded) == 2
    assert loaded[0].refuel_date == date(2024, 1, 1)
    assert loaded[1].refuel_date == date(2024, 1, 15)


def test_append_entry(db_store: SqliteStore) -> None:
    result = db_store.append_entry(_entry(10))
    assert len(result) == 1
    assert result[0].liters == 40.0


def test_delete_entry(db_store: SqliteStore) -> None:
    db_store.save_entries([_entry(1), _entry(2), _entry(3)])
    remaining = db_store.delete_entry(1)
    assert len(remaining) == 2
    assert remaining[0].refuel_date.day == 1
    assert remaining[1].refuel_date.day == 3


def test_delete_entry_raises_on_invalid(db_store: SqliteStore) -> None:
    with pytest.raises(IndexError):
        db_store.delete_entry(0)


def test_update_odometer(db_store: SqliteStore) -> None:
    db_store.save_entries([_entry(1)])
    updated = db_store.update_odometer(0, 50000.0)
    assert updated.odometer_km == 50000.0
    reloaded = db_store.load_entries()[0]
    assert reloaded.odometer_km == 50000.0


def test_update_odometer_to_none(db_store: SqliteStore) -> None:
    db_store.save_entries([_entry(1)])
    db_store.update_odometer(0, 100.0)
    updated = db_store.update_odometer(0, None)
    assert updated.odometer_km is None


def test_multiple_appends_preserve_order(db_store: SqliteStore) -> None:
    db_store.append_entry(_entry(3))
    db_store.append_entry(_entry(1))
    db_store.append_entry(_entry(2))
    entries = db_store.load_entries()
    assert [e.refuel_date.day for e in entries] == [3, 1, 2]


def test_create_store_factory_returns_sqlite_store(tmp_path: Path) -> None:
    from benzatracker.store import create_store

    store = create_store(str(tmp_path))
    assert isinstance(store, SqliteStore)
    store.close()
