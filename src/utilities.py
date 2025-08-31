import json

class Network:
    def __init__(self):
        self.areas = set()
        self.external_routes = set()

    def add_area(self, area):
        self.areas.add(area)

    def add_external_network(self, route):
        self.external_routes.add(route)

    def find_target_area(self, area_data):
        target_area = None
        for area in self.areas:
            if area.area_id == area_data:
                target_area = area
                break
        return target_area

    def __str__(self):
        topology_str = "\nNETWORK TOPOLOGY:\n"

        for area in self.areas:
            topology_str += f"\n{str(area)}"
        
        topology_str += "\n\nexternal routes:"
        for route in self.external_routes:
            topology_str += f"\n  - ip: [{route.ip}]"
            topology_str += f"\n    - prefixlen: {route.masklen}"
            topology_str += f"\n    - via: {route.via}"
            topology_str += f"\n    - metric: {route.metric}"
            topology_str += f"\n    - metric_type: {route.metric_type}"

        topology_str += "\n"

        return topology_str
    
    def toJSON(self):
        return json.dumps({
            "areas": [area.toJSON() for area in self.areas],
            "external_routes": [route.toJSON() for route in self.external_routes]
        }, indent=None)

class Area:
    def __init__(self, area_id):
        self.area_id = area_id
        self.nodes = set()
        self.links = set()
        self.ospf_inter_area_routes = set()
        self.paths_to_asbrs = set()

    def add_node(self, node):
        self.nodes.add(node)

    def add_link(self, link):
        self.links.add(link)

    def add_inter_area_route(self, route):
        self.ospf_inter_area_routes.add(route)

    def add_path_to_asbr(self, path):
        self.paths_to_asbrs.add(path)

    def __str__(self):
        topology_str = f"area {self.area_id}:\n  nodes:"

        for node in self.nodes:
            topology_str += f"\n    - {node}"

        topology_str += "\n  links:"
        
        for link in self.links:
            topology_str += f"\n    - [ {link.id} ]:"
            topology_str += f"\n      - endpoints: {link.endpoints}"
            topology_str += f"\n      - type: {link.type}"
            topology_str += f"\n      - prefix: {getattr(link, 'prefix', None)}"
            topology_str += f"\n      - dr: {getattr(link, 'dr', None)}"
            topology_str += f"\n      - bdr: {getattr(link, 'bdr', None)}"
            topology_str += f"\n      - metric: {link.metric}"

        topology_str += "\n  ospf inter-area routes:"
        
        for route in self.ospf_inter_area_routes:
            topology_str += f"\n    - ip: [{route.ip}]"
            topology_str += f"\n      - masklen: {route.masklen}"
            topology_str += f"\n      - via: {route.via}"
            topology_str += f"\n      - metric: {route.metric}"

        topology_str += "\n  paths to ASBRs:"
        
        for path in self.paths_to_asbrs:
            topology_str += f"\n    - ASBR: {path.asbr}"
            topology_str += f"\n      - via: {path.via}"
            topology_str += f"\n      - metric: {path.metric}"

        topology_str += "\n"

        return topology_str
    
    def toJSON(self):
        return {
            "area_id": self.area_id,
            "nodes": list(self.nodes), 
            "links": [link.toJSON() for link in self.links],
            "ospf_inter_area_routes": [route.toJSON() for route in self.ospf_inter_area_routes],
            "paths_to_asbrs": [path.toJSON() for path in self.paths_to_asbrs]
        }

class Node:
    def __init__(self, router_id, hostname, interface_list=None, 
                 neighbor_list=None, route_table=None):
        self.hostname = hostname
        self.router_id = router_id
        self.interfaces = interface_list if interface_list else []
        self.neighbors = neighbor_list if neighbor_list else []
        self.route_table = route_table if route_table else []

    # devo considerare che per un'interfaccia potrebbero essere più
    # indirizzi configurati con differente scope

    # quindi invece di considerare ip e maschera considero una lista
    # di dict del tipo ip, maschera
    def add_interface(self, id, add, interface_status, line_protocol_status):
        self.interfaces.append({
            "id": id,
            "addresses":add,
            "interface_status": interface_status,
            "line_protocol_status": line_protocol_status
        })

    # qua non posso considerare l'indirizzo del vicino
    # a patto che non si consideri linkLSA per poter vedere
    # indirizzo link-local
    def add_neighbor(self, interface_id, neighbor_router_id, neighbor_ip_addr, 
                     adjacency_state, designated_router, backup_designated_router):
        self.neighbors.append({
            "interface_id": interface_id,
            "router_id": neighbor_router_id,
            #"neighbor_ip_addr": neighbor_ip_addr,
            "adjacency_state": adjacency_state,
            "designated_router": designated_router,
            "backup_designated_router": backup_designated_router
        })

    # la rotta potrebbe avere più vie, quindi via potrebbe essere una lista
    def add_route(self, ip, masklen, vias, protocol):
            self.route_table.append({
                "ip": ip,
                "prefixLen": masklen,
                "vias":vias,
                "protocol": protocol
            })

    def __str__(self):
        interface_str=""
        #creare manualmente interface_str, perché devi tenere conto che un'interfaccia ha più indirizzi
        for iface in self.interfaces:
            interface_str += f"       ID: {iface['id']},"
            for ind_int in iface['addresses']:
                interface_str+=f"\n         address:{ind_int['address']}/{ind_int['prefix_length']}, active:{ind_int['active']}, type:{ind_int['type']}"
            interface_str+=f"\n         Interface Status: {iface['interface_status']}, Line Protocol Status: {iface['line_protocol_status']}\n"
            
        #Neighbor ip address: {n['neighbor_ip_addr']},
        neighbors_str = "\n        ".join(
            f"Interface: {n['interface']}, Router ID: {n['router_id']}, "
            f"Adj-State: {n['adjacency_state']}, DR: {n['designated_router']}, "
            f"BDR: {n['backup_designated_router']}" for n in self.neighbors
        )
        #le vie devono essere stampate per conto proprio, perché potrebbe esserci più di una via
        #route_table_str = "\n        ".join(
         #   f"Destination: {route['ip']}/{route['masklen']}"
          #  f", Via: {route['via']}, Interface: {route['interface']}, Protocol: {route['protocol']}"   
           # for route in self.route_table
            #)
        
        route_table_str=""
        for route in self.route_table:
            route_table_str+=f"Destination: {route['ip']}/{route['prefix_len']}\n          "
            for v in route['vias']:
                route_table_str+=f" Via: {v['via']}, Interface: {v['interface']}\n          "   
            route_table_str+=f" Protocol: {route['protocol']}\n        "

        return (
            f"Hostname: {self.hostname}\n"
            f"    Router ID: {self.router_id}\n"
            f"    Interfaces:\n{interface_str if self.interfaces else 'None'}"
            f"    Neighbors:\n        {neighbors_str if self.neighbors else 'None'}\n"
            f"    Route Table:\n        {route_table_str if self.route_table else 'None'}"
        )
    
    def toJSON(self):
        return json.dumps({
            "hostname": self.hostname,
            "router_id": self.router_id,
            "interfaces": [dict(interface) for interface in self.interfaces],
            "neighbors": [dict(neighbor) for neighbor in self.neighbors],
            "route_table": [dict(route) for route in self.route_table]
        }, indent=4)


