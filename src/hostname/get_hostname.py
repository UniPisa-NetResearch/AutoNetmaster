import pyeapi

def get_hostname(target_node):
    return (target_node.enable('show hostname'))[0]['result']['hostname']