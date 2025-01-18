class Network:
    def __init__(self, area):
        self.area = area
        self.nodes = set()
        self.links = set()
        self.ospfInterAreaRoutes = set()

    def add_node(self, node):
        self.nodes.add(node)

    def add_link(self, link):
        self.links.add(link)

    def add_inter_area_route(self, route):
        self.ospfInterAreaRoutes.add(route)

    def __str__(self):
        topology_str = f"topology area {self.area}:\n  nodes:"

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
        
        for route in self.ospfInterAreaRoutes:
            topology_str += f"\n    - ip: {route.ip}"
            topology_str += f"\n      - mask: {route.mask}"
            topology_str += f"\n      - via: {route.via}"
            topology_str += f"\n      - metric: {route.metric}"

        return topology_str


class Node:
    def __init__(self, router_id, interface_list=None):
        self.router_id = router_id
        self.interfaces = interface_list if interface_list else []
        self.neighbors = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def add_neighbor(self, interface, neighbor_router_id, adjacency_state, designated_router, backup_designated_router):
        self.neighbors.append({
            "interface": interface,
            "router_id": neighbor_router_id,
            "adjacency_state": adjacency_state,
            "designated_router": designated_router,
            "backup_designated_router": backup_designated_router
        })

    def __str__(self):
        interface_str = "\n        ".join(str(iface) for iface in self.interfaces)
        neighbors_str = "\n        ".join(
            f"Interface: {n['interface']}, Router ID: {n['router_id']}, "
            f"Adjacency State: {n['adjacency_state']}, Designated Router: {n['designated_router']}, "
            f"Backup Designated Router: {n['backup_designated_router']}" for n in self.neighbors
        )
        return (
            f"Router ID: {self.router_id}\n"
            f"    Interfaces:\n        {interface_str}\n"
            f"    Neighbors:\n        {neighbors_str if self.neighbors else 'None'}"
        )


class Interface:
    def __init__(self, id, ip, masklen, ok, status):
        self.id = id
        self.ip = ip
        self.masklen = masklen
        self.ok = ok
        self.status = status

    def __str__(self):
        return f"ID: {self.id}, IP: {self.ip}/{self.masklen}, OK: {self.ok}, Status: {self.status}"
    
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

    def set_dr_bdr(self, dr, bdr):
        self.dr = dr
        self.bdr = bdr


class Route:
    def __init__(self, ip, mask, via, metric):
        self.ip = ip
        self.mask = mask
        self.via = via
        self.metric = metric