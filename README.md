# BenzaTracker

Un semplice strumento a riga di comando per registrare i rifornimenti di benzina e consultare rapidamente KPI e storico.

## Funzionalità principali

- Inserimento guidato di data, litri, importo e benzinaio direttamente dal terminale.
- KPI sintetici (totale speso, litri totali, prezzo medio, spesa media mensile, miglior/peggior prezzo).
- Elenco dello storico rifornimenti in ordine cronologico.
- Aggregazione della spesa per mese.
- Persistenza dei dati sul disco (`~/.benzatracker/refuels.json`).

## Requisiti

- macOS con Python 3.10 o superiore.

## Installazione rapida su macOS

Esegui lo script di installazione che crea un ambiente virtuale, installa (se necessario) le dipendenze e avvia il programma:

```bash
./install_mac.sh
```

Al primo avvio potrebbe essere necessario concedere i permessi di esecuzione:

```bash
chmod +x install_mac.sh
```

## Utilizzo su Windows (PowerShell)

Lancia il file batch che prepara automaticamente l'ambiente virtuale e avvia il programma:

```powershell
./run_benzatracker.bat
```

Il comando funziona sia da PowerShell sia dal Prompt dei comandi.

## Esecuzione manuale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m benzatracker.cli
```

## Test

```bash
pytest
```

## Struttura del progetto

```
BenzaTracker/
├─ main.py                # Entry point
├─ install_mac.sh         # Installer per macOS
├─ requirements.txt       # Dipendenze Python
├─ benzatracker/
│  ├─ data_store.py       # Gestione persistenza
│  ├─ cli.py              # Interfaccia a riga di comando
│  └─ kpi.py              # Calcolo indicatori e aggregazioni
└─ tests/
   └─ test_kpi.py         # Test automatici per i KPI
```
