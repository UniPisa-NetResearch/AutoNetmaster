# Parto da un'immagine python che contiene 
# librerie installate anche per l'uso di firefox
FROM python:3.12.3-slim 
# faccio update e installo tutte le dipendenze
# necessarie per poter utilizzare firefox 
RUN apt-get update && apt-get install -y firefox-esr curl wget gnupg  && rm -rf /var/lib/apt/lists/* 
# Installo pyeapi e Flask 
RUN pip install --no-cache-dir flask pyeapi 

# elementi per configurazione della scheda di rete
RUN apt-get update && apt-get install -y iproute2 iputils-ping net-tools && rm -rf /var/lib/apt/lists/*


# Espone la porta per Flask per poter accedere
# al template
EXPOSE 5000 
