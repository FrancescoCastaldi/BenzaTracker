# BenzaTracker

[![CI](https://github.com/FrancescoCastaldi/BenzaTracker/actions/workflows/python-app.yml/badge.svg)](https://github.com/FrancescoCastaldi/BenzaTracker/actions/workflows/python-app.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/FrancescoCastaldi/BenzaTracker/pulls)

> Applicazione desktop e CLI per tracciare i rifornimenti di carburante, calcolare KPI di spesa e generare report PDF.

---

## ✨ Funzionalità

| Feature | Dettaglio |
|---|---|
| 📋 **Inserimento rifornimenti** | Data, litri, importo, prezzo/L e benzinaio |
| 📊 **Dashboard KPI** | Totale speso, litri totali, prezzo medio, spesa mensile |
| 📈 **Grafico spesa mensile** | Barchart interattivo con matplotlib |
| 📄 **Export PDF** | Report completo con tabella e grafici via ReportLab |
| 💾 **Persistenza locale** | `~/.benzatracker/refuels.json` con scrittura atomica |
| 🖥️ **GUI + CLI** | Interfaccia ttkbootstrap e fallback testuale |

---

## 🚀 Installazione

### Prerequisiti

- Python **3.10** o superiore
- `pip`

### macOS / Linux

```bash
git clone https://github.com/FrancescoCastaldi/BenzaTracker.git
cd BenzaTracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bat
git clone https://github.com/FrancescoCastaldi/BenzaTracker.git
cd BenzaTracker
install_and_run.bat
```

---

## ▶️ Utilizzo

### Interfaccia grafica

```bash
python -m benzatracker.gui
# oppure
python main.py
```

### Interfaccia CLI

```bash
python -m benzatracker.cli
```

---

## 🧪 Test

```bash
pip install pytest
pytest
```

I test coprono `DataStore`, `KPI` e il flusso CLI su Windows.

---

## 🗂 Struttura del progetto

```
BenzaTracker/
├── main.py                    # Entry point GUI
├── requirements.txt           # Dipendenze runtime
├── pyproject.toml             # Metadata progetto + config ruff/mypy
├── pytest.ini                 # Configurazione pytest
├── install_and_run.bat        # Installer Windows
├── benzatracker/
│   ├── __init__.py
│   ├── data_store.py          # Persistenza (atomic write)
│   ├── kpi.py                 # Calcolo KPI e aggregazioni
│   ├── cli.py                 # Interfaccia CLI
│   ├── gui.py                 # Interfaccia grafica ttkbootstrap
│   └── pdf_report.py          # Export PDF con ReportLab
└── tests/
    ├── test_data_store.py
    ├── test_kpi.py
    └── test_cli_windows.py
```

---

## 🤝 Contribuire

1. Fai un fork del repository
2. Crea un branch: `git checkout -b feat/nome-feature`
3. Committa con [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`
4. Apri una Pull Request descrivendo le modifiche

```bash
# Setup pre-commit (opzionale ma consigliato)
pip install pre-commit
pre-commit install
```

---

## 📜 Changelog

Vedi [CHANGELOG.md](CHANGELOG.md) per la cronologia delle versioni.

---

## 📄 Licenza

Distribuito sotto licenza **MIT**. Vedi [LICENSE](LICENSE) per i dettagli.
