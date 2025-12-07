# BenzaTracker - PDF Export Feature Setup Guide

## Overview
This guide explains how to complete the PDF export feature integration for BenzaTracker. The core PDF generation module (`pdf_report.py`) has been created, but the GUI integration requires manual updates to `gui.py` to ensure proper functionality.

## What's Already Done ✓

1. **PDF Report Generator Module** (`benzatracker/pdf_report.py`)
   - Complete PDF generation functionality
   - Generates professional reports with KPI summaries
   - Includes detailed refuel entry tables
   - Uses ReportLab for styling and formatting

2. **Dependencies Updated** (`requirements.txt`)
   - Added `reportlab>=4.0.0` for PDF generation

3. **Documentation** (`benzatracker/MODIFICATIONS.md`)
   - Detailed step-by-step instructions for GUI integration
   - Code snippets ready to copy-paste

## What You Need to Do

### Step 1: Update Dependencies
Run this command to install the new dependency:
```bash
pip install -r requirements.txt
```
or directly:
```bash
pip install reportlab>=4.0.0
```

### Step 2: Update `benzatracker/gui.py`
Follow these modifications in order:

#### 2a. Add imports (after line 16)
Add these three lines after the existing imports:
```python
from .pdf_report import PDFReportGenerator
from pathlib import Path
from tkinter import filedialog
```

#### 2b. Add Export Button (in `_build_form` method, after line ~63)
Find the button_frame section where "Salva rifornimento" button is added, and add this after:
```python
tb.Button(
    button_frame, text="Esporta PDF", 
    command=self._on_export_pdf, 
    bootstyle="info"
).pack(side=RIGHT, padx=5)
```

#### 2c. Add Export Method (after `_on_submit` method, around line ~160)
Add this complete method:
```python
def _on_export_pdf(self) -> None:
    """Export current data to PDF report."""
    if not self.entries:
        messagebox.showwarning(
            "Nessun dato", 
            "Non ci sono dati da esportare"
        )
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

## Feature Description

Once implemented, the PDF export feature allows users to:

1. **Click the "Esporta PDF" button** in the main application window (appears next to "Salva rifornimento")
2. **Choose a save location** via the standard file dialog
3. **Generate a professional PDF report** containing:
   - **KPI Summary Section**
     - Total spent (€)
     - Total liters
     - Average price per liter
     - Average monthly spend
     - Number of refuel entries
     - Best price (with date)
     - Worst price (with date)
   - **Detailed Entries Table**
     - Date (formatted as DD/MM/YYYY)
     - Liters
     - Amount paid
     - Price per liter
     - Station name

4. **Save the PDF** to the specified location with an informative success message

## Report Format

The PDF reports are generated with:
- **Professional Layout**: A4 size with proper margins
- **Color Styling**: Blue headers, alternating row backgrounds
- **Formatted Tables**: Well-organized with proper alignment
- **Italian Localization**: All labels and messages in Italian

## Usage Example

```python
# The feature is fully integrated and accessible through the GUI
# Users simply:
# 1. Add refuel entries through the form
# 2. Click "Esporta PDF"
# 3. Select save location
# 4. PDF is generated and saved automatically
```

## Troubleshooting

### Issue: "Module 'pdf_report' not found"
**Solution**: Ensure you've added the import statement correctly:
```python
from .pdf_report import PDFReportGenerator
```

### Issue: "reportlab module not found"
**Solution**: Install the dependency:
```bash
pip install reportlab>=4.0.0
```

### Issue: PDF export button doesn't appear
**Solution**: Verify the button code was added to the `_build_form` method in the correct location (after the "Salva rifornimento" button)

## Files Involved

- `benzatracker/pdf_report.py` - PDF generation logic (NEW)
- `benzatracker/gui.py` - GUI integration (NEEDS UPDATE)
- `requirements.txt` - Dependencies (UPDATED)
- `benzatracker/MODIFICATIONS.md` - Detailed instructions (NEW)

## Next Steps

1. Copy the code from MODIFICATIONS.md
2. Paste it into gui.py in the specified locations
3. Test the feature by adding refuel entries and exporting to PDF
4. Verify the PDF is created with proper formatting

## Testing the Feature

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py

# 3. Add some test data
# 4. Click "Esporta PDF"
# 5. Choose save location and verify PDF is generated
```
