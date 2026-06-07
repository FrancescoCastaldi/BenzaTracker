"""GUI application for BenzaTracker (ttkbootstrap / tkinter).

Tech-minimal theme: black/grey/brown/orange palette with inline validation
that preserves form state on errors (non-blocking pipeline).
"""
from __future__ import annotations

import csv
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict

import matplotlib

matplotlib.use("TkAgg")
import ttkbootstrap as tb  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from ttkbootstrap.constants import BOTH, CENTER, END, LEFT, RIGHT, W  # noqa: E402
from ttkbootstrap.scrolled import ScrolledFrame  # noqa: E402
from ttkbootstrap.style import ThemeDefinition  # noqa: E402

from . import config
from .kpi import compute, monthly_spend
from .models import DATE_FORMAT, RefuelEntry
from .pdf import ReportGenerator
from .store import create_store

# ── custom palette ────────────────────────────────────────────────────────────

C = {
    "bg": "#0d0d0d",
    "surface": "#1a1a1a",
    "surface2": "#242424",
    "surface3": "#2a2a2a",
    "border": "#333333",
    "text": "#e8ddd0",
    "text_muted": "#7a7066",
    "accent": "#d4893a",
    "accent_hover": "#e8993f",
    "brown": "#8b7355",
    "danger": "#c0392b",
    "success": "#27ae60",
    "error": "#e74c3c",
    "warning": "#e67e22",
}

_THEME_DEF = ThemeDefinition(
    name="techminimal",
    colors={
        "primary": C["accent"],
        "secondary": C["brown"],
        "success": C["success"],
        "info": C["accent"],
        "warning": C["warning"],
        "danger": C["danger"],
        "light": C["text_muted"],
        "dark": C["surface"],
        "bg": C["bg"],
        "fg": C["text"],
        "selectbg": C["accent"],
        "selectfg": C["bg"],
        "border": C["border"],
        "inputfg": C["text"],
        "inputbg": C["surface2"],
    },
)


# ── validation helpers ──────────────────────────────────────────────────────


class _Field:
    """Wraps a form field: StringVar, Entry, and inline error label."""

    def __init__(
        self, parent: tk.Widget, label: str, row: int, col: int,
        width: int = 20,
    ) -> None:
        self.error_var = tk.StringVar(value="")
        self.var = tk.StringVar()
        self.label_text = label
        self._row = row
        self._col = col

        # trace clears error on edit
        self.var.trace_add("write", lambda *_: self.error_var.set(""))

        frame = tb.Frame(parent, padding=3)
        frame.grid(row=row, column=col, padx=4, pady=2, sticky="n")

        lbl = tb.Label(frame, text=label, font=("Segoe UI", 9))
        lbl.pack(anchor=W)

        self.entry = tb.Entry(frame, textvariable=self.var, width=width)
        self.entry.pack(fill=tk.X, pady=(1, 0))

        self.error_lbl = tb.Label(
            frame, textvariable=self.error_var,
            font=("Segoe UI", 8), foreground=C["error"],
        )
        self.error_lbl.pack(anchor=W, pady=(0, 0))

    def get(self) -> str:
        return self.var.get().strip()

    def set_error(self, msg: str) -> None:
        self.error_var.set(msg)

    def set(self, value: str) -> None:
        self.var.set(value)

    def clear(self) -> None:
        self.var.set("")
        self.error_var.set("")


# ── application ──────────────────────────────────────────────────────────────


