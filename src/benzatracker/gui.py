"""GUI application for BenzaTracker (ttkbootstrap / tkinter)."""
from __future__ import annotations

import csv
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
        self.geometry("1200x760")
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
        tb.Label(section, text="New refuel", font=("Helvetica", 18, "bold")).pack(
            anchor=W, pady=(0, 10)
        )
        form_frame = tb.Frame(section)
        form_frame.pack(fill=tk.X)
        self.date_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Date (YYYY-MM-DD)", self.date_var, 0)
        self.liters_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Liters", self.liters_var, 1)
        self.amount_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Amount (\u20ac)", self.amount_var, 2)
        self.price_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Price \u20ac/L (optional)", self.price_var, 3)
        self.station_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Station (optional)", self.station_var, 4)
        self.odometer_var = tk.StringVar()
        self._add_labeled_entry(form_frame, "Odometer km (optional)", self.odometer_var, 5)
        button_frame = tb.Frame(section)
        button_frame.pack(fill=tk.X, pady=(12, 0))
        tb.Button(button_frame, text="Save refuel", command=self._on_submit, bootstyle="success").pack(
            side=RIGHT
        )
        tb.Button(
            button_frame,
            text="Export PDF",
            command=self._on_export_pdf,
            bootstyle="info",
        ).pack(side=RIGHT, padx=5)
        tb.Button(
            button_frame,
            text="Export CSV",
            command=self._on_export_csv,
            bootstyle="secondary",
        ).pack(side=RIGHT, padx=5)

    def _build_summary(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="KPIs", padding=(15, 10))
        section.pack(fill=tk.X, padx=10, pady=10)
        summary_grid = tb.Frame(section)
        summary_grid.pack(fill=tk.X)
        self.summary_vars: dict[str, tk.StringVar] = {}
        labels = {
            "total_spent": "Total spent",
            "total_liters": "Total liters",
            "average_price": "Avg price \u20ac/L",
            "average_monthly_spend": "Avg monthly spend",
            "entries_count": "Refuels count",
            "best_price": "Best price",
            "worst_price": "Worst price",
        }
        for column, (key, label) in enumerate(labels.items()):
            frame = tb.Frame(summary_grid, padding=10)
            frame.grid(row=0, column=column, sticky=W)
            tb.Label(frame, text=label, font=("Helvetica", 10, "bold")).pack(anchor=W)
            value_var = tk.StringVar(value="-")
            tb.Label(frame, textvariable=value_var, font=("Helvetica", 12)).pack(anchor=W)
            self.summary_vars[key] = value_var

    def _build_table(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Refuel history", padding=(15, 10))
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ("date", "liters", "amount", "price", "station", "odo")
        self.tree = tb.Treeview(
            section, columns=columns, show="headings", height=8, bootstyle="dark",
        )
        headings = {
            "date": "Date", "liters": "Liters", "amount": "Amount",
            "price": "\u20ac/L", "station": "Station", "odo": "Odometer",
        }
        for name, text in headings.items():
            self.tree.heading(name, text=text)
            self.tree.column(name, anchor=CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _build_chart(self, parent: tk.Widget) -> None:
        section = tb.Labelframe(parent, text="Monthly spend", padding=(15, 10))
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        btn_frame = tb.Frame(section)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        tb.Button(
            btn_frame, text="Delete selected",
            command=self._on_delete, bootstyle="danger",
        ).pack(side=RIGHT)
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Spend (\u20ac)")
        self.ax.set_title("Monthly trend")
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
            messagebox.showerror("Invalid date", "Enter date in YYYY-MM-DD format")
            return
        try:
            liters = float(self.liters_var.get())
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Invalid values", "Liters and amount must be numbers")
            return
        if liters <= 0 or amount <= 0:
            messagebox.showerror("Invalid values", "Liters and amount must be positive")
            return
        if self.price_var.get().strip():
            try:
                price = float(self.price_var.get())
            except ValueError:
                messagebox.showerror("Invalid price", "Price must be a number")
                return
        else:
            price = amount / liters
        station = self.station_var.get().strip() or None
        odometer_raw = self.odometer_var.get().strip()
        odometer_km: float | None = float(odometer_raw) if odometer_raw else None

        entry = RefuelEntry(
            refuel_date=refuel_date, liters=liters, amount_paid=amount,
            price_per_liter=price, station=station, odometer_km=odometer_km,
        )
        self.entries = self.datastore.append_entry(entry)
        self._clear_form()
        self._refresh_dashboard()
        messagebox.showinfo("Refuel saved", "The refuel has been recorded successfully")

    def _on_delete(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a refuel to delete")
            return

        # Retrieve entry index stored in iid
        iid = selected[0]
        idx = int(iid)

        entry = self.entries[idx]
        confirm_msg = (
            f"Delete this refuel?\n\n"
            f"Date: {entry.refuel_date}\n"
            f"Liters: {entry.liters:.2f}\n"
            f"Amount: \u20ac{entry.amount_paid:.2f}\n"
            f"Station: {entry.station or '-'}"
        )
        if not messagebox.askyesno("Confirm delete", confirm_msg):
            return

        try:
            self.entries = self.datastore.delete_entry(idx)
        except IndexError:
            messagebox.showerror("Error", "Entry not found")
            return
        self._refresh_dashboard()
        messagebox.showinfo("Deleted", "The refuel has been deleted")

    def _on_export_pdf(self) -> None:
        if not self.entries:
            messagebox.showwarning("No data", "No data to export")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="benzatracker_report.pdf",
        )
        if file_path:
            try:
                ReportGenerator(file_path).generate(self.entries)
                messagebox.showinfo("Export complete", f"Report saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Export error", f"Error during export: {e}")

    def _on_export_csv(self) -> None:
        if not self.entries:
            messagebox.showwarning("No data", "No data to export")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="benzatracker_export.csv",
        )
        if file_path:
            try:
                with Path(file_path).open("w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Liters", "Amount", "Price/L", "Station", "Odometer (km)"])
                    for e in sorted(self.entries, key=lambda x: x.refuel_date):
                        writer.writerow([
                            e.refuel_date.strftime(DATE_FORMAT),
                            e.liters,
                            e.amount_paid,
                            e.price_per_liter,
                            e.station or "",
                            e.odometer_km or "",
                        ])
                messagebox.showinfo("Export complete", f"CSV exported to: {file_path}")
            except Exception as e:
                messagebox.showerror("Export error", f"Error exporting CSV: {e}")

    # Helpers ----------------------------------------------------------------
    def _clear_form(self) -> None:
        for var in (self.date_var, self.liters_var, self.amount_var,
                     self.price_var, self.station_var, self.odometer_var):
            var.set("")

    def _refresh_dashboard(self) -> None:
        self._update_summary()
        self._update_table()
        self._update_chart()

    def _update_summary(self) -> None:
        report = compute(self.entries)
        self.summary_vars["total_spent"].set(f"\u20ac {report.total_spent:.2f}")
        self.summary_vars["total_liters"].set(f"{report.total_liters:.2f} L")
        self.summary_vars["average_price"].set(f"\u20ac {report.average_price:.3f}")
        self.summary_vars["average_monthly_spend"].set(f"\u20ac {report.average_monthly_spend:.2f}")
        self.summary_vars["entries_count"].set(str(report.entries_count))
        if report.best_price:
            d, p = report.best_price
            self.summary_vars["best_price"].set(f"\u20ac {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["best_price"].set("-")
        if report.worst_price:
            d, p = report.worst_price
            self.summary_vars["worst_price"].set(f"\u20ac {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["worst_price"].set("-")

    def _update_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        # Display in reverse chronological order
        for idx, entry in enumerate(self.entries):
            self.tree.insert(
                "", END, iid=str(idx),
                values=(
                    entry.refuel_date.strftime("%d/%m/%Y"),
                    f"{entry.liters:.2f}",
                    f"\u20ac {entry.amount_paid:.2f}",
                    f"\u20ac {entry.price_per_liter:.3f}",
                    entry.station or "-",
                    f"{entry.odometer_km:.0f} km" if entry.odometer_km else "-",
                ),
            )

    def _update_chart(self) -> None:
        self.ax.clear()
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Spend (\u20ac)")
        self.ax.set_title("Monthly trend")
        monthly_data = monthly_spend(self.entries)
        if monthly_data:
            months = [m.strftime("%b %Y") for m, _ in monthly_data]
            values = [v for _, v in monthly_data]
            bars = self.ax.bar(months, values, color="#3cb371")
            self.ax.bar_label(bars, fmt="\u20ac %.0f")
        else:
            self.ax.text(
                0.5, 0.5, "No data available",
                ha="center", va="center", transform=self.ax.transAxes,
            )
        self.figure.tight_layout()
        self.canvas.draw_idle()


def run() -> None:
    app = BenzaTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    run()
