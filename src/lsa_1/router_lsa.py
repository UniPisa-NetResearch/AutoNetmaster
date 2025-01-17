import pyeapi
import json

def get_router_lsa_info(target_node):
    
    command = "show ip ospf database router"

    output = target_node.enable(command)

    lsa_1_list = output[0]['result']['vrfs']['default']['instList']['1']['areas']

    return lsa_1_list
