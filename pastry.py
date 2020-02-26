"""
Run Experiments for the Pastry DHT Protocol
Uses the PastryNode and Network classes defined in this repo.
"""
import math
import sys
import hashlib
from pastry_node import PastryNode
from modules.network import Network

if len(sys.argv) == 2:
    print ('Please enter required number of arguments')
    sys.exit(0)

# Global Variables
num_nodes = sys.argv[1]
read_from_file = bool(sys.argv[2])
nodes = []
l = 6
b = 4

def init_network(network, num_nodes):
    for i in range(num_nodes):
        node_name = str(i)
        m = hashlib.sha1(node_name.encode('utf-8'))
        node_hash = int(m.hexdigest()[:6], 16)
        pn = PastryNode(node_hash, l, b)
        network.add_node(pn)



# Number of switches :- Max number of nodes that can be added onto the network
num_switches = math.pow(2, 24)
network = Network(num_switches, read_from_file)

