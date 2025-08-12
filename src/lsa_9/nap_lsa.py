import pyeapi
import json
from areas.get_areas import get_areas
def get_nap_lsa_info(target_node):
    command= "show ipv6 ospf database area "

    node_areas= get_areas(target_node)
    lsa_type_9=[]
    # dato che non esiste un comando che da tutti gli lsa di tipo router senza specificare l'area
    # bisogna eseguire il comando per ogni area
    for a in node_areas:
        output=target_node.enable(command+a+" intra-area-prefix detail")
        area_entries= output[0]["result"]["vrfs"]["default"]["instList"]["10"]["ospf3AreaEntries"]
        if not(area_entries[str(a)]["ospf3AreaLsaList"]==[]):
            lsa_type_9.append(area_entries)
    return lsa_type_9