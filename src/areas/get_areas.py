import pyeapi
import json

def get_areas(target_node):
    
    command= "sh ospfv3 database"

    output= target_node.enable(command)

    areas=[]

    areasEntries= output[0]['result']['vrfs']['default']['addressFamily']['ipv6']['ospf3AreaEntries']
    
    for area in areasEntries.keys():
        areas.append(area)

    return areas