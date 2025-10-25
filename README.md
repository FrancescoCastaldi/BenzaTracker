# BenzaTracker

Una mini applicazione desktop per monitorare i rifornimenti di benzina con un'interfaccia moderna e indicatori utili.

## Funzionalità principali

- Inserimento guidato di data, litri, importo, prezzo al litro e benzinaio.
- Dashboard con KPI: totale speso, litri totali, prezzo medio, spesa media mensile e migliori/peggiori prezzi.
- Storico dei rifornimenti con tabella ordinata.
- Grafico a barre dell'andamento della spesa mensile.
- Persistenza dei dati sul disco (`~/.benzatracker/refuels.json`).

## Requisiti

- macOS con Python 3.10 o superiore.

## Installazione rapida su macOS

Esegui lo script di installazione che crea un ambiente virtuale, installa le dipendenze e avvia l'applicazione:

```bash
./install_mac.sh
```

Al primo avvio potrebbe essere necessario concedere i permessi di esecuzione:

```bash
chmod +x install_mac.sh
```

## Esecuzione manuale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m benzatracker.cli
```

Durante l'inserimento di un rifornimento puoi lasciare vuoto il campo contachilometri se non disponibile. I KPI sui consumi (km/L e L/100km) verranno mostrati solo quando sono presenti almeno due registrazioni consecutive con il contachilometri compilato. Puoi sempre utilizzare le opzioni "Aggiorna contachilometri" ed "Elimina rifornimento" del menu principale per correggere o gestire le registrazioni esistenti.

La nuova voce di menu "Filtra periodi (10 del mese)" mostra rapidamente i rifornimenti compresi fra il 10 del mese scorso, il 10 del mese corrente e il 10 del mese successivo, includendo un riepilogo dei KPI per l'intervallo selezionato.

python -m benzatracker.gui
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
│  ├─ gui.py              # Interfaccia grafica e dashboard
│  └─ kpi.py              # Calcolo indicatori e aggregazioni
└─ tests/
   └─ test_kpi.py         # Test automatici per i KPI
```
