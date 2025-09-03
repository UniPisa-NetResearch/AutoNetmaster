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
from lsa_7.nssa_lsa import *
from lsa_8.link_lsa import *
from lsa_9.nap_lsa import *
from utilities import *
from gui.gui import app

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if len(sys.argv) < 2:
    sys.stderr.write('ERRORE: nodo target non fornito in input\n')
    sys.exit(1)

input_node = sys.argv[1]
print('**** OSPFv3 Management APP ****\n')

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
link_lsa_8 = get_link_lsa_info(target_node)
nap_lsa_9= get_nap_lsa_info(target_node)

for area_data in router_lsa_1:
    new_area = Area(area_data)
    for lsa_entry in router_lsa_1[area_data]['ospf3AreaLsaList']:
        link_state_id = lsa_entry['linkStateId']
        advertising_router = lsa_entry['advertisingRouter']
        # devo cambiare con Advertising router perché il campo
        # link state id non da più info sul router ID in OSPFv3
        new_area.add_node(advertising_router)
        
        for router_link in lsa_entry['ospf3RouterLsa']['routerLsaLinks']:
            # questo controllo viene fatto per evitare
            # che il router interpreti la raggiungibilità verso
            # se stesso come un ulteriore link
            # if router_link['neighborRouterId'] == advertising_router:
            #     continue
            interface_id = router_link['interfaceId']
            interface_type = router_link['interfaceType']
            neighbor_router_id= router_link['neighborRouterId']
            neighbor_interface_id=router_link['neighborInterfaceId']
            metric = router_link['metric']
            
            
            link_id=""
            prefix_l=0
            # per trovare il link id devo andare a trovare lsa di tipo 8 che contiene questa informazione
            # devo trovare coppia di lsa 8 con questi router id e interface id
            for ll in link_lsa_8:
                for lsa8_entry in link_lsa_8[ll]['ospf3InterfaceLsaList']:
                    if len(lsa8_entry['ospf3LinkLsa']['prefixList']) == 0:
                        continue
                    if lsa8_entry['linkStateId'] == interface_id and lsa8_entry['advertisingRouter'] == advertising_router:
                        # riguarda il router advertising
                        prefix_l=lsa8_entry['ospf3LinkLsa']['prefixList'][0]['prefixLength']
                        link_id=lsa8_entry['ospf3LinkLsa']['prefixList'][0]['prefix']
                        break
                    elif lsa8_entry['linkStateId'] == neighbor_interface_id and lsa8_entry['advertisingRouter'] == neighbor_router_id:
                        # ho informazioni sul vicino
                        prefix_l=lsa8_entry['ospf3LinkLsa']['prefixList'][0]['prefixLength']
                        link_id=lsa8_entry['ospf3LinkLsa']['prefixList'][0]['prefix']
                        break

            if link_id=="" :
                continue


            existing_link = None
            for link in new_area.links:
                if link.id == link_id and link.type == interface_type:
                    existing_link = link
                    break
                # dato che in OSPFv3 non sono contenuti indirizzi negli header
                # invece di inserire linkStateID inserisco AdvertisingRouter
            
            if existing_link:
                existing_link.add_endpoint(advertising_router)
            else:
                ins_endpoints=[]
                if(advertising_router != neighbor_router_id):
                    ins_endpoints.append(neighbor_router_id)
                ins_endpoints.append(advertising_router)
                new_link = Link(id=link_id, type=interface_type, options=None, metric=metric, endpoints=ins_endpoints ,prefix=f"{link_id}/{prefix_l}")                
                new_area.add_link(new_link)

    network_topology.add_area(new_area)

#recupero le informazioni sulle stub network non adiacenti dagli nap lsa
for ll in nap_lsa_9:
    for lsa_9_entry in nap_lsa_9[ll]['ospf3AreaLsaList']:
        lsa_nap=lsa_9_entry['ospf3IntraAreaPrefixLsa']
        # if lsa_nap['referencedLsaType']!='routerLsa':
        #     continue
        #if advertising_router == lsa_nap['referencedAdvertisingRouter'] and link_state_id == lsa_nap['referencedLinkStateId'] and lsa_nap['numPrefixes']!=0:
        if lsa_nap['referencedLsaType']!='routerLsa':
            continue
        link_id=lsa_nap['prefixList'][0]['prefix'] 
        prefix_l=lsa_nap['prefixList'][0]['prefixLength']
        metric=lsa_nap['prefixList'][0]['metric']
        new_link = Link(id=link_id, type="stubNetwork", options=None, metric=metric, endpoints=[lsa_nap['referencedAdvertisingRouter']] ,prefix=f"{link_id}/{prefix_l}")
        network_topology.find_target_area(ll).add_link(new_link)

# recupero LSA tipo 2
network_lsa_2 = get_network_lsa_info(target_node)

