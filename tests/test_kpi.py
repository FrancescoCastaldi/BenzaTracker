from __future__ import annotations

from datetime import date

from benzatracker.kpi import compute, monthly_spend
from benzatracker.models import RefuelEntry


def make_entry(day: int, liters: float, amount: float, price: float) -> RefuelEntry:
    return RefuelEntry(date(2024, day // 32 + 1, day % 32 or 1), liters, amount, price)


def test_compute_kpis_basic():
    entries = [
        RefuelEntry(date(2024, 1, 10), 40, 70, 1.75),
        RefuelEntry(date(2024, 2, 14), 35, 63, 1.8),
        RefuelEntry(date(2024, 2, 20), 42, 75.6, 1.8),
    ]

    report = compute(entries)

    assert report.total_spent == 208.6
    assert report.total_liters == 117.0
    assert report.average_price == round(208.6 / 117, 3)
    assert report.entries_count == 3
    assert report.average_monthly_spend == round((70 + 63 + 75.6) / 2, 2)
    assert report.best_price[1] == 1.75
    assert report.worst_price[1] == 1.8


def test_monthly_spend_orders_by_month():
    entries = [
        RefuelEntry(date(2024, 4, 10), 40, 70, 1.75),
        RefuelEntry(date(2024, 2, 14), 35, 63, 1.8),
        RefuelEntry(date(2024, 2, 20), 42, 75.6, 1.8),
    ]

    result = monthly_spend(entries)

    assert result[0][0] == date(2024, 2, 1)
    assert result[0][1] == 138.6
    assert result[1][0] == date(2024, 4, 1)
    assert result[1][1] == 70
