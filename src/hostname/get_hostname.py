import pyeapi

def get_hostname(target_node):
    "Funzione che restituisce hostname del nodo"
    return (target_node.enable('show hostname'))[0]['result']['hostname']