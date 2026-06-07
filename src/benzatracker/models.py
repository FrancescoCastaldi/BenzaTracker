"""Domain models for BenzaTracker."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Tuple

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class RefuelEntry:
    """Represent a single refuel event."""

    refuel_date: date
    liters: float
    amount_paid: float
    price_per_liter: float
    station: str | None = None
    odometer_km: float | None = None

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

        odometer_raw = payload.get("odometer_km")
        odometer_km = float(odometer_raw) if odometer_raw is not None else None

        return cls(
            refuel_date=datetime.strptime(payload["refuel_date"], DATE_FORMAT).date(),
            liters=liters,
            amount_paid=amount_paid,
            price_per_liter=price_per_liter,
            station=payload.get("station") or None,
            odometer_km=odometer_km,
        )


@dataclass
class KPIReport:
    """Aggregated statistics computed from a collection of refuel entries."""

    total_spent: float
    total_liters: float
    average_price: float
    average_monthly_spend: float
    entries_count: int
    best_price: Tuple[date, float] | None
    worst_price: Tuple[date, float] | None
