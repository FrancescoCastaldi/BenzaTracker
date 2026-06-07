"""Command-line interface for BenzaTracker."""
from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Callable, List

from typing import List, Tuple

from . import config
from .kpi import compute, monthly_spend
from .models import DATE_FORMAT, RefuelEntry
from .pdf import ReportGenerator
from .store import create_store


_MONTH_ABBR: List[str] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _add_months(source: date, months: int) -> date:
    """Add months to a date, always landing on the 10th."""
    total_months = source.month - 1 + months
    year = source.year + total_months // 12
    month = total_months % 12 + 1
    return date(year, month, 10)


def build_tenth_windows(ref: date) -> List[Tuple[str, date, date]]:
    """Build 3 ten-day windows (10th-to-10th) centred on the reference month."""
    base = date(ref.year, ref.month, 10)
    windows: List[Tuple[str, date, date]] = []
    for offset in range(-1, 2):
        start = _add_months(base, offset)
        end = _add_months(base, offset + 1)
        label = f"10 {_MONTH_ABBR[start.month - 1]}"
        windows.append((label, start, end))
    return windows


# ── helpers ──────────────────────────────────────────────────────────────────


def _prompt_date(message: str) -> date:
    while True:
        raw = input(f"{message} ({DATE_FORMAT}): ").strip()
        if not raw:
            print("Date is required.")
            continue
        try:
            return datetime.strptime(raw, DATE_FORMAT).date()
        except ValueError:
            print("Invalid date format. Try again.")


def _prompt_float(message: str, minimum: float = 0.0) -> float:
    while True:
        raw = input(f"{message}: ").replace(",", ".").strip()
        try:
            value = float(raw)
        except ValueError:
            print("Enter a valid number.")
            continue
        if value <= minimum:
            print("Value must be greater than zero.")
            continue
        return value


def _prompt_optional(message: str) -> str | None:
    raw = input(f"{message} (optional): ").strip()
    return raw or None


def _prompt_int(message: str, max_val: int) -> int:
    while True:
        raw = input(f"{message}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Enter a valid number.")
            continue
        if value < 0 or value > max_val:
            print(f"Enter a number between 0 and {max_val}.")
            continue
        return value


def _print_header(title: str) -> None:
    print(f"\n--- {title} ---")


# ── actions ──────────────────────────────────────────────────────────────────


def _add_entry(store) -> None:
    _print_header("New refuel")
    refuel_date = _prompt_date("Refuel date")
    liters = _prompt_float("Liters")
    amount_paid = _prompt_float("Amount paid")
    odometer = _prompt_optional("Odometer (km)")
    station = _prompt_optional("Station")
    price_per_liter = round(amount_paid / liters, 3)
    entry = RefuelEntry(
        refuel_date=refuel_date,
        liters=liters,
        amount_paid=amount_paid,
        price_per_liter=price_per_liter,
        station=station,
        odometer_km=float(odometer) if odometer else None,
    )
    store.append_entry(entry)
    print("Refuel saved successfully.\n")


def _show_kpis(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNo refuels recorded.\n")
        return
    report = compute(entries)
    _print_header("KPI summary")
    print(f"  Total spent:       \u20ac {report.total_spent:.2f}")
    print(f"  Total liters:      {report.total_liters:.2f} L")
    print(f"  Average price:     \u20ac {report.average_price:.3f}/L")
    print(f"  Avg monthly spend: \u20ac {report.average_monthly_spend:.2f}")
    print(f"  Refuels recorded:  {report.entries_count}")
    if report.best_price:
        d, p = report.best_price
        print(f"  Best price:        \u20ac {p:.3f}/L on {d.strftime(DATE_FORMAT)}")
    if report.worst_price:
        d, p = report.worst_price
        print(f"  Worst price:       \u20ac {p:.3f}/L on {d.strftime(DATE_FORMAT)}")
    print()


def _list_entries(store) -> None:
    entries = sorted(store.load_entries(), key=lambda e: e.refuel_date)
    if not entries:
        print("\nNo refuels recorded.\n")
        return
    _print_header("Refuel history")
    for i, entry in enumerate(entries):
        date_str = entry.refuel_date.strftime(DATE_FORMAT)
        station = entry.station or "-"
        odo = f"{entry.odometer_km:.0f} km" if entry.odometer_km else "-"
        print(
            f"  [{i}] {date_str} | {entry.liters:.2f} L | "
            f"\u20ac {entry.amount_paid:.2f} | \u20ac {entry.price_per_liter:.3f}/L | "
            f"{station} | {odo}"
        )
    print()


def _show_monthly_spend(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNo refuels recorded.\n")
        return
    _print_header("Monthly spend")
    for month, total in monthly_spend(entries):
        print(f"  {month.strftime('%Y-%m')}  ->  \u20ac {total:.2f}")
    print()


def _delete_entry(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNo refuels to delete.\n")
        return
    _list_entries(store)
    print("Enter the [index] of the entry to delete, or leave empty to cancel.")
    idx = _prompt_int("Index", len(entries) - 1)
    confirm = input(f"Delete entry [{idx}]? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.\n")
        return
    try:
        store.delete_entry(idx)
        print("Entry deleted.\n")
    except IndexError:
        print("Invalid index.\n")


def _export_csv(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNo data to export.\n")
        return
    path = input("Output file (default: benzatracker_export.csv): ").strip()
    filepath = Path(path) if path else Path("benzatracker_export.csv")
    try:
        with filepath.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Liters", "Amount", "Price/L", "Station", "Odometer (km)"])
            for e in sorted(entries, key=lambda x: x.refuel_date):
                writer.writerow([
                    e.refuel_date.strftime(DATE_FORMAT),
                    e.liters,
                    e.amount_paid,
                    e.price_per_liter,
                    e.station or "",
                    e.odometer_km or "",
                ])
        print(f"CSV exported to {filepath}\n")
    except OSError as exc:
        print(f"Error writing file: {exc}\n")


def _export_pdf(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNo data to export.\n")
        return
    path = input("Output file (default: benzatracker_report.pdf): ").strip()
    filepath = Path(path) if path else Path("benzatracker_report.pdf")
    try:
        ReportGenerator(filepath).generate(entries)
        print(f"PDF exported to {filepath}\n")
    except Exception as exc:
        print(f"Error exporting PDF: {exc}\n")


# ── entry point ──────────────────────────────────────────────────────────────


def run() -> None:
    store = create_store(config.get_data_dir())
    actions: dict[str, tuple[str, Callable]] = {
        "1": ("Add refuel", _add_entry),
        "2": ("Show KPIs", _show_kpis),
        "3": ("List refuels", _list_entries),
        "4": ("Monthly spend", _show_monthly_spend),
        "5": ("Delete refuel", _delete_entry),
        "6": ("Export CSV", _export_csv),
        "7": ("Export PDF", _export_pdf),
        "8": ("Exit", lambda _: None),
    }
    while True:
        print("BenzaTracker CLI")
        for key, (label, _) in actions.items():
            print(f"  [{key}] {label}")
        choice = input("Select an option: ").strip()
        if choice == "8":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if not action:
            print("Invalid option. Try again.\n")
            continue
        action[1](store)
