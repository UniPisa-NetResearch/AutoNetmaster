import pyeapi
import json

def get_external_lsa_info(target_node):
    
    command = "show ip ospf database external"

    output = target_node.enable(command)

    lsa_5_list = output[0]['result']['vrfs']['default']['instList']['1']['externalLsdb']

    return lsa_5_list