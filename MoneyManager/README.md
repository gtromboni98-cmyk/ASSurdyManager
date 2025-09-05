# MoneyManager - Sistema di Gestione Pagamenti

Un sistema Python per la gestione dei pagamenti con aggiornamento automatico di file Excel e invio di alert su WhatsApp.

## Struttura del Progetto

```
MoneyManager/
│
├── src/
│   └── main.py         # Script principale
│
├── data/
│   ├── pagamenti.xlsx  # File Excel con i pagamenti
│   └── updates.json    # File JSON con gli aggiornamenti
│
└── requirements.txt    # Dipendenze del progetto
```

## Prerequisiti

1. Python 3.8 o superiore
2. WhatsApp Web configurato sul browser predefinito

## Setup

1. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

2. Prepara i file:
   - Crea un file Excel `data/pagamenti.xlsx` con le colonne: Nome, importo, pagato, telefono, scadenza
   - Modifica il file `data/updates.json` con i tuoi dati

## Utilizzo

Per eseguire il programma:

```bash
python src/main.py
```

Il programma:
1. Carica i dati da Excel e JSON
2. Aggiorna il file Excel con i nuovi dati
3. Invia alert WhatsApp per i pagamenti non effettuati
4. Salva le modifiche nel file Excel

## Formato JSON

```json
[
    {
        "nome": "Nome Cognome",
        "importo": 1000,
        "pagato": false,
        "telefono": "+39123456789",
        "scadenza": "2025-09-15"
    }
]
```

## Note
- I numeri di telefono devono essere nel formato internazionale (es. "+39" per l'Italia)
- WhatsApp Web deve essere già configurato sul browser
- Il primo utilizzo richiederà la scansione del QR code di WhatsApp
