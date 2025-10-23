"""KPIs and aggregations for BenzaTracker."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Tuple

from .data_store import RefuelEntry


@dataclass
class KPIReport:
    total_spent: float
    total_liters: float
    average_price: float
    average_monthly_spend: float
    entries_count: int
    best_price: Tuple[date, float] | None
    worst_price: Tuple[date, float] | None
    total_distance_km: float
    average_km_per_liter: float | None
    average_liters_per_100km: float | None


def compute_kpis(entries: Iterable[RefuelEntry]) -> KPIReport:
    entries_list = list(entries)
    if not entries_list:
        return KPIReport(0.0, 0.0, 0.0, 0.0, 0, None, None, 0.0, None, None)

    total_spent = sum(entry.amount_paid for entry in entries_list)
    total_liters = sum(entry.liters for entry in entries_list)
    average_price = total_spent / total_liters if total_liters else 0.0

    (
        total_distance_km,
        distance_liters,
    ) = _distance_and_liters(entries_list)
    average_km_per_liter = (
        total_distance_km / distance_liters if distance_liters else None
    )
    average_liters_per_100km = (
        (distance_liters / total_distance_km) * 100
        if total_distance_km and distance_liters
        else None
    )

    monthly_totals = _aggregate_by_month(entries_list)
    average_monthly_spend = (
        sum(monthly_totals.values()) / len(monthly_totals) if monthly_totals else 0.0
    )

    prices = sorted(entries_list, key=lambda item: item.price_per_liter)
    best_price_entry = prices[0]
    worst_price_entry = prices[-1]

    return KPIReport(
        total_spent=round(total_spent, 2),
        total_liters=round(total_liters, 2),
        average_price=round(average_price, 3),
        average_monthly_spend=round(average_monthly_spend, 2),
        entries_count=len(entries_list),
        best_price=(best_price_entry.refuel_date, best_price_entry.price_per_liter),
        worst_price=(worst_price_entry.refuel_date, worst_price_entry.price_per_liter),
        total_distance_km=round(total_distance_km, 2),
        average_km_per_liter=round(average_km_per_liter, 2)
        if average_km_per_liter is not None
        else None,
        average_liters_per_100km=round(average_liters_per_100km, 2)
        if average_liters_per_100km is not None
        else None,
    )


def monthly_spend(entries: Iterable[RefuelEntry]) -> List[Tuple[date, float]]:
    aggregated = _aggregate_by_month(entries)
    return sorted(aggregated.items(), key=lambda item: item[0])


def _aggregate_by_month(entries: Iterable[RefuelEntry]) -> dict[date, float]:
    aggregated: dict[date, float] = defaultdict(float)
    for entry in entries:
        month_key = entry.refuel_date.replace(day=1)
        aggregated[month_key] += entry.amount_paid
    return dict(aggregated)


def _distance_and_liters(entries: Iterable[RefuelEntry]) -> tuple[float, float]:
    sorted_entries = sorted(entries, key=lambda item: item.refuel_date)
    total_distance = 0.0
    liters_tracked = 0.0
    previous_odometer: float | None = None

    for entry in sorted_entries:
        if entry.odometer_km is None:
            continue
        if previous_odometer is not None:
            delta = entry.odometer_km - previous_odometer
            if delta > 0:
                total_distance += delta
                liters_tracked += entry.liters
        previous_odometer = entry.odometer_km

    return total_distance, liters_tracked
