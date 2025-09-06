import pyeapi
import json

def get_route_table(target_node):
    "Funzione che recupera la route table per routing ipv6 del nodo"

    result = target_node.enable('show ipv6 route')
    table_entries = []
    routes = result[0]['result']['routes']
    # considero che potrebbe esseerci più di una via 
    for route, details in routes.items():
        vias=[]
        for out_via in details.get('vias',[{}]):
            vias.append({
                'via': out_via.get('nexthopAddr','Directly connected'),
                'interface': out_via.get('interface','Unknown')
            })

        entry_info = {
            'ip': route.split('/')[0],
            'prefix_len': route.split('/')[-1],
            'vias':vias,
            'protocol': details['routeType'],
            'metric': details['metric']
        }
        table_entries.append(entry_info)

    return table_entries
