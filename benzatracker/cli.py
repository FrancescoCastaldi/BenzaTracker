"""Command-line interface for BenzaTracker."""
from __future__ import annotations

from datetime import datetime, date
from typing import Callable

from .data_store import DataStore, RefuelEntry, DATE_FORMAT
from .kpi import compute_kpis, monthly_spend


def _prompt_date(message: str) -> date:
    while True:
        raw = input(f"{message} ({DATE_FORMAT}): ").strip()
        if not raw:
            print("La data è obbligatoria.")
            continue
        try:
            return datetime.strptime(raw, DATE_FORMAT).date()
        except ValueError:
            print("Formato data non valido. Riprova.")


def _prompt_float(message: str, minimum: float = 0.0) -> float:
    while True:
        raw = input(f"{message}: ").replace(",", ".").strip()
        try:
            value = float(raw)
        except ValueError:
            print("Inserisci un numero valido.")
            continue
        if value <= minimum:
            print("Il valore deve essere maggiore di zero.")
            continue
        return value


def _prompt_optional_float(message: str, minimum: float = 0.0) -> float | None:
    while True:
        raw = input(f"{message} (opzionale): ").replace(",", ".").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            print("Inserisci un numero valido oppure lascia vuoto per saltare.")
            continue
        if value < minimum:
            print("Il valore deve essere maggiore o uguale a zero.")
            continue
        return value


def _prompt_optional(message: str) -> str | None:
    raw = input(f"{message} (opzionale): ").strip()
    return raw or None


def _add_entry(store: DataStore) -> None:
    print("\n--- Nuovo rifornimento ---")
    refuel_date = _prompt_date("Data del rifornimento")
    liters = _prompt_float("Litri effettuati")
    amount_paid = _prompt_float("Importo pagato")
    price_per_liter = round(amount_paid / liters, 3)
    station = _prompt_optional("Benzinaio")
    odometer_km = _prompt_optional_float("Contachilometri attuale (km)")

    entry = RefuelEntry(
        refuel_date=refuel_date,
        liters=liters,
        amount_paid=amount_paid,
        price_per_liter=price_per_liter,
        station=station,
        odometer_km=odometer_km,
    )
    store.append_entry(entry)
    print("Rifornimento salvato correttamente.\n")


def _show_kpis(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    report = compute_kpis(entries)
    print("\n--- KPI sintetici ---")
    print(f"Totale speso: € {report.total_spent:.2f}")
    print(f"Litri totali: {report.total_liters:.2f} L")
    print(f"Prezzo medio: € {report.average_price:.3f}/L")
    print(f"Spesa media mensile: € {report.average_monthly_spend:.2f}")
    print(f"Rifornimenti registrati: {report.entries_count}")
    if report.total_distance_km:
        print(f"Distanza monitorata: {report.total_distance_km:.0f} km")
    if report.average_km_per_liter is not None:
        print(f"Rendimento medio: {report.average_km_per_liter:.2f} km/L")
    if report.average_liters_per_100km is not None:
        print(
            f"Consumo medio: {report.average_liters_per_100km:.2f} L/100 km"
        )
    if report.best_price:
        date_, price = report.best_price
        print(f"Miglior prezzo: € {price:.3f}/L il {date_.strftime(DATE_FORMAT)}")
    if report.worst_price:
        date_, price = report.worst_price
        print(f"Peggior prezzo: € {price:.3f}/L il {date_.strftime(DATE_FORMAT)}")
    print()


def _list_entries(store: DataStore) -> None:
    entries = sorted(store.load_entries(), key=lambda item: item.refuel_date)
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    print("\n--- Storico rifornimenti ---")
    for entry in entries:
        date_str = entry.refuel_date.strftime(DATE_FORMAT)
        station = entry.station or "-"
        odometer = f"{entry.odometer_km:.0f} km" if entry.odometer_km is not None else "-"
        print(
            f"{date_str} | {entry.liters:.2f} L | € {entry.amount_paid:.2f} | "
            f"€ {entry.price_per_liter:.3f}/L | {station} | {odometer}"
        )
    print()


def _show_monthly_spend(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    print("\n--- Spesa mensile ---")
    for month, total in monthly_spend(entries):
        print(f"{month.strftime('%Y-%m')} -> € {total:.2f}")
    print()


def run() -> None:
    store = DataStore()
    actions: dict[str, tuple[str, Callable[[DataStore], None]]] = {
        "1": ("Aggiungi rifornimento", _add_entry),
        "2": ("Mostra KPI", _show_kpis),
        "3": ("Elenca rifornimenti", _list_entries),
        "4": ("Spesa mensile", _show_monthly_spend),
        "5": ("Esci", lambda _store: None),
    }

    while True:
        print("BenzaTracker CLI")
        for key, (label, _) in actions.items():
            print(f"[{key}] {label}")
        choice = input("Seleziona un'opzione: ").strip()

        if choice == "5":
            print("Arrivederci!")
            break

        action = actions.get(choice)
        if not action:
            print("Opzione non valida. Riprova.\n")
            continue

        action[1](store)


if __name__ == "__main__":  # pragma: no cover - manual entrypoint
    run()