class Link:
    def __init__(self, id, type, options, metric, prefix=None, 
                 endpoints=None, dr=None, bdr=None):
        self.id = id
        self.type = type
        self.options = options
        self.metric = metric
        self.endpoints = endpoints if endpoints else []
        self.prefix = prefix
        self.dr = dr 
        self.bdr = bdr
    
    def add_endpoint(self, endpoint):
        if not(endpoint in self.endpoints):
            self.endpoints.append(endpoint)

    # per indirizzo da mettere sopra a link nella fase 
    # di front end uso indirizzo configurato (fd00... oppure 2001:db8...)
    # non il link local
    # guardo il prefisso che vedo prendendo link lsa
    def set_prefix(self, prefix):
        self.prefix=prefix
        self.id = and_bit_to_bit(self.id, prefix)

    def set_dr_bdr(self, dr, bdr):
        self.dr = dr
        self.bdr = bdr

    def toJSON(self):
        return {
            "id": self.id,
            "type": self.type,
            "options": self.options,
            "metric": self.metric,
            "prefix": self.prefix,
            "endpoints": self.endpoints,
            "dr": self.dr,
            "bdr": self.bdr
        }

class Route:
    def __init__(self, ip, masklen, via, metric, metric_type=None):
        self.ip = ip
        self.masklen = masklen
        self.via = via
        self.metric = metric
        self.metric_type = metric_type

    def toJSON(self):
        return {
            "ip": self.ip,
            "prefix_len": self.masklen,
            "via": self.via,
            "metric": self.metric,
            "metric_type": self.metric_type
        }


class Path_To_ASBR:
    def __init__(self, asbr, via, metric):
        self.asbr = asbr
        self.via = via
        self.metric = metric
        
    def toJSON(self):
        return {
            "asbr": self.asbr,
            "via": self.via,
            "metric": self.metric
        }


# dato che esprimere la maschera per intero occuperebbe spazio, verrà specificato direttamente 
# il valore ( ad esempio /64 ) e poi verrà derivata la maschera
def and_bit_to_bit(address, prefix):
    mask_gen = generate_mask(prefix)
    cv_mask= [int(y,16) for y in mask_gen]
    double_semicolon_split=address.split('::')
    net_address=""
    if len(double_semicolon_split)==1:
        #caso in cui non vi è doppio semicolon
        # il contenuto dell'array coincide con l'indirizzo iniziale
        semicolon_split= [int(x,16) for x in address.split(':')]
        net_address_parts= [semicolon_split[i] & cv_mask[i] for i in range(8)]
        hex_address=[f"{ha:04x}" for ha in net_address_parts]
        net_address= ':'.join(map(str,hex_address))
    else:
        # dato che ho il doppio semicolon devo trovare il punto dove inserire
        # la sequenza di zeri
        given_address= []
        first_block=double_semicolon_split[0].split(':')
        second_block=double_semicolon_split[1].split(':')
        already_assigned= len(first_block)+len(second_block)
        for x in first_block:
            given_address.append(x)
        for i in range (8-already_assigned):
            given_address.append('0000')
        for x in second_block:
            given_address.append(x)

        cv_address=[ int(ha,16) for ha in given_address]
        net_address_parts=[cv_address[i] & cv_mask[i] for i in range(8)]
        hex_address=[f"{ha:04x}" for ha in net_address_parts]
        net_address= ':'.join(map(str,hex_address))
    return net_address

# metodo che genera la lista con i gruppi della maschera
def generate_mask(pre):
    mask= "1" * pre + "0" * (128-pre)
    mask_blocks = [mask[i:i+16] for i in range(0,128,16)]
    hex_mask= [f"{int(mb,2):04x}" for mb in mask_blocks]
    return hex_mask