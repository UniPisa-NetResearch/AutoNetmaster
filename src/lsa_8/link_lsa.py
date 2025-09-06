import pyeapi
import json
def get_link_lsa_info(target_node):
    "Funzione che recupera gli lsa di tipo link dal database OSPFv3 del nodo"

    command= "show ipv6 ospf database link detail "
    
    output= target_node.enable(command)

    lsa_type_8= output[0]["result"]["vrfs"]["default"]["instList"]["10"]["ospf3InterfaceEntries"]

    return lsa_type_8