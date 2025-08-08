import pyeapi
import json

def get_route_table(target_node):
    result = target_node.enable('show ipv6 route')
    table_entries = []
    routes = result[0]['result']['routes']
    # NOTA: ATTENZIONE CHE BISOGNA GESTIRE IN FASE DI STAMPA IL CASO IN CUI
    # CI SIANO PIU' VIE
    for route, details in routes.items():
        vias=[]
        for out_via in details.get('vias',[{}]):
            vias.append({
                'via': out_via.get('nexthopAddr','Directly connected'),
                'interface': out_via.get('interface','Unknown')
            })

        entry_info = {
            'ip': route.split('/')[0],
            'masklen': route.split('/')[-1],
            'vias':vias,
            'protocol': details['routeType']
        }
        table_entries.append(entry_info)

    return table_entries
