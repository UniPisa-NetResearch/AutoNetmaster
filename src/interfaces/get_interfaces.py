import pyeapi
import json

def get_interfaces(target_node):
    result = target_node.enable('show ip interface brief')

    interfaces = []
    interface_list = result[0]['result']['interfaces']

    for interface_name, interface_details in interface_list.items():
        interface_info = {
            'name': interface_name,
            'ip': interface_details['interfaceAddress']['ipAddr']['address'],
            'masklen': interface_details['interfaceAddress']['ipAddr']['maskLen'],
            'interface_status': interface_details['interfaceStatus'],
            'line_protocol_status': interface_details['lineProtocolStatus']
        }

        interfaces.append(interface_info)
    
    return interfaces
