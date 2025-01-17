import pyeapi
import json

def get_protocol_info(target_node):

    command = "show ip ospf"
    info = target_node.enable(command)[0]['result']
    
    vrf_data = info.get('vrfs', {}).get('default', {})
    inst_list = vrf_data.get('instList', {})
    ospf_instance = next(iter(inst_list.values()), {})
    
    router_id = ospf_instance.get('routerId', 'Unknown')
    
    area_list = ospf_instance.get('areaList', {})
    areas = []
    for area_id, area_details in area_list.items():
        areas.append({
            "Area ID": area_id,
            "Stub Area": area_details.get('stubArea', False),
            "Normal Area": area_details.get('normalArea', False)
        })
    
    summary = {
        "Router ID": router_id,
        "Areas": areas
    }
    
    return summary
