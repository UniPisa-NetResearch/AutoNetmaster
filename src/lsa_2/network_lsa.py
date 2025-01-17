import pyeapi
import json

def get_network_lsa_info(target_node):
    """
    funzione che restituisce l'elenco degli lsa-2
    """
    output = target_node.enable('show ip ospf database network')

    lsa_2_list =  output[0]['result']['vrfs']['default']['instList']['1']['areas']

    return lsa_2_list