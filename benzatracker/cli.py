"""Command-line interface for BenzaTracker."""
from __future__ import annotations

from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Callable, Iterable, List, Tuple
import os
import subprocess
import sys

from .data_store import (
    DataStore,
    RefuelEntry,
    DATE_FORMAT,
    TIMESTAMP_FORMAT,
    EXAMPLE_TIMESTAMP_DISPLAY,
)
from .kpi import compute_kpis, monthly_spend


def _shift_month(year: int, month: int, offset: int) -> Tuple[int, int]:
    """Return a (year, month) tuple offset by the requested number of months."""

    total_months = month - 1 + offset
    new_year = year + total_months // 12
    new_month = total_months % 12 + 1
    return new_year, new_month


def build_tenth_windows(reference: date | None = None) -> List[Tuple[str, date, date]]:
    """Compute rolling windows anchored on the 10th day of each month.

    The function returns three consecutive ranges:

    * 10 of the previous month -> 9 of the current month
    * 10 of the current month -> 9 of the next month
    * 10 of the next month -> 9 of the following month

    Labels are human friendly while the start/end boundaries are returned
    as ``date`` objects. The end boundary is exclusive, so callers should
    include dates with ``start <= date < end``.
    """

    reference = reference or date.today()
    year = reference.year
    month = reference.month

    prev_year, prev_month = _shift_month(year, month, -1)
    next_year, next_month = _shift_month(year, month, 1)
    after_next_year, after_next_month = _shift_month(year, month, 2)

    prev_start = date(prev_year, prev_month, 10)
    current_start = date(year, month, 10)
    next_start = date(next_year, next_month, 10)
    after_next_start = date(after_next_year, after_next_month, 10)

    def _window_label(start: date, end: date) -> str:
        end_display = end - timedelta(days=1)
        return f"{start.strftime('%d %b %Y')} → {end_display.strftime('%d %b %Y')}"

    return [
        (_window_label(prev_start, current_start), prev_start, current_start),
        (_window_label(current_start, next_start), current_start, next_start),
        (
            _window_label(next_start, after_next_start),
            next_start,
            after_next_start,
        ),
    ]


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


def _prompt_optional_photo_path(message: str) -> Path | None:
    while True:
        raw = input(f"{message} (opzionale): ").strip()
        if not raw:
            return None
        candidate = Path(raw).expanduser()
        if candidate.exists():
            return candidate
        print("File non trovato. Inserisci un percorso valido oppure lascia vuoto per annullare.")


