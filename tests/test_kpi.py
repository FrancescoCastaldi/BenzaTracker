from datetime import date

from benzatracker.data_store import RefuelEntry
from benzatracker.kpi import compute_kpis, monthly_spend


def test_compute_kpis_basic():
    entries = [
        RefuelEntry(date(2024, 1, 10), 40, 70, 1.75, odometer_km=10000),
        RefuelEntry(date(2024, 2, 14), 35, 63, 1.8, odometer_km=10350),
        RefuelEntry(date(2024, 2, 20), 42, 75.6, 1.8, odometer_km=10780),
    ]

    report = compute_kpis(entries)

    assert report.total_spent == 208.6
    assert report.total_liters == 117.0
    assert report.average_price == round(208.6 / 117, 3)
    assert report.entries_count == 3
    assert report.average_monthly_spend == round((70 + 63 + 75.6) / 2, 2)
    assert report.best_price[1] == 1.75
    assert report.worst_price[1] == 1.8
    assert report.total_distance_km == 780.0
    assert report.average_km_per_liter == 10.13
    assert report.average_liters_per_100km == 9.87


def test_compute_kpis_without_odometer_data():
    entries = [
        RefuelEntry(date(2024, 1, 10), 40, 70, 1.75),
        RefuelEntry(date(2024, 2, 14), 35, 63, 1.8),
    ]

    report = compute_kpis(entries)

    assert report.total_distance_km == 0.0
    assert report.average_km_per_liter is None
    assert report.average_liters_per_100km is None


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
