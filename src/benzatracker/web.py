"""Flask web interface for BenzaTracker.

Usage::

    DATA_DIR=./data python -m benzatracker.web
"""
from __future__ import annotations

import csv
import io
import os
import tempfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from flask import Flask, redirect, render_template, request, send_file, url_for  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from . import config
from .kpi import compute, monthly_spend
from .models import DATE_FORMAT, RefuelEntry
from .pdf import ReportGenerator
from .store import create_store

app = Flask(__name__)
store = create_store(config.get_data_dir())


# ── helpers ─────────────────────────────────────────────────────────────────


def _build_chart_bytes(entries: list[RefuelEntry]) -> bytes | None:
    monthly_data = monthly_spend(entries)
    if not monthly_data:
        return None
    fig = Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)
    months = [m.strftime("%b %Y") for m, _ in monthly_data]
    values = [v for _, v in monthly_data]
    bars = ax.bar(months, values, color="#3cb371")
    ax.bar_label(bars, fmt="\u20ac %.0f")
    ax.set_xlabel("Month")
    ax.set_ylabel("Spend (\u20ac)")
    ax.set_title("Monthly trend")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf.getvalue()


# ── routes ──────────────────────────────────────────────────────────────────


@app.route("/")
def dashboard():
    entries = store.load_entries()
    kpi = compute(entries)
    return render_template("index.html", kpi=kpi, chart_available=bool(entries))


@app.route("/chart")
def chart():
    entries = store.load_entries()
    png_data = _build_chart_bytes(entries)
    if png_data is None:
        return "", 204
    return send_file(io.BytesIO(png_data), mimetype="image/png")


@app.route("/entries")
def entries_list():
    entries = store.load_entries()
    return render_template("entries.html", entries=entries)


@app.route("/entries/add", methods=["POST"])
def entries_add():
    try:
        refuel_date = datetime.strptime(request.form["refuel_date"], DATE_FORMAT).date()
    except (KeyError, ValueError):
        return "Invalid date (use YYYY-MM-DD)", 400
    try:
        liters = float(request.form["liters"])
        amount_paid = float(request.form["amount_paid"])
    except (KeyError, ValueError):
        return "Liters and amount must be numeric", 400
    if liters <= 0 or amount_paid <= 0:
        return "Liters and amount must be positive", 400

    price_raw = request.form.get("price_per_liter", "").strip()
    price_per_liter = float(price_raw) if price_raw else round(amount_paid / liters, 3)

    station = request.form.get("station", "").strip() or None
    odometer_raw = request.form.get("odometer_km", "").strip()
    odometer_km: float | None = float(odometer_raw) if odometer_raw else None

    entry = RefuelEntry(refuel_date, liters, amount_paid, price_per_liter, station, odometer_km)
    store.append_entry(entry)
    return redirect(url_for("entries_list"))


@app.route("/entries/<int:index>/delete", methods=["POST"])
def entries_delete(index: int):
    try:
        store.delete_entry(index)
    except IndexError:
        return "Refuel not found", 404
    return redirect(url_for("entries_list"))


@app.route("/report")
def report():
    entries = store.load_entries()
    if not entries:
        return "No data to export", 400
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        ReportGenerator(tmp.name).generate(entries)
        return send_file(
            tmp.name,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="benzatracker_report.pdf",
        )
    finally:
        Path(tmp.name).unlink(missing_ok=True)


@app.route("/export/csv")
def export_csv():
    entries = store.load_entries()
    if not entries:
        return "No data to export", 400

    buf = io.StringIO()
    writer = csv.writer(buf)
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
    buf.seek(0)
    return send_file(
        io.BytesIO(buf.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="benzatracker_export.csv",
    )


# ── entry point ─────────────────────────────────────────────────────────────


def run() -> None:
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    run()
