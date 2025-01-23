import pyeapi
import json

def get_route_table(target_node):
    result = target_node.enable('show ip route')
    table_entries = []
    routes = result[0]['result']['vrfs']['default']['routes']

    for route, details in routes.items():
        entry_info = {
            'ip': route.split('/')[0],
            'masklen': route.split('/')[-1],
            'via': details.get('vias', [{}])[0].get('nexthopAddr', 'Directly Connected'),
            'interface': details.get('vias', [{}])[0].get('interface', 'Unknown'),
            'protocol': details['routeType']
        }
        table_entries.append(entry_info)

    return table_entries
