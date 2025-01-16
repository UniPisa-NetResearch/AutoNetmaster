import pyeapi
import json

def get_network_lsa_info(target_node):
    """
    funzione che restituisce l'elenco degli lsa-2
    """
    lsa_2 = target_node.enable('show ip ospf database router')
    return lsa_2