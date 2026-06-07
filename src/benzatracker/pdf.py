"""PDF report generation via ReportLab."""
from __future__ import annotations

from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .kpi import compute
from .models import RefuelEntry


class ReportGenerator:
    """Generate PDF reports from refuel entries."""

    def __init__(self, filename: str | Path = "benzatracker_report.pdf") -> None:
        self.filename = Path(filename)

    def generate(
        self, entries: List[RefuelEntry], title: str = "BenzaTracker Report"
    ) -> Path:
        doc = SimpleDocTemplate(
            str(self.filename), pagesize=A4,
            rightMargin=0.5 * inch, leftMargin=0.5 * inch,
            topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Heading1"],
            fontSize=24, textColor=colors.HexColor("#1f77b4"),
            spaceAfter=30, alignment=1,
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        if entries:
            kpi = compute(entries)
            story.append(self._build_kpi_table(kpi, styles))
            story.append(Spacer(1, 0.3 * inch))
            story.append(self._build_entries_table(entries, styles))

        doc.build(story)
        return self.filename

    def _build_kpi_table(self, kpi, styles) -> Table:
        data = [
            ["KPI", "Value"],
            ["Total spent", f"\u20ac {kpi.total_spent:.2f}"],
            ["Total liters", f"{kpi.total_liters:.2f} L"],
            ["Average price \u20ac/L", f"\u20ac {kpi.average_price:.3f}"],
            ["Avg monthly spend", f"\u20ac {kpi.average_monthly_spend:.2f}"],
            ["Refuels count", str(kpi.entries_count)],
        ]
        if kpi.best_price:
            d, p = kpi.best_price
            data.append(["Best price", f"\u20ac {p:.3f} ({d:%d/%m/%Y})"])
        if kpi.worst_price:
            d, p = kpi.worst_price
            data.append(["Worst price", f"\u20ac {p:.3f} ({d:%d/%m/%Y})"])

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        return table

    def _build_entries_table(self, entries: List[RefuelEntry], styles) -> Table:
        sorted_entries = sorted(entries, key=lambda x: x.refuel_date, reverse=True)
        data = [["Date", "Liters", "Amount", "€/L", "Station", "Km"]]
        for entry in sorted_entries:
            data.append([
                entry.refuel_date.strftime("%d/%m/%Y"),
                f"{entry.liters:.2f}",
                f"€ {entry.amount_paid:.2f}",
                f"€ {entry.price_per_liter:.3f}",
                entry.station or "-",
                f"{entry.odometer_km:.0f}" if entry.odometer_km else "-",
            ])
        table = Table(data, colWidths=[1.2 * inch, 0.9 * inch, 1.1 * inch, 0.9 * inch, 1.3 * inch, 0.7 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
        ]))
        return table
