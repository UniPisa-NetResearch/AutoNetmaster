import pyeapi
import json

def get_router_lsa_info(target_node, adv_router=None):
    """
    Funzione che restituisce l'elenco degli LSA-1.
    Se viene fornito un `adv_router`, la funzione restituira gli LSA-1 per quel router.
    """

    if adv_router is not None:
        command = f"show ip ospf database router {adv_router}"
    else:
        command = "show ip ospf database router"

    lsa_1_list = target_node.enable(command)

    return lsa_1_list
