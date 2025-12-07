# PDF Report Feature - Implementation Guide

## Files Modified:

### 1. requirements.txt
Add the following line to the end:
```
reportlab>=4.0.0
```

### 2. gui.py - Changes needed:

#### Add import (after line 16):
```python
from .pdf_report import PDFReportGenerator
from pathlib import Path
from tkinter import filedialog
```

#### In _build_form method, after the Save button (around line ~60), add:
```python
tb.Button(
    button_frame, text="Esporta PDF", 
    command=self._on_export_pdf, 
    bootstyle="info"
).pack(side=RIGHT, padx=5)
```

#### Add new method to BenzaTrackerApp class (after _on_submit method):
```python
def _on_export_pdf(self) -> None:
    """Export current data to PDF report."""
    if not self.entries:
        messagebox.showwarning("Nessun dato", "Non ci sono dati da esportare")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        initialfile="benzatracker_report.pdf"
    )
    
    if file_path:
        try:
            generator = PDFReportGenerator(file_path)
            generator.generate_report(self.entries)
            messagebox.showinfo(
                "Esportazione completata",
                f"Report salvato in: {file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Errore esportazione",
                f"Errore durante l'esportazione: {str(e)}"
            )
```

## Files Already Created:
- `benzatracker/pdf_report.py` - Complete PDF generation module

## Summary:
The PDF export feature allows users to:
1. Click the "Esporta PDF" button in the application
2. Choose a location to save the PDF file
3. Generate a professional PDF report with:
   - KPI summary (total spent, average price, best/worst prices, etc.)
   - Detailed table of all refuel entries
   - Formatted with colors and proper styling