def _add_entry(store: DataStore) -> None:
    print("\n--- Nuovo rifornimento ---")
    refuel_date = _prompt_date("Data del rifornimento")
    liters = _prompt_float("Litri effettuati")
    amount_paid = _prompt_float("Importo pagato")
    price_per_liter = round(amount_paid / liters, 3)
    station = _prompt_optional("Benzinaio")
    odometer_km = _prompt_optional_float("Contachilometri attuale (km)")
    photo_source = _prompt_optional_photo_path("Percorso foto a supporto")

    photo_identifier: str | None = None
    if photo_source is not None:
        try:
            photo_identifier = store.import_photo(photo_source)
        except FileNotFoundError as exc:
            print(f"Impossibile allegare la foto: {exc}")
            return

    entry = RefuelEntry(
        refuel_date=refuel_date,
        liters=liters,
        amount_paid=amount_paid,
        price_per_liter=price_per_liter,
        station=station,
        odometer_km=odometer_km,
        photo_path=photo_identifier,
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


def _render_entries(entries: Iterable[RefuelEntry]) -> None:
    ordered = sorted(entries, key=lambda item: item.refuel_date)
    for idx, entry in enumerate(ordered, start=1):
        date_str = entry.refuel_date.strftime(DATE_FORMAT)
        station = entry.station or "-"
        odometer = f"{entry.odometer_km:.0f} km" if entry.odometer_km is not None else "-"
        photo_flag = "📷" if entry.photo_path else "-"
        print(
            f"[{idx}] {date_str} | {entry.liters:.2f} L | € {entry.amount_paid:.2f} | "
            f"€ {entry.price_per_liter:.3f}/L | {station} | {odometer} | Foto: {photo_flag}"
        )


def _list_entries(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    print("\n--- Storico rifornimenti ---")
    _render_entries(entries)
    print()


def _prompt_entry_index(entries: list[RefuelEntry], action: str) -> int | None:
    print()
    _render_entries(entries)
    while True:
        raw = input(
            f"Seleziona l'ID del rifornimento da {action} (lascia vuoto per annullare): "
        ).strip()
        if not raw:
            return None
        if not raw.isdigit():
            print("Inserisci un numero valido oppure lascia vuoto per uscire.")
            continue
        index = int(raw) - 1
        if not 0 <= index < len(entries):
            print("Indice non valido. Riprova.")
            continue
        return index


def _delete_entry(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento disponibile da eliminare.\n")
        return

    print("\n--- Elimina rifornimento ---")
    index = _prompt_entry_index(entries, "eliminare")
    if index is None:
        print("Operazione annullata.\n")
        return

    confirmation = input("Confermi l'eliminazione? [s/N]: ").strip().lower()
    if confirmation != "s":
        print("Eliminazione annullata.\n")
        return

    store.delete_entry(index)
    print("Rifornimento eliminato correttamente.\n")


def _update_odometer(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento disponibile da aggiornare.\n")
        return

    print("\n--- Aggiorna contachilometri ---")
    index = _prompt_entry_index(entries, "aggiornare")
    if index is None:
        print("Operazione annullata.\n")
        return

    new_value = _prompt_optional_float("Nuovo contachilometri (km)", minimum=0.0)
    updated = store.update_odometer(index, new_value)
    if new_value is None:
        print("Contachilometri rimosso per il rifornimento selezionato.")
    else:
        print(
            "Contachilometri aggiornato a "
            f"{updated.odometer_km:.0f} km per il rifornimento selezionato."
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


def _open_photo(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    print("\n--- Apri foto rifornimento ---")
    index = _prompt_entry_index(entries, "visualizzare")
    if index is None:
        print("Operazione annullata.\n")
        return

    entry = entries[index]
    if not entry.photo_path:
        print("Nessuna foto associata al rifornimento selezionato.\n")
        return

    photo_file = store.resolve_photo_path(entry.photo_path)
    if not photo_file.exists():
        print(f"Foto non trovata sul disco: {photo_file}\n")
        return

    print(f"Aprendo foto: {photo_file}")
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(photo_file))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(photo_file)], check=False)
        else:
            subprocess.run(["xdg-open", str(photo_file)], check=False)
    except Exception as exc:  # pragma: no cover - platform dependent
        print(f"Impossibile aprire automaticamente la foto: {exc}")
        print(f"Puoi aprirla manualmente dal percorso indicato sopra.\n")
    else:
        print()


def _filter_by_tenth_windows(store: DataStore) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return

    windows = build_tenth_windows()
    print("\n--- Filtra per periodi dal 10 del mese ---")
    for idx, (label, _, _) in enumerate(windows, start=1):
        print(f"[{idx}] {label}")

    choice = input("Seleziona un periodo (lascia vuoto per annullare): ").strip()
    if not choice:
        print("Operazione annullata.\n")
        return
    if not choice.isdigit():
        print("Scelta non valida.\n")
        return

    index = int(choice) - 1
    if not 0 <= index < len(windows):
        print("Indice fuori intervallo.\n")
        return

    label, start, end = windows[index]
    filtered = [
        entry for entry in entries if start <= entry.refuel_date < end
    ]

    print(f"\n--- Periodo selezionato: {label} ---")
    if not filtered:
        print("Nessun rifornimento nel periodo indicato.\n")
        return

    _render_entries(filtered)

    report = compute_kpis(filtered)
    print("\nRiepilogo periodo:")
    print(f"Totale speso: € {report.total_spent:.2f}")
    print(f"Litri erogati: {report.total_liters:.2f} L")
    if report.average_km_per_liter is not None:
        print(f"Rendimento medio: {report.average_km_per_liter:.2f} km/L")
    if report.average_liters_per_100km is not None:
        print(f"Consumo medio: {report.average_liters_per_100km:.2f} L/100 km")
    print()


def run() -> None:
    store = DataStore()
    sample_hint = f"esempio: {EXAMPLE_TIMESTAMP_DISPLAY}"
    actions: dict[str, tuple[str, Callable[[DataStore], None]]] = {
        "1": ("Aggiungi rifornimento", _add_entry),
        "2": ("Mostra KPI", _show_kpis),
        "3": ("Elenca rifornimenti", _list_entries),
        "4": ("Spesa mensile", _show_monthly_spend),
        "5": ("Aggiorna contachilometri", _update_odometer),
        "6": ("Elimina rifornimento", _delete_entry),
        "7": (
            "Filtra periodi (10 del mese)",
            _filter_by_tenth_windows,
        ),
        "8": ("Apri foto rifornimento", _open_photo),
        "9": ("Esci", lambda _store: None),
    }

    while True:
        print("BenzaTracker CLI")
        last_update = store.last_updated_at()
        if last_update is not None:
            print(
                "Ultimo aggiornamento archivio: "
                f"{last_update.strftime(TIMESTAMP_FORMAT)}"
            )
        else:
            print(f"Nessun dato salvato finora ({sample_hint}).")
        for key, (label, _) in actions.items():
            print(f"[{key}] {label}")
        choice = input("Seleziona un'opzione: ").strip()

        if choice == "9":
            print("Arrivederci!")
            break

        action = actions.get(choice)
        if not action:
            print("Opzione non valida. Riprova.\n")
            continue

        action[1](store)


if __name__ == "__main__":  # pragma: no cover - manual entrypoint
    run()
