import pyeapi
import json

def get_external_lsa_info(target_node):
    
    command = "show ipv6 ospf database as detail"

    output = target_node.enable(command)

    lsa_5_list = output[0]['result']['vrfs']['default']['instList']['10']['ospf3AsLsas']

    return lsa_5_list