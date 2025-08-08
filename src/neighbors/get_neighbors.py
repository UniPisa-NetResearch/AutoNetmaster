import pyeapi
import json

def get_neighbors(target_node):
    neighbors_data = target_node.enable('show ipv6 ospf neighbor')
    
    neighbors_list = []
    ospf_neighbors = neighbors_data[0]['result']['vrfs']['default']['instList']['10']['ospf3NeighborEntries']
        
    for neighbor in ospf_neighbors:
        neighbor_info = {
            "router_id": neighbor['routerId'],
            "interface": neighbor['interfaceName'],
            "adjacency_state": neighbor['adjacencyState'],
            "designated_router": neighbor['designatedRouter'],
            "backup_designated_router": neighbor['backupDesignatedRouter'],
        }
        neighbors_list.append(neighbor_info)
    
    return neighbors_list
