# BenzaTracker

Un'applicazione desktop che permette di registrare i rifornimenti e monitorare KPI, storico e spesa mensile attraverso un'interfaccia grafica. L'interfaccia a riga di comando resta disponibile per chi preferisce il terminale.

## Funzionalità principali

- Interfaccia grafica completa con form di inserimento rapido, schede KPI e grafico a barre della spesa mensile.
- Inserimento guidato di data, litri, importo, contachilometri e benzinaio con validazioni immediate.
- KPI sintetici (totale speso, litri totali, prezzo medio, spesa media mensile, miglior/peggior prezzo, rendimento medio km/L e consumo medio L/100km).
- Storico rifornimenti con possibilità di aggiornare il contachilometri o eliminare una registrazione direttamente dalla GUI.
- Grafico dinamico della spesa mensile aggiornato automaticamente ad ogni modifica.
- Persistenza dei dati sul disco (`~/.benzatracker/refuels.json`).
- Interfaccia a riga di comando opzionale con filtro "10 del mese" per le analisi periodiche dal terminale.

## Requisiti

- macOS o Windows con Python 3.10 o superiore.
- Tkinter (incluso nella maggior parte delle installazioni Python) e Matplotlib per il grafico incorporato.

## Installazione rapida su macOS (GUI)

Esegui lo script di installazione che crea un ambiente virtuale, installa (se necessario) le dipendenze e avvia la GUI:

```bash
./install_mac.sh
```

Al primo avvio potrebbe essere necessario concedere i permessi di esecuzione:

```bash
chmod +x install_mac.sh
```

## Utilizzo su Windows (PowerShell)

Lancia il file batch che prepara automaticamente l'ambiente virtuale e avvia la GUI:

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
python -m benzatracker.gui
```

Durante l'inserimento puoi lasciare vuoto il campo contachilometri se non disponibile. I KPI sui consumi (km/L e L/100km) vengono mostrati automaticamente quando sono presenti almeno due registrazioni consecutive con il contachilometri compilato. Usa i pulsanti sotto la tabella per aggiornare il valore o eliminare un rifornimento.

Se preferisci la modalità testuale puoi avviare la CLI manualmente:

```bash
python -m benzatracker.cli
```

La CLI mantiene tutte le funzioni avanzate, incluso il filtro "10 del mese" per consultare rapidamente i rifornimenti compresi fra il 10 del mese scorso, il 10 del mese corrente e il 10 del mese successivo con KPI dedicati.

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
│  ├─ gui.py              # Interfaccia grafica
│  ├─ cli.py              # Interfaccia a riga di comando
│  └─ kpi.py              # Calcolo indicatori e aggregazioni
└─ tests/
   ├─ test_data_store.py  # Test per operazioni di persistenza
   └─ test_kpi.py         # Test automatici per i KPI
```
