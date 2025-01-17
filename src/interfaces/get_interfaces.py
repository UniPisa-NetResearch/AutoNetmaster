import pyeapi
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utilities import *

def get_interfaces(target_node):
    result = target_node.enable('show ip interface brief')

    interfaces = []
    for interface_info in result[0]['result']['interfaces'].values():
        interfaces.append(Interface(
            interface_info['name'],
            interface_info['interfaceAddress']['ipAddr']['address'],
            interface_info['interfaceAddress']['ipAddr']['maskLen'],
            interface_info.get('lineProtocolStatus', 'unknown'),
            interface_info.get('interfaceStatus', 'unknown')
        ))
    
    return interfaces
