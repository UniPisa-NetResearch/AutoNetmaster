import pyeapi
import sys
import time
import webbrowser
from threading import Thread
from queue import Queue
from urllib.parse import quote

from hostname.get_hostname import *
from protocol.protocol_info import *
from interfaces.get_interfaces import *
from neighbors.get_neighbors import *
from route_table.get_route_table import *
from lsa_1.router_lsa import *
from lsa_2.network_lsa import *
from lsa_3.summary_lsa import *
from lsa_4.asbr_summary_lsa import *
from lsa_5.external_lsa import *
from utilities import *
from gui.gui import app

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if len(sys.argv) < 2:
    sys.stderr.write('ERRORE: nodo target non fornito in input\n')
    sys.exit(1)

input_node = sys.argv[1]

print('**** OSPF Management APP ****\n')

target_node = pyeapi.client.connect(
    transport='https',
    host=input_node,
    username='admin',
    password='admin',
    return_node=True
)

hostname = get_hostname(target_node)

interfaces = get_interfaces(target_node)

route_table = get_route_table(target_node)

protocol_info = get_protocol_info(target_node)

neighbors = get_neighbors(target_node)

router = Node(protocol_info['Router ID'], hostname, interfaces, neighbors, route_table)

print(f"\n{router}\n")

network_topology = Network()

# recupero informazioni LSA tipo 1

router_lsa_1 = get_router_lsa_info(target_node)

for area_data in router_lsa_1:
    new_area = Area(area_data)

    for area_db_entry in router_lsa_1[area_data]['areaDatabase']:
        for lsa_entry in area_db_entry['areaLsas']:
            link_state_id = lsa_entry['linkStateId']
            advertising_router = lsa_entry['advertisingRouter']
            new_area.add_node(link_state_id)

            for router_link in lsa_entry['ospfRouterLsa']['routerLsaLinks']:
                link_id = router_link['linkId']
                link_type = router_link['linkType']
                metric = router_link['metric']

                existing_link = None
                for link in new_area.links:
                    if link.id == link_id and link.type == link_type:
                        existing_link = link
                        break

                if existing_link:
                    existing_link.add_endpoint(link_state_id)
                else:
                    new_link = Link(id=link_id, type=link_type, options=None, metric=metric, endpoints=[link_state_id])

                    if(link_type == "stubNetwork"):
                        new_link.set_mask(router_link['linkData'])
                    
                    new_area.add_link(new_link)

    network_topology.add_area(new_area)

# recupero LSA tipo 2
network_lsa_2 = get_network_lsa_info(target_node)

for area_data in network_lsa_2:
    for target_area in network_topology.areas:
        for area_db_entry in network_lsa_2[area_data]['areaDatabase']:
            for lsa_entry in area_db_entry['areaLsas']:
                link_state_id = lsa_entry['linkStateId']
                network_mask = lsa_entry['ospfNetworkLsa']['networkMask']
                dr = lsa_entry['advertisingRouter']
                attached_routers = lsa_entry['ospfNetworkLsa']['attachedRouters']
                bdr = attached_routers[1] if len(attached_routers) > 1 else None

                for link in target_area.links:
                    if link.id == link_state_id:
                        link.set_mask(network_mask)
                        link.set_dr_bdr(dr, bdr)

# recupero LSA tipo 3

summary_lsa_3 = get_summary_lsa_info(target_node)

for area_data in summary_lsa_3:
    target_area = network_topology.find_target_area(area_data)
    if not target_area:
        continue
    
    for area_db_entry in summary_lsa_3[area_data]['areaDatabase']:
        for lsa_entry in area_db_entry['areaLsas']:
                ip = lsa_entry['linkStateId']
                mask = lsa_entry['ospfSummaryLsa']['networkMask']
                via = lsa_entry['advertisingRouter']
                metric = lsa_entry['ospfSummaryLsa']['metric']

                route = Route(ip, mask, via, metric)

                target_area.add_inter_area_route(route)

