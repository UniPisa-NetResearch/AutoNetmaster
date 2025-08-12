import pyeapi
import json

def get_areas(target_node):
    output=target_node.enable("show ipv6 ospf")

    info_areas= output[0]["result"]["vrfs"]["default"]["instList"]["10"]["areaList"]

    areas=[]
    for a in info_areas:
        areas.append(a)

    return areas