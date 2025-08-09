import pyeapi
import json
def get_network_lsa_info(target_node):

    command= "show ipv6 ospf database detail"

    output=target_node.enable(command)

    area_entries= output[0]["result"]["vrfs"]["default"]["instList"]["10"]["ospf3AreaEntries"]
    lsa_type_2=[]
    for area_key,area_value in area_entries.items():
        lsa_type_2_area=[]
        for lsa_entry in area_value["ospf3AreaLsaList"]:
            if lsa_entry["lsaType"] == "networkLsa":
                lsa_type_2_area.append(lsa_entry)
        if not(lsa_type_2_area == []):
            lsa_type_2.append({
                area_key:{
                    "ospf3AreaLsaList":lsa_type_2_area
                }
            })

    return lsa_type_2