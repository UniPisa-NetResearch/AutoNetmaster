import pyeapi
import json

def get_neighbors(target_node):
    neighbors_data = target_node.enable('show ip ospf neighbor')
    
    neighbors_list = []
    ospf_neighbors = neighbors_data[0]['result']['vrfs']['default']['instList']['1']['ospfNeighborEntries']
        
    for neighbor in ospf_neighbors:
        neighbor_info = {
            "router_id": neighbor['routerId'],
            "interface": neighbor['interfaceName'],
            "neighbor_ip_addr": neighbor['interfaceAddress'],
            "adjacency_state": neighbor['adjacencyState'],""
            "designated_router": neighbor['details']['designatedRouter'],
            "backup_designated_router": neighbor['details']['backupDesignatedRouter'],
        }
        neighbors_list.append(neighbor_info)
    
    return neighbors_list
