import pyeapi
import json

def get_summary_lsa_info(target_node):

    command= "show ipv6 ospf database detail"

    output=target_node.enable(command)

    area_entries= output[0]["result"]["vrfs"]["default"]["instList"]["10"]["ospf3AreaEntries"]
    lsa_type_3=[]
    for area_key,area_value in area_entries.items():
        lsa_type_3_area=[]
        for lsa_entry in area_value["ospf3AreaLsaList"]:
            if lsa_entry["lsaType"] == "interAreaPrefixLsa":
                lsa_type_3_area.append(lsa_entry)
        if not(lsa_type_3_area == []):
            lsa_type_3.append({
                area_key:{
                    "ospf3AreaLsaList":lsa_type_3_area
                }
            })

    return lsa_type_3