class BenzaTrackerApp(tb.Window):
    """Main GUI application with tech-minimal styling."""

    def __init__(self) -> None:
        super().__init__(themename="techminimal", title="BenzaTracker")
        self.geometry("1220x780")
        self.minsize(900, 600)
        self.datastore = create_store(config.get_data_dir())
        self.entries: list[RefuelEntry] = self.datastore.load_entries()
        self._configure_styles()
        self._build_layout()
        self._refresh_dashboard()

    # ── custom styling ──────────────────────────────────────────────────────

    def _configure_styles(self) -> None:
        style = tb.Style()
        # Register & apply custom theme
        try:
            style.register_theme(_THEME_DEF)
            style.theme_use("techminimal")
        except Exception:
            pass  # fall back to darkly if registration fails

        # ── ttk widget overrides ────────────────────────────────────────────
        style.configure(".", background=C["bg"])

        style.configure(
            "TLabel", background=C["surface"], foreground=C["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Heading.TLabel", background=C["bg"], foreground=C["accent"],
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Subhead.TLabel", background=C["surface"], foreground=C["text_muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Card.TFrame", background=C["surface"], relief="flat",
            borderwidth=0,
        )
        style.configure(
            "TFrame", background=C["bg"],
        )
        style.configure(
            "TLabelframe", background=C["bg"], foreground=C["accent"],
            font=("Segoe UI", 11, "bold"), relief="flat", borderwidth=0,
        )
        style.configure(
            "TLabelframe.Label", background=C["bg"], foreground=C["accent"],
            font=("Segoe UI", 11, "bold"),
        )
        # Accent / outline buttons
        style.configure(
            "Accent.TButton", font=("Segoe UI", 10),
        )
        # KPI value label
        style.configure(
            "KPI.TLabel", background=C["surface"], foreground=C["text"],
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "KPI-label.TLabel", background=C["surface"], foreground=C["text_muted"],
            font=("Segoe UI", 8),
        )
        # Error label
        style.configure(
            "Error.TLabel", background=C["bg"], foreground=C["error"],
            font=("Segoe UI", 8),
        )
        # Delete button (outlined danger)
        style.configure(
            "Delete.TButton", font=("Segoe UI", 9),
        )

        # Treeview
        style.configure(
            "Treeview", background=C["surface2"], fieldbackground=C["surface2"],
            foreground=C["text"], rowheight=28, font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading", background=C["surface"], foreground=C["accent"],
            font=("Segoe UI", 9, "bold"), relief="flat",
        )
        style.map(
            "Treeview.Heading", background=[("active", C["surface3"])],
        )
        style.map(
            "Treeview",
            background=[("selected", C["accent"])],
            foreground=[("selected", C["bg"])],
        )

        # Separator
        style.configure(
            "TSeparator", background=C["border"],
        )

    # ── layout ──────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        main_frame = ScrolledFrame(self, autohide=True, padding=(20, 15))
        main_frame.pack(fill=BOTH, expand=True)
        container = tb.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True)

        self._build_form(container)
        self._build_summary(container)
        self._build_table(container)
        self._build_chart(container)

    def _build_form(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, style="Card.TFrame", padding=(15, 12))
        section.pack(fill=tk.X, padx=0, pady=(0, 10))

        # Header row
        hdr = tb.Frame(section, style="Card.TFrame")
        hdr.pack(fill=tk.X)
        tb.Label(hdr, text="New refuel", style="Heading.TLabel").pack(
            side=LEFT, anchor=W,
        )

        csv_btn = tb.Button(
            hdr, text="Export CSV",
            command=self._on_export_csv, bootstyle="secondary-outline",
        )
        csv_btn.pack(side=RIGHT, padx=(5, 0))

        pdf_btn = tb.Button(
            hdr, text="Export PDF",
            command=self._on_export_pdf, bootstyle="secondary-outline",
        )
        pdf_btn.pack(side=RIGHT, padx=(5, 0))

        # Form grid
        form_frame = tb.Frame(section, style="Card.TFrame")
        form_frame.pack(fill=tk.X, pady=(10, 0))

        self.fields: Dict[str, _Field] = {}
        field_defs = [
            ("date", "Date (YYYY-MM-DD)", 0),
            ("liters", "Liters", 1),
            ("amount", "Amount (\u20ac)", 2),
            ("price", "Price \u20ac/L (optional)", 3),
            ("station", "Station (optional)", 4),
            ("odometer", "Odometer km (optional)", 5),
        ]
        for key, label, col in field_defs:
            self.fields[key] = _Field(form_frame, label, 0, col)

        # Button row
        btn_frame = tb.Frame(section, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        tb.Button(
            btn_frame, text="Save refuel",
            command=self._on_submit, bootstyle="Accent",
        ).pack(side=RIGHT)

    def _build_summary(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, style="Card.TFrame", padding=(15, 12))
        section.pack(fill=tk.X, padx=0, pady=(0, 10))

        tb.Label(section, text="KPIs", style="Heading.TLabel").pack(
            anchor=W, pady=(0, 10),
        )

        grid = tb.Frame(section, style="Card.TFrame")
        grid.pack(fill=tk.X)

        self.summary_vars: dict[str, tk.StringVar] = {}
        kpi_defs = [
            ("total_spent", "Total spent"),
            ("total_liters", "Total liters"),
            ("average_price", "Avg price \u20ac/L"),
            ("average_monthly_spend", "Avg monthly spend"),
            ("entries_count", "Refuels"),
            ("best_price", "Best price"),
            ("worst_price", "Worst price"),
        ]
        for col, (key, label_text) in enumerate(kpi_defs):
            card = tb.Frame(grid, style="Card.TFrame", padding=(10, 6))
            card.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)
            grid.columnconfigure(col, weight=1)
            tb.Label(card, text=label_text, style="KPI-label.TLabel").pack(
                anchor=W,
            )
            value_var = tk.StringVar(value="-")
            value_lbl = tb.Label(card, textvariable=value_var, style="KPI.TLabel")
            value_lbl.pack(anchor=W)
            self.summary_vars[key] = value_var

    def _build_table(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, style="Card.TFrame", padding=(15, 12))
        section.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 10))

        hdr = tb.Frame(section, style="Card.TFrame")
        hdr.pack(fill=tk.X)
        tb.Label(hdr, text="Refuel history", style="Heading.TLabel").pack(
            side=LEFT, anchor=W,
        )
        tb.Button(
            hdr, text="Delete selected",
            command=self._on_delete, bootstyle="danger-outline",
        ).pack(side=RIGHT)

        columns = ("date", "liters", "amount", "price", "station", "odo")
        self.tree = tb.Treeview(
            section, columns=columns, show="headings",
            height=8, bootstyle="dark",
        )
        headings = {
            "date": "Date", "liters": "Liters", "amount": "Amount",
            "price": "\u20ac/L", "station": "Station", "odo": "Odometer",
        }
        for name, text in headings.items():
            self.tree.heading(name, text=text)
            self.tree.column(name, anchor=CENTER, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _build_chart(self, parent: tk.Widget) -> None:
        section = tb.Frame(parent, style="Card.TFrame", padding=(15, 12))
        section.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))

        tb.Label(section, text="Monthly spend", style="Heading.TLabel").pack(
            anchor=W, pady=(0, 8),
        )

        self.figure = Figure(figsize=(7, 3), dpi=100)
        self.figure.patch.set_facecolor(C["surface"])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(C["surface"])
        self.ax.set_xlabel("Month", color=C["text_muted"])
        self.ax.set_ylabel("Spend (\u20ac)", color=C["text_muted"])
        self.ax.set_title("Monthly trend", color=C["text"], fontsize=11)
        self.ax.tick_params(colors=C["text_muted"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(C["border"])
        self.ax.grid(True, alpha=0.15, color=C["border"])

        self.canvas = FigureCanvasTkAgg(self.figure, master=section)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ── event handlers ──────────────────────────────────────────────────────

    def _on_submit(self) -> None:
        """Validate inline, show errors without clearing the form."""
        ok = True

        # date
        raw_date = self.fields["date"].get()
        if not raw_date:
            self.fields["date"].set_error("Required")
            ok = False
        else:
            try:
                refuel_date = datetime.strptime(raw_date, DATE_FORMAT).date()
            except ValueError:
                self.fields["date"].set_error("Use YYYY-MM-DD")
                ok = False

        # liters
        raw_liters = self.fields["liters"].get()
        if not raw_liters:
            self.fields["liters"].set_error("Required")
            ok = False
        else:
            try:
                liters = float(raw_liters)
                if liters <= 0:
                    self.fields["liters"].set_error("Must be positive")
                    ok = False
            except ValueError:
                self.fields["liters"].set_error("Enter a number")
                ok = False

        # amount
        raw_amount = self.fields["amount"].get()
        if not raw_amount:
            self.fields["amount"].set_error("Required")
            ok = False
        else:
            try:
                amount = float(raw_amount)
                if amount <= 0:
                    self.fields["amount"].set_error("Must be positive")
                    ok = False
            except ValueError:
                self.fields["amount"].set_error("Enter a number")
                ok = False

        if not ok:
            return  # form state preserved, user can fix and retry

        # price (optional)
        raw_price = self.fields["price"].get()
        if raw_price:
            try:
                price = float(raw_price)
            except ValueError:
                self.fields["price"].set_error("Enter a number")
                return
        else:
            price = amount / liters

        station = self.fields["station"].get() or None
        raw_odo = self.fields["odometer"].get()
        odometer_km: float | None = float(raw_odo) if raw_odo else None

        entry = RefuelEntry(
            refuel_date=refuel_date, liters=liters, amount_paid=amount,
            price_per_liter=round(price, 3), station=station,
            odometer_km=odometer_km,
        )
        self.entries = self.datastore.append_entry(entry)
        self._clear_form()
        self._refresh_dashboard()
        messagebox.showinfo(
            "Refuel saved",
            f"Saved: {liters:.2f} L \u00b7 \u20ac{amount:.2f} \u00b7 {refuel_date}",
        )

    def _on_delete(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        iid = selected[0]
        idx = int(iid)
        try:
            entry = self.entries[idx]
        except IndexError:
            return

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

    def _on_export_pdf(self) -> None:
        if not self.entries:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="benzatracker_report.pdf",
        )
        if file_path:
            try:
                ReportGenerator(file_path).generate(self.entries)
                messagebox.showinfo(
                    "Export complete", f"Report saved to: {file_path}",
                )
            except Exception as e:
                messagebox.showerror("Export error", str(e))

    def _on_export_csv(self) -> None:
        if not self.entries:
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
                    writer.writerow(
                        ["Date", "Liters", "Amount", "Price/L", "Station", "Odometer (km)"],
                    )
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
                messagebox.showerror("Export error", str(e))

    # ── helpers ─────────────────────────────────────────────────────────────

    def _clear_form(self) -> None:
        for field in self.fields.values():
            field.clear()

    def _refresh_dashboard(self) -> None:
        self.entries = self.datastore.load_entries()
        self._update_summary()
        self._update_table()
        self._update_chart()

    def _update_summary(self) -> None:
        report = compute(self.entries)
        self.summary_vars["total_spent"].set(f"\u20ac {report.total_spent:.2f}")
        self.summary_vars["total_liters"].set(f"{report.total_liters:.2f} L")
        self.summary_vars["average_price"].set(f"\u20ac {report.average_price:.3f}")
        self.summary_vars["average_monthly_spend"].set(
            f"\u20ac {report.average_monthly_spend:.2f}"
        )
        self.summary_vars["entries_count"].set(str(report.entries_count))

        if report.best_price:
            d, p = report.best_price
            self.summary_vars["best_price"].set(f"\u20ac {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["best_price"].set("N/A")

        if report.worst_price:
            d, p = report.worst_price
            self.summary_vars["worst_price"].set(f"\u20ac {p:.3f} ({d:%d/%m/%Y})")
        else:
            self.summary_vars["worst_price"].set("N/A")

    def _update_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
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
        self.ax.set_facecolor(C["surface"])
        self.ax.set_xlabel("Month", color=C["text_muted"])
        self.ax.set_ylabel("Spend (\u20ac)", color=C["text_muted"])
        self.ax.set_title("Monthly trend", color=C["text"], fontsize=11)
        self.ax.tick_params(colors=C["text_muted"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(C["border"])
        self.ax.grid(True, alpha=0.15, color=C["border"])

        monthly_data = monthly_spend(self.entries)
        if monthly_data:
            months = [m.strftime("%b %Y") for m, _ in monthly_data]
            values = [v for _, v in monthly_data]
            bars = self.ax.bar(
                months, values, color=C["accent"], edgecolor=C["accent_hover"],
                linewidth=0.6,
            )
            self.ax.bar_label(
                bars, fmt="\u20ac %.0f", color=C["text"], fontsize=8,
            )
        else:
            self.ax.text(
                0.5, 0.5, "No data available",
                ha="center", va="center", transform=self.ax.transAxes,
                color=C["text_muted"], fontsize=10,
            )

        self.figure.tight_layout()
        self.canvas.draw_idle()


def run() -> None:
    app = BenzaTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    run()
