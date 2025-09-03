import pyeapi
import json

def get_interfaces(target_node):
    result = target_node.enable('show ipv6 interface brief')

    interfaces = []
    interface_list = result[0]['result']['interfaces']
    # ogni interfaccia dispone di un link-local address
    # e di uno o più indirizzi configurati ( ULA, GUA )

    for interface_name, interface_details in interface_list.items():
        addresses=[]
        # inserisco link-local
        addresses.append({
            'address':interface_details["linkLocal"]["address"],
            'prefix_length': interface_details["linkLocal"]["subnet"].split('/')[-1],
            'type':'link local'
        })
        # inserisco gli altri indirizzi configurati
        for add in interface_details["addresses"]:
            addresses.append({
                'address':add["address"],
                'prefix_length': add["subnet"].split('/')[-1],
                'type':'config'
            })

        interface_info = {
            'id': interface_name,
            'addresses': addresses,
            'interface_status': interface_details['interfaceStatus'],
            'line_protocol_status': interface_details['lineProtocolStatus']
        }

        interfaces.append(interface_info)
    
    return interfaces
