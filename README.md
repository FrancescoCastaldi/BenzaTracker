# BenzaTracker

Una mini applicazione desktop per monitorare i rifornimenti di benzina con un'interfaccia moderna e indicatori utili.

## Funzionalità principali

- Inserimento guidato di data, litri, importo, prezzo al litro e benzinaio.
- Dashboard con KPI: totale speso, litri totali, prezzo medio, spesa media mensile e migliori/peggiori prezzi.
- Storico dei rifornimenti con tabella ordinata.
- Grafico a barre dell'andamento della spesa mensile.
- Persistenza dei dati sul disco (`~/.benzatracker/refuels.json`).

## Anteprima interfaccia

L'interfaccia principale mostra un form per inserire i rifornimenti e una serie di KPI sintetici.
Sono inoltre presenti una tabella con lo storico e un grafico a barre della spesa mensile.

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
