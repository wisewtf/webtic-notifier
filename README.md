# Webtic Notifier

**Versione:** `UNDEF`

## Introduzione

`Webtic Notifier` è un piccolo esperimento in Python che esegue una logica di notifica ad ogni nuovo `evento` (inteso come programmazione cinematografica) da specificati cinema presenti sotto l'ombrello del sistema di ticketing `Webtic`.

"Esperimento" perché sono un sistemista e non un programmatore, quindi essendo ancora alle prime armi sto imparando cosa va fatto, come va fatto e se va fatto.

## Funzionalità

Al primo lancio, lo script invia due richieste HTTP `GET` a due endpoint della `API` di Webtic. La prima è la lista di tutti i cinema e la seconda è la lista degli eventi presenti nei cinema preconfigurati nel file `config.toml`. I dati raccolti vengono salvati in due `collection` di un database MongoDB. Per tutti i lanci successivi, lo script si occuperà di mantenere la lista dei cinema aggiornata e ogni qualvolta un nuovo evento (quindi un evento in aggiunta alla `collection` degli eventi) si presenta, allora una notifica di Telegram viene inviata nella chat preconfigurata.

## Roadmap

- [ ] Configurazione cinema per nome e non per ID
- [X] Inserimento primo orario nel messaggio di telegram
- [X] Rimozione libreria Apprise in favore di una semplicissima `POST` a Telegram
- [ ] Ampliamento documentazione per uso con CRON e SYSTEMD

## Installazione e uso

Questo capitolo è un work in progress. Sto ancora decidendo come meglio gestire il QoL di un utente medio.

### Materiale necessario per i capaci

1. Una macchina con Python (3.7+) che può eseguire lo script.
2. Un database MongoDB.
3. Le librerie: `requests`, `argparse`, `tomli` e `pymongo` (Io consiglio l'utilizzo di [poetry](https://python-poetry.org/) o [venv](https://docs.python.org/3/library/venv.html) per gestire le dipendenze)
4. `cron` o `systemd` timers per eseguire lo script ogni X.

Lo script può essere eseguito da un timer `systemd` o da un `cron`.

### Uso

Clonare questo repo.

`argparse` genera un tooltip utile a capire come lanciare lo script.

Lanciandolo senza argomenti otteniamo questo output:

```bash
❯ python .\start.py
usage: start.py [-h] [-c CONFIG]

The config file path must be specified

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file absolute path
```

`-c` è un argomento obbligatorio. Indica quale file di configurazione usare. Il file di conifgurazione deve essere un `.toml` scritto come `example.config.toml` presente in questo repo.