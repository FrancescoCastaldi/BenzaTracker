# BenzaTracker

Un semplice strumento a riga di comando per registrare i rifornimenti di benzina e consultare rapidamente KPI e storico.

## Funzionalità principali

- Inserimento guidato di data, litri, importo, contachilometri e benzinaio direttamente dal terminale.
- KPI sintetici (totale speso, litri totali, prezzo medio, spesa media mensile, miglior/peggior prezzo, rendimento medio km/L e consumo medio L/100km).
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

Durante l'inserimento di un rifornimento puoi lasciare vuoto il campo contachilometri se non disponibile. I KPI sui consumi (km/L e L/100km) verranno mostrati solo quando sono presenti almeno due registrazioni consecutive con il contachilometri compilato.

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
