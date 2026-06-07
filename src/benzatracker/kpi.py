"""KPI computations and aggregations."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, List, Tuple

from .models import KPIReport, RefuelEntry


def compute(entries: Iterable[RefuelEntry]) -> KPIReport:
    """Compute aggregate KPIs from refuel entries."""
    entries_list = list(entries)
    if not entries_list:
        return KPIReport(0.0, 0.0, 0.0, 0.0, 0, None, None)

    total_spent = sum(entry.amount_paid for entry in entries_list)
    total_liters = sum(entry.liters for entry in entries_list)
    average_price = total_spent / total_liters if total_liters else 0.0

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
    )


def monthly_spend(entries: Iterable[RefuelEntry]) -> List[Tuple[date, float]]:
    """Return sorted list of ``(month, total_spent)`` pairs."""
    aggregated = _aggregate_by_month(entries)
    return sorted(aggregated.items(), key=lambda item: item[0])


def _aggregate_by_month(entries: Iterable[RefuelEntry]) -> dict[date, float]:
    aggregated: dict[date, float] = defaultdict(float)
    for entry in entries:
        month_key = entry.refuel_date.replace(day=1)
        aggregated[month_key] += entry.amount_paid
    return dict(aggregated)
