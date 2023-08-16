# Webtic Notifier

**Versione:** `Milestone 1.7`

## Introduzione

`Webtic Notifier` è un piccolo esperimento in Python che esegue una logica di notifica ad ogni nuovo `evento` (inteso come programmazione cinematografica) da ognuno dei cinema presenti sotto l'ombrello del sistema di ticketing `Webtic`.

"Esperimento" perché sono un sistemista e non un programmatore, quindi essendo ancora alle prime armi sto imparando cosa va fatto, come va fatto e se va fatto.

## Funzionalità

Al primo lancio, lo script salva in un database MongoDB tutti gli eventi dei cinema configurati nel file di configurazione (`config.toml`) e per tutti i lanci successivi si preoccuperà solo di prendere nota degli eventi (dei `documents` sotto MongoDB) che sono stati **aggiunti** al database (`collection` sotto MongoDB).

Se un **nuovo** documento dovesse venir aggiunto, allora lo script si preoccuperà - tramite la libreria [Apprise](https://github.com/caronc/apprise) - di compilare un messaggio Telegram che verrà poi inviato nei canali definiti nel file di configurazione.

Per far si che lo script venga eseguito automaticamente, usando la libreria `schedule`, rimarrà attivo ma dormiente. Questo fino a quando il lasso di tempo configurato (che ha un minimo di 15 minuti) non scade. Di conseguenza fino a quando non si rompe o lo si interrompe, lo script dovrebbe rimanere attivo ininterrottamente.

## Roadmap

- [ ] Bot interattivo per Telegram
- [ ] Configurazione cinema per nome e non per ID
- [ ] Inserimento primo orario nel messaggio di telegram
- [ ] Implementazione della multinotifica con tutto il parco API di Apprise

## Installazione e uso

Questo capitolo è un work in progress. Sto ancora decidendo come meglio gestire il QoL di un utente medio.

Attualmente il software è as-is. E' presente un'[immagine docker](https://hub.docker.com/r/megawise/webtic-notifier) buildata da me che funziona con l'ultima RC di Python.

Chi sa come farlo partire è libero di utilizzarlo.

Appena decido che strada prendere spiegherò tutto in questa sezione.
