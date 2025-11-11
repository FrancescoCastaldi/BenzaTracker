"""Graphical user interface for BenzaTracker."""
from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .data_store import (
    DataStore,
    RefuelEntry,
    DATE_FORMAT,
    TIMESTAMP_FORMAT,
    EXAMPLE_TIMESTAMP_DISPLAY,
)
from .kpi import compute_kpis, monthly_spend

class BenzaTrackerApp(ttk.Frame):
    """Main application window for BenzaTracker."""

    def __init__(self, master: tk.Misc | None = None, store: DataStore | None = None) -> None:
        self.root = master or tk.Tk()
        super().__init__(self.root)
        self.root.title("BenzaTracker")
        self.root.geometry("1024x720")
        self.root.minsize(900, 600)

        self.store = store or DataStore()
        self._entries_cache: list[RefuelEntry] = []

        self.pack(fill=tk.BOTH, expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=2)
        self.rowconfigure(6, weight=1)

        self._build_header()
        self._build_form()
        self._build_kpi_panel()
        self._build_table()
        self._build_chart()

        self._refresh_data()

    # ------------------------------------------------------------------
    # UI Builders
    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        title = ttk.Label(
            self,
            text="BenzaTracker",
            font=("Helvetica", 20, "bold"),
        )
        subtitle = ttk.Label(
            self,
            text="Registra i rifornimenti e monitora KPI e spesa mensile",
        )
        self.last_update_var = tk.StringVar(
            value=(
                "Ultimo aggiornamento: nessun dato "
                f"(esempio: {EXAMPLE_TIMESTAMP_DISPLAY})"
            )
        )
        last_update_label = ttk.Label(
            self,
            textvariable=self.last_update_var,
            font=("Helvetica", 9),
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 0))
        subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 4))
        last_update_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))

    def _build_form(self) -> None:
        form_frame = ttk.LabelFrame(self, text="Nuovo rifornimento")
        form_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        form_frame.columnconfigure(tuple(range(6)), weight=1)

        self.date_var = tk.StringVar(value=datetime.today().strftime(DATE_FORMAT))
        self.liters_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.station_var = tk.StringVar()
        self.odometer_var = tk.StringVar()

        fields = [
            ("Data (YYYY-MM-DD)", self.date_var),
            ("Litri", self.liters_var),
            ("Importo (€)", self.amount_var),
            ("Benzinaio", self.station_var),
            ("Contachilometri (km)", self.odometer_var),
        ]

        for column, (label, variable) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=0, column=column, sticky="w", padx=5, pady=(8, 2))
            ttk.Entry(form_frame, textvariable=variable, width=18).grid(
                row=1, column=column, sticky="ew", padx=5, pady=(0, 10)
            )

        add_button = ttk.Button(form_frame, text="Salva rifornimento", command=self._on_add_entry)
        add_button.grid(row=1, column=len(fields), padx=5, pady=(0, 10))

    def _build_kpi_panel(self) -> None:
        kpi_frame = ttk.LabelFrame(self, text="KPI sintetici")
        kpi_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        kpi_frame.columnconfigure(tuple(range(3)), weight=1)

        self.kpi_labels: dict[str, ttk.Label] = {}
        entries = [
            ("total_spent", "Totale speso", "€ 0.00"),
            ("total_liters", "Litri totali", "0.00 L"),
            ("average_price", "Prezzo medio", "€ 0.000/L"),
            ("average_monthly_spend", "Spesa media mensile", "€ 0.00"),
            ("entries_count", "Rifornimenti", "0"),
            ("total_distance", "Distanza monitorata", "0 km"),
            ("km_per_liter", "Rendimento medio", "-"),
            ("liters_per_100km", "Consumo medio", "-"),
            ("best_price", "Miglior prezzo", "-"),
            ("worst_price", "Peggior prezzo", "-"),
        ]

        for index, (key, title, default) in enumerate(entries):
            card = ttk.Frame(kpi_frame, padding=10)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=6, pady=6)
            card.columnconfigure(0, weight=1)

            ttk.Label(card, text=title, font=("Helvetica", 10, "bold")).grid(
                row=0, column=0, sticky="w"
            )
            value_label = ttk.Label(card, text=default, font=("Helvetica", 12))
            value_label.grid(row=1, column=0, sticky="w", pady=(4, 0))
            self.kpi_labels[key] = value_label

    def _build_table(self) -> None:
        table_frame = ttk.LabelFrame(self, text="Storico rifornimenti")
        table_frame.grid(row=5, column=0, sticky="nsew", padx=20, pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("date", "liters", "amount", "price", "station", "odometer")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("date", text="Data")
        self.tree.heading("liters", text="Litri")
        self.tree.heading("amount", text="Importo")
        self.tree.heading("price", text="€/L")
        self.tree.heading("station", text="Benzinaio")
        self.tree.heading("odometer", text="Contachilometri")

        for column, width in zip(columns, (120, 80, 100, 80, 160, 150)):
            self.tree.column(column, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        button_frame = ttk.Frame(table_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=6)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Aggiorna contachilometri", command=self._on_update_odometer).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(button_frame, text="Elimina rifornimento", command=self._on_delete_entry).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

    def _build_chart(self) -> None:
        chart_frame = ttk.LabelFrame(self, text="Andamento spesa")
        chart_frame.grid(row=6, column=0, sticky="nsew", padx=20, pady=(0, 20))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.figure = Figure(figsize=(9, 3.4), dpi=100)
        self.ax = self.figure.add_subplot(121)
        self.ax_pie = self.figure.add_subplot(122)
        self.ax.set_ylabel("Euro")
        self.ax.set_xlabel("Mese")
        self.ax.set_title("Spesa per mese")
        self.ax_pie.set_title("Peso per benzinaio")

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _on_add_entry(self) -> None:
        try:
            refuel_date = datetime.strptime(self.date_var.get().strip(), DATE_FORMAT).date()
        except ValueError:
            messagebox.showerror("Data non valida", f"Inserisci una data nel formato {DATE_FORMAT}.")
            return

        try:
            liters = float(self.liters_var.get().replace(",", "."))
            if liters <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valore non valido", "Inserisci un numero di litri maggiore di zero.")
            return

        try:
            amount = float(self.amount_var.get().replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valore non valido", "Inserisci un importo maggiore di zero.")
            return

        station = self.station_var.get().strip() or None
        odometer_raw = self.odometer_var.get().strip()
        odometer_value: float | None
        if odometer_raw:
            try:
                odometer_value = float(odometer_raw.replace(",", "."))
                if odometer_value < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Valore non valido", "Il contachilometri deve essere un numero positivo.")
                return
        else:
            odometer_value = None

        entry = RefuelEntry(
            refuel_date=refuel_date,
            liters=liters,
            amount_paid=amount,
            price_per_liter=round(amount / liters, 3),
            station=station,
            odometer_km=odometer_value,
        )

        self.store.append_entry(entry)
        self._clear_form()
        self._refresh_data()
        messagebox.showinfo("Salvato", "Rifornimento registrato correttamente.")

    def _on_delete_entry(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Nessuna selezione", "Seleziona un rifornimento da eliminare.")
            return

        iid = selection[0]
        index = int(iid)
        entry = self._entries_cache[index]
        confirm = messagebox.askyesno(
            "Conferma eliminazione",
            f"Vuoi eliminare il rifornimento del {entry.refuel_date.strftime(DATE_FORMAT)}?",
        )
        if not confirm:
            return

        self.store.delete_entry(index)
        self._refresh_data()

    def _on_update_odometer(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Nessuna selezione", "Seleziona un rifornimento da aggiornare.")
            return

        iid = selection[0]
        index = int(iid)
        entry = self._entries_cache[index]
        prompt = (
            "Inserisci il nuovo valore del contachilometri (km).\n"
            "Lascia vuoto per rimuovere il dato."
        )
        current_value = "" if entry.odometer_km is None else str(entry.odometer_km)
        result = simpledialog.askstring(
            "Aggiorna contachilometri",
            prompt,
            initialvalue=current_value,
            parent=self.root,
        )
        if result is None:
            return

        result = result.strip()
        odometer_value: float | None
        if not result:
            odometer_value = None
        else:
            try:
                odometer_value = float(result.replace(",", "."))
                if odometer_value < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Valore non valido",
                    "Il contachilometri deve essere un numero positivo.",
                )
                return

        self.store.update_odometer(index, odometer_value)
        self._refresh_data()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_form(self) -> None:
        self.liters_var.set("")
        self.amount_var.set("")
        self.station_var.set("")
        self.odometer_var.set("")
        self.date_var.set(datetime.today().strftime(DATE_FORMAT))

    def _refresh_data(self) -> None:
        self._entries_cache = self.store.load_entries()
        self._refresh_last_update()
        self._refresh_kpis()
        self._refresh_table()
        self._refresh_chart()

    def _refresh_last_update(self) -> None:
        timestamp = self.store.last_updated_at()
        if timestamp is not None:
            formatted = timestamp.strftime(TIMESTAMP_FORMAT)
            self.last_update_var.set(f"Ultimo aggiornamento: {formatted}")
        else:
            self.last_update_var.set(
                "Ultimo aggiornamento: nessun dato "
                f"(esempio: {EXAMPLE_TIMESTAMP_DISPLAY})"
            )

    def _refresh_kpis(self) -> None:
        report = compute_kpis(self._entries_cache)
        self.kpi_labels["total_spent"].configure(text=f"€ {report.total_spent:.2f}")
        self.kpi_labels["total_liters"].configure(text=f"{report.total_liters:.2f} L")
        self.kpi_labels["average_price"].configure(text=f"€ {report.average_price:.3f}/L")
        self.kpi_labels["average_monthly_spend"].configure(text=f"€ {report.average_monthly_spend:.2f}")
        self.kpi_labels["entries_count"].configure(text=str(report.entries_count))

        distance_text = f"{report.total_distance_km:.0f} km" if report.total_distance_km else "0 km"
        self.kpi_labels["total_distance"].configure(text=distance_text)

        if report.average_km_per_liter is not None:
            self.kpi_labels["km_per_liter"].configure(text=f"{report.average_km_per_liter:.2f} km/L")
        else:
            self.kpi_labels["km_per_liter"].configure(text="-")

        if report.average_liters_per_100km is not None:
            self.kpi_labels["liters_per_100km"].configure(text=f"{report.average_liters_per_100km:.2f} L/100 km")
        else:
            self.kpi_labels["liters_per_100km"].configure(text="-")

        if report.best_price:
            date_, price = report.best_price
            self.kpi_labels["best_price"].configure(
                text=f"€ {price:.3f}/L ({date_.strftime(DATE_FORMAT)})"
            )
        else:
            self.kpi_labels["best_price"].configure(text="-")

        if report.worst_price:
            date_, price = report.worst_price
            self.kpi_labels["worst_price"].configure(
                text=f"€ {price:.3f}/L ({date_.strftime(DATE_FORMAT)})"
            )
        else:
            self.kpi_labels["worst_price"].configure(text="-")

    def _refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, entry in enumerate(self._entries_cache):
            odometer = "-" if entry.odometer_km is None else f"{entry.odometer_km:.0f} km"
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    entry.refuel_date.strftime(DATE_FORMAT),
                    f"{entry.liters:.2f}",
                    f"€ {entry.amount_paid:.2f}",
                    f"€ {entry.price_per_liter:.3f}",
                    entry.station or "-",
                    odometer,
                ),
            )

    def _refresh_chart(self) -> None:
        self.ax.clear()
        self.ax_pie.clear()
        self.ax.set_ylabel("Euro")
        self.ax.set_xlabel("Mese")
        self.ax.set_title("Spesa per mese")
        self.ax_pie.set_title("Peso per benzinaio")

        data = monthly_spend(self._entries_cache)
        if data:
            labels = [month.strftime("%b %Y") for month, _ in data]
            values = [amount for _, amount in data]
            self.ax.bar(labels, values, color="#2a9d8f")
            self.ax.tick_params(axis="x", rotation=30)
        else:
            self.ax.text(0.5, 0.5, "Nessun dato disponibile", ha="center", va="center", transform=self.ax.transAxes)

        station_totals: dict[str, float] = {}
        for entry in self._entries_cache:
            station_name = entry.station or "Senza nome"
            station_totals[station_name] = station_totals.get(station_name, 0.0) + entry.amount_paid

        if station_totals and any(amount > 0 for amount in station_totals.values()):
            labels = list(station_totals.keys())
            sizes = list(station_totals.values())
            self.ax_pie.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
            self.ax_pie.axis("equal")
        else:
            self.ax_pie.text(0.5, 0.5, "Nessun dato disponibile", ha="center", va="center", transform=self.ax_pie.transAxes)

        self.figure.tight_layout()
        self.canvas.draw_idle()


def run() -> None:
    """Start the BenzaTracker GUI application."""
    root = tk.Tk()
    app = BenzaTrackerApp(root)
    app.mainloop()


if __name__ == "__main__":
    run()
