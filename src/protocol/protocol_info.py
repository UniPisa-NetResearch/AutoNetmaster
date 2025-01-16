import pyeapi
import json

def get_protocol_info(target_node):
    
    command = "show ip ospf protocol"

    info = target_node.enable(command)

    return info
