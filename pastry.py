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
l = 4
b = 4

def init_network(network, num_nodes):
    num_added = 0
    for i in range(2 * num_nodes):
        print ("Adding node " + str(i))
        node_name = str(i)
        m = hashlib.sha1(node_name.encode('utf-8'))
        node_hash = m.hexdigest()[:l]
        print (node_hash)
        pn = PastryNode(node_hash, l, b)
        is_added = network.add_node(pn)
        if is_added:
            pn.expanding_multicast(network)
            num_added += 1
        if num_added == num_nodes:
            break

# Number of switches :- Max number of nodes that can be added onto the network
num_switches = num_nodes
network = Network(num_switches, read_from_file)
init_network(network, num_nodes)
