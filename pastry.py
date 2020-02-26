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
num_nodes = int(sys.argv[1])
read_from_file = bool(int(sys.argv[2]))
nodes = []
l = 6
b = 4

def init_network(network, num_nodes):
    for i in range(num_nodes):
        print ("Adding node " + str(i))
        node_name = str(i)
        m = hashlib.sha1(node_name.encode('utf-8'))
        node_hash = m.hexdigest()[:6]
        print (node_hash)
        pn = PastryNode(node_hash, l, b)
        network.add_node(pn)
        pn.expanding_multicast(network)


# Number of switches :- Max number of nodes that can be added onto the network
num_switches = 2000
network = Network(num_switches, read_from_file)
init_network(network, num_nodes)
