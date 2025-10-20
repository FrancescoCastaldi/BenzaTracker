"""GUI application for BenzaTracker."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import matplotlib
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from ttkbootstrap.constants import BOTH, CENTER, END, RIGHT, W
from ttkbootstrap.scrolled import ScrolledFrame

from .data_store import DATE_FORMAT, DataStore, RefuelEntry
from .kpi import KPIReport, compute_kpis, monthly_spend

matplotlib.use("TkAgg")


class BenzaTrackerApp(tb.Window):
    """Main GUI application."""

    def __init__(self, datastore: DataStore | None = None, theme: str = "darkly") -> None:
        super().__init__(themename=theme, title="BenzaTracker")
        self.geometry("1100x720")
        self.datastore = datastore or DataStore()
        self.entries: list[RefuelEntry] = self.datastore.load_entries()

        self._build_layout()
        self._refresh_dashboard()

    # Layout -----------------------------------------------------------------
    def _build_layout(self) -> None:
        main_frame = ScrolledFrame(self, autohide=True, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Some ttkbootstrap releases renamed the internal container attribute;
        # create a backwards-compatible alias so previously cached bytecode or
        # stale installs that still expect ``innerframe`` continue to work once
        # the updated script is copied over.
        if not hasattr(main_frame, "innerframe"):
            fallback = self._resolve_scroll_container(main_frame)
            setattr(main_frame, "innerframe", fallback)
        else:
            fallback = main_frame.innerframe

        container = fallback

        self._build_form(container)
        self._build_summary(container)
        self._build_table(container)
        self._build_chart(container)

    @staticmethod
    def _resolve_scroll_container(frame: ScrolledFrame) -> tk.Widget:
        """Return the widget that should host scrollable content."""

        # ``ScrolledFrame``'s public API has changed names across ttkbootstrap
        # releases: early versions used ``innerframe``, intermediate builds
        # switched to ``scrollable_frame``, and the latest versions expose the
        # content as ``container`` while delegating geometry methods directly on
        # the scrolled frame itself.  Probe the known attribute names in order of
        # preference and fall back to the frame so we always return a widget that
        # accepts child elements.
        for attr in ("scrollable_frame", "innerframe", "container", "frame", "_frame"):
            widget = getattr(frame, attr, None)
            if isinstance(widget, tk.Misc):
                return widget
        return frame

    def _build_form(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, padding=(15, 10))
        section.pack(fill=tk.X, padx=10, pady=10)

        tb.Label(section, text="Nuovo rifornimento", font=("Helvetica", 18, "bold")).pack(
            anchor=W, pady=(0, 10)
        )

        form_frame = tb.Frame(section)
        form_frame.pack(fill=tk.X)

        self.date_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Data (YYYY-MM-DD)", self.date_var, 0)

        self.liters_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Litri", self.liters_var, 1)

        self.amount_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Pagamento (€)", self.amount_var, 2)

        self.price_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Prezzo €/L (opzionale)", self.price_var, 3)

        self.station_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Benzinaio (opzionale)", self.station_var, 4)

        button_frame = tb.Frame(section)
        button_frame.pack(fill=tk.X, pady=(12, 0))
        tb.Button(button_frame, text="Salva rifornimento", command=self._on_submit, bootstyle="success").pack(
            side=RIGHT
        )

    def _build_summary(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Indicatori", padding=(15, 10))
        section.pack(fill=tk.X, padx=10, pady=10)

        summary_grid = tb.Frame(section)
        summary_grid.pack(fill=tk.X)

        self.summary_vars: dict[str, tk.StringVar] = {}
        labels = {
            "total_spent": "Totale speso",
            "total_liters": "Litri totali",
            "average_price": "Prezzo medio €/L",
            "average_monthly_spend": "Spesa media mensile",
            "entries_count": "Numero rifornimenti",
            "best_price": "Miglior prezzo",
            "worst_price": "Peggior prezzo",
        }

        for column, (key, label) in enumerate(labels.items()):
            frame = tb.Frame(summary_grid, padding=10)
            frame.grid(row=0, column=column, sticky=W)
            tb.Label(frame, text=label, font=("Helvetica", 10, "bold")).pack(anchor=W)
            value_var = tk.StringVar(value="-")
            tb.Label(frame, textvariable=value_var, font=("Helvetica", 12)).pack(anchor=W)
            self.summary_vars[key] = value_var

    def _build_table(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Storico rifornimenti", padding=(15, 10))
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("date", "liters", "amount", "price", "station")
        self.tree = tb.Treeview(
            section,
            columns=columns,
            show="headings",
            height=8,
            bootstyle="dark",
        )
        headings = {
            "date": "Data",
            "liters": "Litri",
            "amount": "Pagamento",
            "price": "€/L",
            "station": "Benzinaio",
        }
        for name, text in headings.items():
            self.tree.heading(name, text=text)
            self.tree.column(name, anchor=CENTER, width=130)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _build_chart(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Spesa mensile", padding=(15, 10))
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Mese")
        self.ax.set_ylabel("Spesa (€)")
        self.ax.set_title("Andamento mensile")

        self.canvas = FigureCanvasTkAgg(self.figure, master=section)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _add_labeled_entry(self, parent: tk.Widget, label: str, variable: tk.StringVar, column: int) -> None:
        frame = tb.Frame(parent, padding=5)
        frame.grid(row=0, column=column, padx=5, pady=5)
        tb.Label(frame, text=label).pack(anchor=W)
        tb.Entry(frame, textvariable=variable, width=20).pack()

    # Event handlers ----------------------------------------------------------
    def _on_submit(self) -> None:
        try:
            refuel_date = datetime.strptime(self.date_var.get().strip(), DATE_FORMAT).date()
        except ValueError:
            messagebox.showerror("Data non valida", "Inserisci la data nel formato YYYY-MM-DD")
            return

        try:
            liters = float(self.liters_var.get())
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Valori non validi", "Litri e pagamento devono essere numeri")
            return

        if liters <= 0 or amount <= 0:
            messagebox.showerror("Valori non validi", "Litri e pagamento devono essere positivi")
            return

        if self.price_var.get().strip():
            try:
                price = float(self.price_var.get())
            except ValueError:
                messagebox.showerror("Prezzo non valido", "Il prezzo deve essere numerico")
                return
        else:
            price = amount / liters

        station = self.station_var.get().strip() or None

        entry = RefuelEntry(
            refuel_date=refuel_date,
            liters=liters,
            amount_paid=amount,
            price_per_liter=price,
            station=station,
        )

        self.entries = self.datastore.append_entry(entry)
        self._clear_form()
        self._refresh_dashboard()
        messagebox.showinfo("Rifornimento salvato", "Il rifornimento è stato registrato correttamente")

    # Helpers ----------------------------------------------------------------
    def _clear_form(self) -> None:
        for var in (self.date_var, self.liters_var, self.amount_var, self.price_var, self.station_var):
            var.set("")

    def _refresh_dashboard(self) -> None:
        self._update_summary()
        self._update_table()
        self._update_chart()

    def _update_summary(self) -> None:
        report: KPIReport = compute_kpis(self.entries)
        self.summary_vars["total_spent"].set(f"€ {report.total_spent:.2f}")
        self.summary_vars["total_liters"].set(f"{report.total_liters:.2f} L")
        self.summary_vars["average_price"].set(f"€ {report.average_price:.3f}")
        self.summary_vars["average_monthly_spend"].set(f"€ {report.average_monthly_spend:.2f}")
        self.summary_vars["entries_count"].set(str(report.entries_count))
        if report.best_price:
            date_value, price = report.best_price
            self.summary_vars["best_price"].set(f"€ {price:.3f} ({date_value:%d/%m/%Y})")
        else:
            self.summary_vars["best_price"].set("-")
        if report.worst_price:
            date_value, price = report.worst_price
            self.summary_vars["worst_price"].set(f"€ {price:.3f} ({date_value:%d/%m/%Y})")
        else:
            self.summary_vars["worst_price"].set("-")

    def _update_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for entry in sorted(self.entries, key=lambda item: item.refuel_date, reverse=True):
            self.tree.insert(
                "",
                END,
                values=(
                    entry.refuel_date.strftime("%d/%m/%Y"),
                    f"{entry.liters:.2f}",
                    f"€ {entry.amount_paid:.2f}",
                    f"€ {entry.price_per_liter:.3f}",
                    entry.station or "-",
                ),
            )

    def _update_chart(self) -> None:
        self.ax.clear()
        self.ax.set_xlabel("Mese")
        self.ax.set_ylabel("Spesa (€)")
        self.ax.set_title("Andamento mensile")

        monthly_data = monthly_spend(self.entries)
        if monthly_data:
            months = [month.strftime("%b %Y") for month, _ in monthly_data]
            values = [total for _, total in monthly_data]
            bars = self.ax.bar(months, values, color="#3cb371")
            self.ax.bar_label(bars, fmt="€ %.0f")
        else:
            self.ax.text(0.5, 0.5, "Nessun dato disponibile", ha="center", va="center", transform=self.ax.transAxes)
        self.figure.tight_layout()
        self.canvas.draw_idle()


def run() -> None:
    app = BenzaTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    run()
