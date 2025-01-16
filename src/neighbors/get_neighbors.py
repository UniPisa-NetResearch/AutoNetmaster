import pyeapi
import json

def get_neighbors(target_node):
    """
    funzione che restituisce l'elenco dei vicini del nodo target
    """
    neighbors = target_node.enable('show ip ospf neighbors')
    return neighbors