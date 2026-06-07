"""GUI application for BenzaTracker (ttkbootstrap / tkinter)."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import matplotlib

matplotlib.use("TkAgg")
import ttkbootstrap as tb  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from ttkbootstrap.constants import BOTH, CENTER, END, RIGHT, W  # noqa: E402
from ttkbootstrap.scrolled import ScrolledFrame  # noqa: E402

from . import config
from .kpi import compute, monthly_spend
from .models import DATE_FORMAT, RefuelEntry
from .pdf import ReportGenerator
from .store import create_store


class BenzaTrackerApp(tb.Window):
    """Main GUI application."""

    def __init__(self, theme: str = "darkly") -> None:
        super().__init__(themename=theme, title="BenzaTracker")
        self.geometry("1100x720")
        self.datastore = create_store(config.get_data_dir())
        self.entries: list[RefuelEntry] = self.datastore.load_entries()
        self._build_layout()
        self._refresh_dashboard()

    # Layout -----------------------------------------------------------------
    def _build_layout(self) -> None:
        main_frame = ScrolledFrame(self, autohide=True, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        container = tb.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True)
        self._build_form(container)
        self._build_summary(container)
        self._build_table(container)
        self._build_chart(container)

    def _build_form(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, padding=(15, 10))
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
        tb.Button(
            button_frame,
            text="Esporta PDF",
            command=self._on_export_pdf,
            bootstyle="info",
        ).pack(side=RIGHT, padx=5)

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
            section, columns=columns, show="headings", height=8, bootstyle="dark",
        )
        headings = {
            "date": "Data", "liters": "Litri", "amount": "Pagamento",
            "price": "€/L", "station": "Benzinaio",
        }
        for name, text in headings.items():
            self.tree.heading(name, text=text)
            self.tree.column(name, anchor=CENTER, width=130)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _build_chart(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Spesa mensile", padding=(15, 10))
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        btn_frame = tb.Frame(section)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        tb.Button(
            btn_frame, text="Elimina selezionato",
            command=self._on_delete, bootstyle="danger",
        ).pack(side=RIGHT)
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
            refuel_date=refuel_date, liters=liters, amount_paid=amount,
            price_per_liter=price, station=station,
        )
        self.entries = self.datastore.append_entry(entry)
        self._clear_form()
        self._refresh_dashboard()
        messagebox.showinfo("Rifornimento salvato", "Il rifornimento è stato registrato correttamente")

    def _on_delete(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nessuna selezione", "Seleziona un rifornimento da eliminare")
            return
        if not messagebox.askyesno("Conferma eliminazione", "Vuoi davvero eliminare questo rifornimento?"):
            return
        selected_item = self.tree.item(selected[0])
        date_str = selected_item["values"][0]
        refuel_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        self.entries = [e for e in self.entries if e.refuel_date != refuel_date]
        self.datastore.save_entries(self.entries)
        self._refresh_dashboard()
        messagebox.showinfo("Eliminato", "Il rifornimento è stato eliminato")

    def _on_export_pdf(self) -> None:
        if not self.entries:
            messagebox.showwarning("Nessun dato", "Non ci sono dati da esportare")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="benzatracker_report.pdf",
        )
        if file_path:
            try:
                generator = ReportGenerator(file_path)
                generator.generate(self.entries)
                messagebox.showinfo("Esportazione completata", f"Report salvato in: {file_path}")
            except Exception as e:
                messagebox.showerror("Errore esportazione", f"Errore durante l'esportazione: {e}")

    # Helpers ----------------------------------------------------------------
    def _clear_form(self) -> None:
        for var in (self.date_var, self.liters_var, self.amount_var, self.price_var, self.station_var):
            var.set("")

    def _refresh_dashboard(self) -> None:
        self._update_summary()
        self._update_table()
        self._update_chart()

    def _update_summary(self) -> None:
        report = compute(self.entries)
        self.summary_vars["total_spent"].set(f"€ {report.total_spent:.2f}")
        self.summary_vars["total_liters"].set(f"{report.total_liters:.2f} L")
        self.summary_vars["average_price"].set(f"€ {report.average_price:.3f}")
        self.summary_vars["average_monthly_spend"].set(f"€ {report.average_monthly_spend:.2f}")
        self.summary_vars["entries_count"].set(str(report.entries_count))
        if report.best_price:
            d, p = report.best_price
            self.summary_vars["best_price"].set(f"€ {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["best_price"].set("-")
        if report.worst_price:
            d, p = report.worst_price
            self.summary_vars["worst_price"].set(f"€ {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["worst_price"].set("-")

    def _update_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for entry in sorted(self.entries, key=lambda e: e.refuel_date, reverse=True):
            self.tree.insert(
                "", END,
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
            months = [m.strftime("%b %Y") for m, _ in monthly_data]
            values = [v for _, v in monthly_data]
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
