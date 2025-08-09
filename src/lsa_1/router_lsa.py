import pyeapi
import json
from areas.get_areas import get_areas

def get_router_lsa_info(target_node):
    
    node_areas= get_areas(target_node)

    command = "show ospfv3 database area "
    lsa_1_list=[]

    for a in node_areas:
        output = target_node.enable(command+str(a))
        
        lsa_area_target= output[0]['result']['vrfs']['default']['addressFamily']['ipv6']['ospf3AreaEntries'][str(a)]['ospf3AreaLsaList']

        for lsa in  lsa_area_target:
            if lsa['lsaType'] == "routerLsa":
                lsa_1_list.append(lsa)

    return lsa_1_list
