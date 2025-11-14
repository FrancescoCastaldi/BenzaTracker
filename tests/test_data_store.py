from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from benzatracker.data_store import DataStore, RefuelEntry


@pytest.fixture()
def temp_store(tmp_path: Path) -> DataStore:
    storage = tmp_path / "refuels.json"
    return DataStore(storage_path=storage)


def _sample_entry(day: int, odometer: float | None = None) -> RefuelEntry:
    return RefuelEntry(
        refuel_date=date(2024, 1, day),
        liters=40.0,
        amount_paid=72.0,
        price_per_liter=1.8,
        station="Test",
        odometer_km=odometer,
    )


def test_delete_entry_removes_selected_item(temp_store: DataStore) -> None:
    temp_store.save_entries([_sample_entry(1), _sample_entry(2), _sample_entry(3)])

    remaining = temp_store.delete_entry(1)

    assert len(remaining) == 2
    assert remaining[0].refuel_date.day == 1
    assert remaining[1].refuel_date.day == 3


def test_update_odometer_updates_value(temp_store: DataStore) -> None:
    temp_store.save_entries([_sample_entry(1, None)])

    updated = temp_store.update_odometer(0, 12345.0)

    assert updated.odometer_km == 12345.0
    reloaded = temp_store.load_entries()[0]
    assert reloaded.odometer_km == 12345.0


def test_update_odometer_accepts_none(temp_store: DataStore) -> None:
    temp_store.save_entries([_sample_entry(1, 9000.0)])

    updated = temp_store.update_odometer(0, None)

    assert updated.odometer_km is None
    assert temp_store.load_entries()[0].odometer_km is None


def test_last_updated_returns_none_without_file(temp_store: DataStore) -> None:
    assert temp_store.last_updated_at() is None


def test_last_updated_reports_recent_timestamp(temp_store: DataStore) -> None:
    temp_store.append_entry(_sample_entry(5))

    timestamp = temp_store.last_updated_at()

    assert timestamp is not None
    assert timestamp >= datetime.now() - timedelta(minutes=1)


def test_photo_management_import_and_delete(temp_store: DataStore, tmp_path: Path) -> None:
    image_path = tmp_path / "sample.jpg"
    image_path.write_bytes(b"fake-image")

    identifier = temp_store.import_photo(image_path)
    stored = temp_store.resolve_photo_path(identifier)

    assert stored.exists()

    entry = _sample_entry(7)
    entry.photo_path = identifier
    temp_store.save_entries([entry])

    temp_store.delete_entry(0)

    assert not stored.exists()
