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
            topology_str += f"\n  - ip: {route.ip}"
            topology_str += f"\n    - mask: {route.mask}"
            topology_str += f"\n    - via: {route.via}"
            topology_str += f"\n    - metric: {route.metric}"
            topology_str += f"\n    - metric_type: {route.metric_type}"

        return topology_str
    
    def toJSON(self):
        return json.dumps({
            "areas": [area.toJSON() for area in self.areas],
            "external_routes": [route.toJSON() for route in self.external_routes]
        }, indent=4)

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
            topology_str += f"\n    - {link.id}:"
            topology_str += f"\n      - endpoints: {link.endpoints}"
            topology_str += f"\n      - type: {link.type}"
            topology_str += f"\n      - mask: {getattr(link, 'mask', None)}"
            topology_str += f"\n      - dr: {getattr(link, 'dr', None)}"
            topology_str += f"\n      - bdr: {getattr(link, 'bdr', None)}"
            topology_str += f"\n      - metric: {link.metric}"

        topology_str += "\n  ospf inter-area routes:"
        
        for route in self.ospf_inter_area_routes:
            topology_str += f"\n    - ip: {route.ip}"
            topology_str += f"\n      - mask: {route.mask}"
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
    def __init__(self, router_id, hostname, interface_list=None, neighbor_list=None, route_table=None):
        self.hostname = hostname
        self.router_id = router_id
        self.interfaces = interface_list if interface_list else []
        self.neighbors = neighbor_list if neighbor_list else []
        self.route_table = route_table if route_table else []

    def add_interface(self, id, ip, masklen, interface_status, line_protocol_status):
        self.interfaces.append({
            "id": id,
            "ip": ip,
            "masklen": masklen,
            "interface_status": interface_status,
            "line_protocol_status": line_protocol_status
        })

    def add_neighbor(self, interface_id, neighbor_router_id, adjacency_state, designated_router, backup_designated_router):
        self.neighbors.append({
            "interface_id": interface_id,
            "router_id": neighbor_router_id,
            "adjacency_state": adjacency_state,
            "designated_router": designated_router,
            "backup_designated_router": backup_designated_router
        })

    def add_route(self, ip, masklen, via, interface, protocol):
        self.route_table.append({
            "ip": ip,
            "masklen": masklen,
            "via": via,
            "interface": interface,
            "protocol": protocol
        })

    def __str__(self):
        interface_str = "\n        ".join(
            f"ID: {iface['name']}, IP: {iface['ip']}/{iface['masklen']}, Interface Status: {iface['interface_status']}, Line Protocol Status: {iface['line_protocol_status']}"
            for iface in self.interfaces
        )
        neighbors_str = "\n        ".join(
            f"Interface ID: {n['interface']}, Router ID: {n['router_id']}, "
            f"Adjacency State: {n['adjacency_state']}, Designated Router: {n['designated_router']}, "
            f"Backup Designated Router: {n['backup_designated_router']}" for n in self.neighbors
        )
        route_table_str = "\n        ".join(
            f"Destination: {route['ip']}/{route['masklen']}, Via: {route['via']}, "
            f"Interface: {route['interface']}, Protocol: {route['protocol']}"
            for route in self.route_table
        )
        return (
            f"Hostname: {self.hostname}\n"
            f"Router ID: {self.router_id}\n"
            f"    Interfaces:\n        {interface_str if self.interfaces else 'None'}\n"
            f"    Neighbors:\n        {neighbors_str if self.neighbors else 'None'}\n"
            f"    Route Table:\n        {route_table_str if self.route_table else 'None'}"
        )
    
    def toJSON(self):
        return {
            "hostname": self.hostname,
            "router_id": self.router_id,
            "interfaces": self.interfaces,
            "neighbors": self.neighbors,
            "route_table": self.route_table
        }


class Link:
    def __init__(self, id, type, options, metric, mask=None, endpoints=None, dr=None, bdr=None):
        self.id = id
        self.type = type
        self.options = options
        self.metric = metric
        self.endpoints = endpoints
        self.mask = mask
        self.dr = dr 
        self.bdr = bdr
    
    def add_endpoint(self, endpoint):
        self.endpoints.append(endpoint)

    def set_mask(self, mask):
        self.mask = mask
        self.id = and_bit_to_bit(self.id, mask)

    def set_dr_bdr(self, dr, bdr):
        self.dr = dr
        self.bdr = bdr

    def toJSON(self):
        return {
            "id": self.id,
            "type": self.type,
            "options": self.options,
            "metric": self.metric,
            "mask": self.mask,
            "endpoints": self.endpoints,
            "dr": self.dr,
            "bdr": self.bdr
        }

class Route:
    def __init__(self, ip, mask, via, metric, metric_type=None):
        self.ip = ip
        self.mask = mask
        self.via = via
        self.metric = metric
        self.metric_type = metric_type

    def toJSON(self):
        return {
            "ip": self.ip,
            "mask": self.mask,
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


def and_bit_to_bit(address, mask):
    address_parts = list(map(int, address.split('.')))
    mask_parts = list(map(int, mask.split('.')))
    
    net_address_parts = [address_parts[i] & mask_parts[i] for i in range(4)]
    
    net_address = '.'.join(map(str, net_address_parts))
    return net_address