# recupero LSA tipo 4

asbr_summary_lsa_4 = get_asbr_summary_lsa_info(target_node)

for area_data in asbr_summary_lsa_4:
    target_area = network_topology.find_target_area(area_data)

    if not target_area:
        continue

    for area_db_entry in asbr_summary_lsa_4[area_data]['areaDatabase']:
        for lsa_entry in area_db_entry['areaLsas']:
                asbr = lsa_entry['linkStateId']
                via = lsa_entry['advertisingRouter']
                metric = lsa_entry['ospfSummaryLsa']['metric']

                path = Path_To_ASBR(asbr, via, metric)

                target_area.add_path_to_asbr(path)

# recupero LSA di tipo 5

external_lsa_5 = get_external_lsa_info(target_node)

for external_data in external_lsa_5:
    for lsa in external_data['externalLsas']: 
        ip = lsa['linkStateId']
        mask = lsa['ospfExternalLsa']['networkMask']
        via = lsa['advertisingRouter']
        metric = lsa['ospfExternalLsa']['metric']
        metric_type = lsa['ospfExternalLsa']['metricType']

        route = Route(ip, mask, via, metric, metric_type)
        
        network_topology.add_external_network(route)

# discover other nodes

def discover_router(ip_addr):
    """Connette al router dato l'IP e ne estrae le informazioni."""
    print(ip_addr)
    node = pyeapi.client.connect(
        transport='https',
        host=ip_addr,
        username='admin',
        password='admin',
        return_node=True
    )

    hostname = (node.enable('show hostname'))[0]['result']['hostname']
    interfaces = get_interfaces(node)
    route_table = get_route_table(node)
    protocol_info = get_protocol_info(node)
    neighbors = get_neighbors(node)

    router_id = protocol_info['Router ID']

    return Node(router_id, hostname, interfaces, neighbors, route_table), neighbors

network_routers = {router.router_id: router}  # Mappa router_id -> Node
discovered_ips = {router.router_id: router.neighbors}  # Mappa router_id -> IP dei vicini
queue = Queue()  
queue.put(router) 

while not queue.empty():
    current_router = queue.get()
    #neighbors_dict = {n["router_id"]: n for n in current_router.neighbors}

    for nghb in current_router.neighbors:
        nghb_id = nghb['router_id']
        nghb_ip = nghb['neighbor_ip_addr']

        if nghb_id not in network_routers: # and nghb_id != router.router_id:
            new_router, new_neighbors = discover_router(nghb_ip)
            network_routers[nghb_id] = new_router
            queue.put(new_router)

while True:
        cmd = input("> ").strip() 
        
        if cmd.startswith("id "):
            id = cmd[3:] 
            matching_router = network_routers.get(id)
            if(matching_router != None):
                print(matching_router)
                print('\n')
            else:
                print("Non esistono router con l'id selezionato")

        elif cmd == "nodes":
            print('NODES:\n')
            for router in network_routers.values():
                print(router)
                print('\n')

        elif cmd == "topology":
            print(network_topology)

        elif cmd == "display":
            network_routers_json = {router_id: json.loads(router.toJSON()) for router_id, router in network_routers.items()}
            data = network_topology.toJSON()

            app.config['NETWORK_ROUTERS_JSON'] = network_routers_json
            app.config['DATA'] = data
            app.config['TARGET'] = input_node

            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()

        elif cmd == "help":
            print("""
        Comandi disponibili:
            id [ospf_id]      - Ottieni informazioni sul nodo di rete l'ID ospf specificato.
            nodes             - Mostra le caratteristiche dei nodi della rete
            topology          - Stampa la topologia della rete.
            display           - Avvia un'interfaccia web per la visualizzazione grafica della topologia.
            exit              - Esci dal programma.
                """) 

        elif cmd == "exit":
            sys.exit(0)

        else:
            print("Comando non riconosciuto. Digita 'help' per assistenza.")

