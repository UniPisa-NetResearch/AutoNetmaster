# OSPFv3 management software application

L'obiettivo dell'applicazione e' ricostruire la topologia di una rete partendo da uno specifico nodo, utilizzando in particolare, le informazioni del database ospfv3.

----

## Installazione

Per poter usare il programma si dovranno installare diverse componenti sull'host che elencherò qua sotto:

### WSL
Nel caso in cui si stia usando un host con sistema operativo differente da uno linux-based, sarà necessario installare WSL ( Windows Subsystem Linux ) all'interno del quale potremo poi eseguire tutte le operazioni necessarie. Per installarlo si troveranno maggiori dettagli sul sito [ContainerLab](www.containerlab.dev)

### Container lab

[ContainerLab](www.containerlab.dev) è un software che ha il ruolo di emulare una topologia di rete attraverso l'uso di container le cui immagini vengono specificate all'interno di un **file yaml** ( per esempio si guardino i casi di test ) dove verranno indicati quindi i nodi della nostra rete (inclusi gli endpoint) e i link che collegano i suddetti. Per poter emulare la nostra topologia di rete si potrà eseguire uno script:

_curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"_


**Fonte sezione [QuickStart](https://containerlab.dev/quickstart/) di ContainerLab**

Una volta installato basterà un semplice IDE oppure un editor per poter scrivere i file yaml, per la sintassi si rimanda nuovamente al sito di ContainerLab nella sezione [QuickStart](https://containerlab.dev/quickstart/)

Per emulare la topologia dovrà essere eseguito il comando:

_sudo clab -t [percorso file topologia] deploy_

Invece per terminare l'emulazione si dovrà eseguire:

_sudo clab -t [percorso file topologia] destroy_

E' necessario creare manualmente un bridge, poiche' CONTAINERlab non supporta nativamente gli switch e l'utilizzo di nodi Arista per la loro emulazione sarebbe prestazionalmente costoso, è stato, quindi, predisposto uno script activate_bridge.sh da eseguire con privilegi di su (supervisor user) per creare i birdge i cui nomi sono passati in una stringa separati da spazio

Esempio: 
Supponendo di voler attivare gli switch SW1 e SW2 si dovrà eseguire il comando :
sudo ./activate_bridge.sh "SW1 SW2"

Per verificare la correttezza si può eseguire il comando:
ip link show [nome_switch]

Le immagini usate per i nodi che offrono servizi a livello di rete sono container con immagini di **nodi ARISTA** (nei test e' utilizzata immagine _ceos:4.34.0F_), nei quali si dovrà anche riscrivere l'attributo binds ed inserire il path dell'host che si vuole rendere visibile al container.

### Python e moduli
Il linguaggio di programmazione python viene utilizzato per sfruttare il modulo  [pyeapi](https://pyeapi.readthedocs.io/en/latest/) che permette di recuperare le informazioni dai nodi con immagine Arista e il modulo [Flask](https://flask.palletsprojects.com/en/stable/) per hostare un server che preparerà il template inserito sotto la cartella _gui/template/_.

I moduli python possono essere installati tramite **pip** eseguendo i comandi:

_pip install pyeapi_

_pip install Flask_

### Vis.js
[Vis.js](https://visjs.org/) è una libreria javascript che viene utilizzata per creare grafi ( composti da nodi e archi ) su una pagina web e nel nostro caso viene utilizzata per riprodurre graficamente la topologia di rete. 

----
## Utilizzo dell'applicazione
Una volta completati tutti questi step di installazione, si potrà eseguire scrivere la topologia di rete, emularla ed interagirci con l'applicazione. In particolare si dovrà eseguire lo script **ospf_mgmt.sh** passando come parametro il router ID del nodo da cui si vuole partire per ricostruire la topologia, ad esempio:

(Supponendo che il nostro router ID sia 10.0.0.1)

Si dovrà fare:  *./ospf_mgmt.sh 10.0.0.1*

si aprirà quindi un terminale in cui l'utente potrà vedere le informazioni sul nodo il cui router ID viene passato come parametro e potrà inserire uno tra i comandi disponibili per effettuare operazioni ( saranno visualizzabili digitando _help_)

Per accedere ai container si può utilizzare **docker**, in particolare per accedere alla bash del nostro container dovremo eseguire da terminale dell'host:

_docker exec -it [nome container] bash_

Così facendo si aprirà una CLI che opererà sul nostro container e dal quale si potrà eseguire la nostra applicazione. 

### interfaccia grafica
Se si esegue il comando _display_ (nel terminale dell'applicazione) potrà poi successivamente aprire il proprio browser ed accedere al localhost per accedere al template renderizzato da Flask ( digitando _127.0.0.1:5000_ nella barra dell'URL).

Verrà quindi rappresentata graficamente la topologia di rete che l'applicazione ha ricostruito utilizzando le informazioni dei nodi Arista.

Se l'utente clicca sui nodi verranno stampate le informazioni principali quali: hostname, router id, interfacce, vicini OSPFv3 e tabella di routing IPv6. Mentre se si clicca sui link si avranno le informazioni su tale link come: prefisso, tipo, endpoint ecc.

Se si clicca sul riquadro delle aree e in particolare sugli Area ID verranno mostrate le rotte inter-area e le rotte verso l'ASBR (Autonomous System Boundary Router) dell'AS.

Inoltre sopra il grafo verranno indicate tutte le rotte esterne che il router ASBR pubblicizza nell'AS.

## Note
La cartella test non e' essenziale ai fini del funzionamento dell'applicazione: si suggerisce di salvarla in un percorso differente, in modo tale da non passarla agli host con attributo binds.
