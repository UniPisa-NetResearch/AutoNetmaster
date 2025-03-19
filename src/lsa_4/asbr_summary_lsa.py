import pyeapi
import json

def get_asbr_summary_lsa_info(target_node):
    
    command = "show ip ospf database asbr-summary"

    output = target_node.enable(command)

    lsa_4_list = output[0]['result']['vrfs']['default']['instList']['1']['areas']

    return lsa_4_list