for area_data in network_lsa_2:
    #for target_area in network_topology.areas:
        for lsa_entry in network_lsa_2[area_data]['ospf3AreaLsaList']:
            # for lsa_entry in area_db_entry['areaLsas']:
                link_state_id = lsa_entry['linkStateId']
                #indirizzi non più presenti negli lsa
                #network_mask = lsa_entry['ospfNetworkLsa']['networkMask']
                dr = lsa_entry['advertisingRouter']
                attached_routers = lsa_entry['ospf3NetworkLsa']['attachedRouters']
                #print(attached_routers)
                #cambiare la scelta del DBR, potrei rischiare di inserire il DR anche come BDR
                bdr = attached_routers[0] if len(attached_routers) > 1 else None
                adjacent=True
                # devo scorrere i nap lsa per poter ottenere informazione
                # su network lsa
                network_prefix=""
               #for lsa9_area in nap_lsa_9:
                for lsa9_entry in nap_lsa_9[area_data]['ospf3AreaLsaList']:
                        if lsa9_entry['ospf3IntraAreaPrefixLsa']['referencedLsaType']!='networkLsa':
                            continue
                        elif protocol_info['Router ID'] in attached_routers and dr == lsa9_entry['ospf3IntraAreaPrefixLsa']['referencedAdvertisingRouter'] and  link_state_id == lsa9_entry['ospf3IntraAreaPrefixLsa']['referencedLinkStateId']:
                             network_prefix= lsa9_entry['ospf3IntraAreaPrefixLsa']['prefixList'][0]['prefix']   
                        elif protocol_info['Router ID'] not in attached_routers:
                            #link non adiacente
                            #prendo il dr e trovo il nap annunciato
                            if dr == lsa9_entry['ospf3IntraAreaPrefixLsa']['referencedAdvertisingRouter'] and link_state_id == lsa9_entry['ospf3IntraAreaPrefixLsa']['referencedLinkStateId']:
                                #prendo prefix 
                                network_prefix= lsa9_entry['ospf3IntraAreaPrefixLsa']['prefixList'][0]['prefix']
                                link_id=lsa9_entry['ospf3IntraAreaPrefixLsa']['prefixList'][0]['prefix'] 
                                prefix_l=lsa9_entry['ospf3IntraAreaPrefixLsa']['prefixList'][0]['prefixLength']
                                metric=lsa9_entry['ospf3IntraAreaPrefixLsa']['prefixList'][0]['metric']
                                new_link = Link(id=link_id, type="transitNetwork", options=None, metric=metric, endpoints=attached_routers ,prefix=f"{link_id}/{prefix_l}")
                                new_link.set_dr_bdr(dr=dr,bdr=bdr)
                                network_topology.find_target_area(area_data).add_link(new_link)
                                adjacent=False


                        if adjacent:                    
                            for link in network_topology.find_target_area(area_data=area_data).links:
                                # qua devo fare il confronto con prefix
                                if link.id == network_prefix:
                                    link.set_dr_bdr(dr, bdr)

# recupero LSA tipo 3

iar_lsa_3 = get_iap_lsa_info(target_node)

for area_data in iar_lsa_3:
    target_area = network_topology.find_target_area(area_data)
    if not target_area:
        continue
    
    for lsa_entry in iar_lsa_3[area_data]['ospf3AreaLsaList']:
            ip = lsa_entry['ospf3InterAreaPrefixLsa']['prefix']['prefix']
            mask = lsa_entry['ospf3InterAreaPrefixLsa']['prefix']['prefixLength'] 
            via = lsa_entry['advertisingRouter']
            metric = lsa_entry['ospf3InterAreaPrefixLsa']['metric'] 

            existing=target_area.search_route(ip,mask)
            if existing==None:
                route = Route(ip, mask, via, metric)

                target_area.add_inter_area_route(route)
            else:
                existing.add_via(via)



# recupero LSA tipo 4

iar_lsa_4 = get_iar_lsa_info(target_node)

for area_data in iar_lsa_4:
    target_area = network_topology.find_target_area(area_data)
    if not target_area:
        continue

    for lsa_entry in iar_lsa_4[area_data]['ospf3AreaLsaList']:
                asbr = lsa_entry['ospf3InterAreaRouterLsa']['destinationRouterId']
                via = lsa_entry['advertisingRouter']
                metric = lsa_entry['ospf3InterAreaRouterLsa']['metric']

                path = Path_To_ASBR(asbr, via, metric)
                
                target_area.add_path_to_asbr(path)

# recupero LSA di tipo 5

external_lsa_5 = get_external_lsa_info(target_node)

for lsa in external_lsa_5:
        ip = lsa['ospf3ExternalLsa']['prefix']['prefix']
        prefix_len = lsa['ospf3ExternalLsa']['prefix']['prefixLength']
        via = lsa['advertisingRouter']
        metric = lsa['ospf3ExternalLsa']['metric']
        metric_type = lsa['ospf3ExternalLsa']['metricType']

        route = Route(ip, prefix_len, via, metric, metric_type)
        
        network_topology.add_external_network(route)


# discover other nodes
def discover_router(ip_addr):
    """Connette al router dato l'IP e ne estrae le informazioni."""
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
    neighbors_dict = {n["router_id"]: n for n in current_router.neighbors}

    for nghb in current_router.neighbors:
        nghb_id = nghb['router_id']
        #nghb_ip = nghb['neighbor_ip_addr']

        if nghb_id not in network_routers: # and nghb_id != router.router_id:
            new_router, new_neighbors = discover_router(nghb_id)
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

