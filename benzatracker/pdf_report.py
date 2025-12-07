"""PDF report generation for BenzaTracker."""
from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from .data_store import RefuelEntry
from .kpi import KPIReport, compute_kpis

class PDFReportGenerator:
    """Generate PDF reports from refuel entries."""

    def __init__(self, filename: str | Path = "benzatracker_report.pdf") -> None:
        """Initialize the PDF generator.
        
        Args:
            filename: Path where PDF will be saved.
        """
        self.filename = Path(filename)

    def generate_report(
        self, entries: List[RefuelEntry], title: str = "BenzaTracker Report"
    ) -> Path:
        """Generate a PDF report from refuel entries.
        
        Args:
            entries: List of RefuelEntry objects.
            title: Report title.
            
        Returns:
            Path to the generated PDF file.
        """
        doc = SimpleDocTemplate(
            str(self.filename), pagesize=A4,
            rightMargin=0.5*inch, leftMargin=0.5*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2*inch))

        # KPI Summary
        if entries:
            kpi_report: KPIReport = compute_kpis(entries)
            story.append(self._build_kpi_section(kpi_report, styles))
            story.append(Spacer(1, 0.3*inch))
            
            # Entries table
            story.append(self._build_entries_table(entries, styles))

        # Build PDF
        doc.build(story)
        return self.filename

    def _build_kpi_section(self, kpi: KPIReport, styles) -> Table:
        """Build KPI summary section."""
        kpi_data = [
            ["KPI", "Valore"],
            ["Totale speso", f"€ {kpi.total_spent:.2f}"],
            ["Litri totali", f"{kpi.total_liters:.2f} L"],
            ["Prezzo medio €/L", f"€ {kpi.average_price:.3f}"],
            ["Spesa media mensile", f"€ {kpi.average_monthly_spend:.2f}"],
            ["Numero rifornimenti", str(kpi.entries_count)],
        ]
        
        if kpi.best_price:
            date_val, price = kpi.best_price
            kpi_data.append(["Miglior prezzo", f"€ {price:.3f} ({date_val:%d/%m/%Y})"])
        
        if kpi.worst_price:
            date_val, price = kpi.worst_price
            kpi_data.append(["Peggior prezzo", f"€ {price:.3f} ({date_val:%d/%m/%Y})"])

        table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        return table

    def _build_entries_table(self, entries: List[RefuelEntry], styles) -> Table:
        """Build detailed entries table."""
        sorted_entries = sorted(entries, key=lambda x: x.refuel_date, reverse=True)
        
        table_data = [
            ["Data", "Litri", "Importo", "€/L", "Benzinaio"]
        ]
        
        for entry in sorted_entries:
            table_data.append([
                entry.refuel_date.strftime("%d/%m/%Y"),
                f"{entry.liters:.2f}",
                f"€ {entry.amount_paid:.2f}",
                f"€ {entry.price_per_liter:.3f}",
                entry.station or "-"
            ])

        table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1*inch, 1.6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        return table
