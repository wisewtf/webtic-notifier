# Webtic Notifier

**Versione:** `UNDEF`

WIP

## Uso

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
