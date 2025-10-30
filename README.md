# BenzaTracker

Un semplice strumento a riga di comando per registrare i rifornimenti di benzina e consultare rapidamente KPI e storico.

## Funzionalità principali

- Inserimento guidato di data, litri, importo, contachilometri e benzinaio direttamente dal terminale.
- KPI sintetici (totale speso, litri totali, prezzo medio, spesa media mensile, miglior/peggior prezzo, rendimento medio km/L e consumo medio L/100km).
- Elenco dello storico rifornimenti in ordine cronologico con ID progressivi.
- Aggregazione della spesa per mese.
- Filtri rapidi sui periodi "10 del mese" (10 mese scorso → 10 mese corrente → 10 mese successivo).
- Aggiornamento del contachilometri anche dopo aver salvato il rifornimento.
- Eliminazione dei rifornimenti indesiderati.
- Persistenza dei dati sul disco (`~/.benzatracker/refuels.json`).

## Requisiti

- macOS o Windows con Python 3.10 o superiore.

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

Il comando funziona sia da PowerShell sia dal Prompt dei comandi. Se `python` non è disponibile, lo script prova automaticamente ad utilizzare il launcher `py` prima di creare l'ambiente virtuale.

### Creazione dell'eseguibile standalone (Windows)

Se preferisci distribuire o avviare BenzaTracker come eseguibile `.exe`, utilizza lo script PowerShell dedicato che si occupa di installare automaticamente PyInstaller e le dipendenze mancanti prima di generare il pacchetto:

```powershell
./build_windows_exe.ps1
```

Al termine troverai `BenzaTracker.exe` nella cartella `dist/`. L'eseguibile include il programma completo e può essere copiato su un altro PC Windows senza dover installare Python.

## Esecuzione manuale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m benzatracker.cli
```

Durante l'inserimento di un rifornimento puoi lasciare vuoto il campo contachilometri se non disponibile. I KPI sui consumi (km/L e L/100km) verranno mostrati solo quando sono presenti almeno due registrazioni consecutive con il contachilometri compilato. Puoi sempre utilizzare le opzioni "Aggiorna contachilometri" ed "Elimina rifornimento" del menu principale per correggere o gestire le registrazioni esistenti.

La nuova voce di menu "Filtra periodi (10 del mese)" mostra rapidamente i rifornimenti compresi fra il 10 del mese scorso, il 10 del mese corrente e il 10 del mese successivo, includendo un riepilogo dei KPI per l'intervallo selezionato.

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
   ├─ test_data_store.py  # Test per operazioni di persistenza
   └─ test_kpi.py         # Test automatici per i KPI
```
