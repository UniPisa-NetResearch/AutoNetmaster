class Network:
    def __init__(self, target_router):
        self.target_router = target_router
        self.topology = {target_router}

    def add_node(self, node):
        self.topology.add(node)

    def __str__(self):
        result = f"Target Router: {self.target_router}\nTopology:\n"
        for node in self.topology:
            result += f"- {node}\n"
        return result
    

class Node:
    def __init__(self, router_id, interface_list=None):
        self.router_id = router_id
        self.interfaces = interface_list if interface_list else []  # Lista di interfaccie

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def __str__(self):
        interface_str = "\n  ".join(str(iface) for iface in self.interfaces)
        return f"Router ID: {self.router_id}\n  Interfaces:\n  {interface_str}"


class Interface:
    def __init__(self, id, ip, masklen, ok, status):
        self.id = id
        self.ip = ip
        self.masklen = masklen
        self.ok = ok
        self.status = status

    def __str__(self):
        return f"ID: {self.id}, IP: {self.ip}, Status: {self.status}, Protocol: {self.protocol}"
