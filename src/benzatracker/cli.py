"""Command-line interface for BenzaTracker."""
from __future__ import annotations

from datetime import date, datetime
from typing import Callable, List, Tuple

from . import config
from .kpi import compute, monthly_spend
from .models import DATE_FORMAT, RefuelEntry
from .store import create_store

# ── 10‑day windows (tenth windows) ─────────────────────────────────────────

_MONTH_ABBR = [
    "", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
    "Lug", "Ago", "Set", "Ott", "Nov", "Dic",
]


def _add_months(source: date, months: int) -> date:
    total = source.year * 12 + source.month + months - 1
    year = total // 12
    month = total % 12 + 1
    day = min(source.day, 28)
    return date(year, month, day)


def build_tenth_windows(
    reference_date: date,
) -> List[Tuple[str, date, date]]:
    """Build three consecutive 10‑day windows around *reference_date*."""
    anchor = date(reference_date.year, reference_date.month, 10)
    past_start = _add_months(anchor, -1)
    past_end = anchor
    cur_start = anchor
    cur_end = _add_months(anchor, 1)
    next_start = cur_end
    next_end = _add_months(next_start, 1)

    def _label(start: date, end: date) -> str:
        return f"10 {_MONTH_ABBR[start.month]} — 10 {_MONTH_ABBR[end.month]}"

    return [
        (_label(past_start, past_end), past_start, past_end),
        (_label(cur_start, cur_end), cur_start, cur_end),
        (_label(next_start, next_end), next_start, next_end),
    ]


# ── CLI actions ─────────────────────────────────────────────────────────────

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


def _prompt_optional(message: str) -> str | None:
    raw = input(f"{message} (opzionale): ").strip()
    return raw or None


def _add_entry(store) -> None:
    print("\n--- Nuovo rifornimento ---")
    refuel_date = _prompt_date("Data del rifornimento")
    liters = _prompt_float("Litri effettuati")
    amount_paid = _prompt_float("Importo pagato")
    price_per_liter = round(amount_paid / liters, 3)
    station = _prompt_optional("Benzinaio")
    entry = RefuelEntry(
        refuel_date=refuel_date,
        liters=liters,
        amount_paid=amount_paid,
        price_per_liter=price_per_liter,
        station=station,
    )
    store.append_entry(entry)
    print("Rifornimento salvato correttamente.\n")


def _show_kpis(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return
    report = compute(entries)
    print("\n--- KPI sintetici ---")
    print(f"Totale speso: € {report.total_spent:.2f}")
    print(f"Litri totali: {report.total_liters:.2f} L")
    print(f"Prezzo medio: € {report.average_price:.3f}/L")
    print(f"Spesa media mensile: € {report.average_monthly_spend:.2f}")
    print(f"Rifornimenti registrati: {report.entries_count}")
    if report.best_price:
        d, p = report.best_price
        print(f"Miglior prezzo: € {p:.3f}/L il {d.strftime(DATE_FORMAT)}")
    if report.worst_price:
        d, p = report.worst_price
        print(f"Peggior prezzo: € {p:.3f}/L il {d.strftime(DATE_FORMAT)}")
    print()


def _list_entries(store) -> None:
    entries = sorted(store.load_entries(), key=lambda e: e.refuel_date)
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return
    print("\n--- Storico rifornimenti ---")
    for entry in entries:
        date_str = entry.refuel_date.strftime(DATE_FORMAT)
        station = entry.station or "-"
        print(
            f"{date_str} | {entry.liters:.2f} L | € {entry.amount_paid:.2f} | "
            f"€ {entry.price_per_liter:.3f}/L | {station}"
        )
    print()


def _show_monthly_spend(store) -> None:
    entries = store.load_entries()
    if not entries:
        print("\nNessun rifornimento registrato.\n")
        return
    print("\n--- Spesa mensile ---")
    for month, total in monthly_spend(entries):
        print(f"{month.strftime('%Y-%m')} -> € {total:.2f}")
    print()


def run() -> None:
    store = create_store(config.get_data_dir())
    actions: dict[str, tuple[str, Callable]] = {
        "1": ("Aggiungi rifornimento", _add_entry),
        "2": ("Mostra KPI", _show_kpis),
        "3": ("Elenca rifornimenti", _list_entries),
        "4": ("Spesa mensile", _show_monthly_spend),
        "5": ("Esci", lambda _: None),
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
