import pyeapi
import sys

from interfaces.get_interfaces import *
from neighbors.get_neighbors import *
from lsa_1.router_lsa import *
from lsa_2.network_lsa import *
from lsa_3.summary_lsa import *
from protocol.protocol_info import *
from utilities import *

if len(sys.argv) < 2:
    sys.stderr.write('ERRORE: nodo target non fornito in input\n')
    sys.exit(1)

input_node = sys.argv[1]

print('**** OSPF Management APP ****\n')

target_node = pyeapi.connect_to(input_node)

interfaces = get_interfaces(target_node)
protocol_info = get_protocol_info(target_node)
neighbors = get_neighbors(target_node)

router = Node(protocol_info['Router ID'], interfaces)
for neighbor in neighbors:
    interface = neighbor['interface']
    router_id = neighbor['router_id']
    adjacency_state = neighbor['adjacency_state']
    designated_router = neighbor['designated_router']
    backup_designated_router = neighbor['backup_designated_router']
    router.add_neighbor(interface, router_id, adjacency_state, designated_router, backup_designated_router)
print(f"\n{router}\n")

main_networks = {}

# recupero informazioni LSA tipo 1

router_lsa_1 = get_router_lsa_info(target_node)

for area_data in router_lsa_1:
    area_id = area_data
    area_network = Network(area=area_id)

    for area_db_entry in router_lsa_1[area_data]['areaDatabase']:
        for lsa_entry in area_db_entry['areaLsas']:
            link_state_id = lsa_entry['linkStateId']
            advertising_router = lsa_entry['advertisingRouter']
            area_network.add_node(link_state_id)

            for router_link in lsa_entry['ospfRouterLsa']['routerLsaLinks']:
                link_id = router_link['linkId']
                link_type = router_link['linkType']
                metric = router_link['metric']

                existing_link = None
                for link in area_network.links:
                    if link.id == link_id and link.type == link_type:
                        existing_link = link
                        break

                if existing_link:
                    existing_link.add_endpoint(link_state_id)
                else:
                    new_link = Link(id=link_id, type=link_type, options=None, metric=metric, endpoints=[link_state_id])
                    area_network.add_link(new_link)

    main_networks[area_id] = area_network

# recupero LSA tipo 2

network_lsa_2 = get_network_lsa_info(target_node)
for area_data in network_lsa_2:
    for area_data, area_network in main_networks.items():
        for area_db_entry in network_lsa_2[area_data]['areaDatabase']:
            for lsa_entry in area_db_entry['areaLsas']:
                link_state_id = lsa_entry['linkStateId']
                network_mask = lsa_entry['ospfNetworkLsa']['networkMask']
                dr = lsa_entry['advertisingRouter']
                attached_routers = lsa_entry['ospfNetworkLsa']['attachedRouters']
                bdr = attached_routers[1] if len(attached_routers) > 1 else None

                for link in area_network.links:
                    if link.id == link_state_id:
                        link.set_mask(network_mask)
                        link.set_dr_bdr(dr, bdr)

# recupero LSA tipo 3

summary_lsa_3 = get_summary_lsa_info(target_node)
for area_data in summary_lsa_3:
    target_network = main_networks[area_data]

    if not target_network:
        continue
    
    for area_db_entry in summary_lsa_3[area_data]['areaDatabase']:
        for lsa_entry in area_db_entry['areaLsas']:
                ip = lsa_entry['linkStateId']
                mask = lsa_entry['ospfSummaryLsa']['networkMask']
                via = lsa_entry['advertisingRouter']
                metric = lsa_entry['ospfSummaryLsa']['metric']

                route = Route(ip, mask, via, metric)

                target_network.add_inter_area_route(route)


for area_id, area_network in main_networks.items():
    print(f"\n{area_network}")
