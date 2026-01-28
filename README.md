# Webtic Notifier

**Versione:** `1.1`

## Uso

1. Clonare questo repo.
2. Installare `python3`
3. Installare le librerie con `pip3 install -r requirements.txt`
4. Installare MongoDB (qualsiasi versione va bene)

Lanciare lo script con:

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

Usare cron o systemd-timers per lanciare `start.py`

### Configurazione

Il repo contiene un file di esempio in formato `.toml`:

```toml
[telegram]
token = 'BOT_TOKEN'
chat_id = 'CHAT_ID'

[database]
host = 'mongodb://user:pass@mongodbhostname:27017/?authMechanism=DEFAULT'

[webtic]
cinema_ids = [ 1234, 5678 ]
```

Vi serviranno:

1. Il token del vostro bot Telegram. (Generabile da BotFather)
2. Il chat ID della vostra group chat in cui è stato inserito il bot. (Trovabile usando un qualsiasi bot tipo getchatid, oppure facendo query a telegram)
3. La stringa di connessione al vostro DB MongoDB.
4. Gli ID dei cinema, trovabili cercando il vostro cinema su Webtic e usando il valore di `?localid=1234` = `1234`

### Systemd units

Consiglio di lanciare lo script periodicamente usando `systemd`.

Ecco un esempio di servizio:

```systemd
# /etc/systemd/system/webtic-notifier.service
[Unit]
Description=Webtic Notifier Service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/webtic-notifier/start.py -c /opt/webtic-notifier/config.toml
WorkingDirectory=/opt/webtic-notifier
Restart=on-failure
User=wise
```

Da modificare sarebbe il valore di `ExecStart` e `WorkingDirectory` per riflettere dove clonerete il repository. E infine il valore di `User`, con il vostro utente non root.

La unit lavora in tandem con il timer:

```systemd
# /etc/systemd/system/webtic-notifier.timer
[Unit]
Description=Run Webtic Notifier every 15 minutes

[Timer]
OnCalendar=*:0/15
Persistent=true

[Install]
WantedBy=timers.target
```

Questo timer esegue lo script ogni 15 minuti. Il valore di `OnCalendar` è ovviamente modificabile.

Una volta create le due unit, ricaricate il database di `systemd` con `systemctl daemon-reload` e abilitatele (eseguendole immediatamente con `--now`) entrambe lanciando `systemctl enable --now webtic-notifier.service webtic-notifier.timer`
