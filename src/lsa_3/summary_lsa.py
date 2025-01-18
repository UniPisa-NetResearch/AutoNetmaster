import pyeapi
import json

def get_summary_lsa_info(target_node):
    
    command = "show ip ospf database summary"

    output = target_node.enable(command)

    lsa_3_list = output[0]['result']['vrfs']['default']['instList']['1']['areas']

    return lsa_3_list