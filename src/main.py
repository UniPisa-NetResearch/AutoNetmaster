import pyeapi
import sys

from interfaces.get_interfaces import *
from neighbors.get_neighbors import *
from lsa_1.router_lsa import *
from protocol.protocol_info import *
from utilities import *

if len(sys.argv) < 2:
    sys.stderr.write('ERRORE: nodo target non fornito in input\n')
    sys.exit(1)

input_node = sys.argv[1]

print('OSPF Management APP\n\n')

target_node = pyeapi.connect_to(input_node)

interfaces = get_interfaces(target_node)
print('Interfacce ottenute correttamente!\n')

protocol_info = get_protocol_info(target_node)
print('Informazioni generali sul protocollo OSPF ottenute correttamente!')

router = Node(protocol_info['Router ID'], interfaces)

neighbors = get_neighbors(target_node)
print('OSPF neighbors ottenuti correttamente!\n')
