from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from benzatracker.json_store import JsonStore
from benzatracker.models import RefuelEntry


@pytest.fixture()
def temp_store(tmp_path: Path) -> JsonStore:
    storage = tmp_path / "refuels.json"
    return JsonStore(storage_path=storage)


def _sample_entry(day: int) -> RefuelEntry:
    return RefuelEntry(
        refuel_date=date(2024, 1, day),
        liters=40.0,
        amount_paid=72.0,
        price_per_liter=1.8,
        station="Test",
    )


def test_save_and_load_roundtrip(temp_store: JsonStore) -> None:
    entries = [_sample_entry(1), _sample_entry(15)]
    temp_store.save_entries(entries)
    loaded = temp_store.load_entries()
    assert len(loaded) == 2
    assert loaded[0].liters == 40.0


def test_append_entry(temp_store: JsonStore) -> None:
    entry = _sample_entry(10)
    result = temp_store.append_entry(entry)
    assert len(result) == 1
    assert result[0].refuel_date == date(2024, 1, 10)


def test_delete_entry_removes_selected_item(temp_store: JsonStore) -> None:
    temp_store.save_entries([_sample_entry(1), _sample_entry(2), _sample_entry(3)])

    remaining = temp_store.delete_entry(1)

    assert len(remaining) == 2
    assert remaining[0].refuel_date.day == 1
    assert remaining[1].refuel_date.day == 3


def test_delete_entry_raises_on_invalid_index(temp_store: JsonStore) -> None:
    with pytest.raises(IndexError):
        temp_store.delete_entry(0)


def test_update_odometer_updates_value(temp_store: JsonStore) -> None:
    temp_store.save_entries([_sample_entry(1)])

    updated = temp_store.update_odometer(0, 12345.0)

    assert updated.odometer_km == 12345.0
    reloaded = temp_store.load_entries()[0]
    assert reloaded.odometer_km == 12345.0


def test_update_odometer_accepts_none(temp_store: JsonStore) -> None:
    temp_store.save_entries([_sample_entry(1)])

    updated = temp_store.update_odometer(0, None)

    assert updated.odometer_km is None
    assert temp_store.load_entries()[0].odometer_km is None


def test_update_odometer_raises_on_invalid_index(temp_store: JsonStore) -> None:
    with pytest.raises(IndexError):
        temp_store.update_odometer(99, 100.0)


def test_from_dict_validates_negative_liters(temp_store: JsonStore) -> None:
    with pytest.raises(ValueError, match="liters must be positive"):
        RefuelEntry.from_dict({
            "refuel_date": "2024-01-10",
            "liters": "-5",
            "amount_paid": "10",
            "price_per_liter": "2",
        })
