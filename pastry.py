"""
Run Experiments for the Pastry DHT Protocol
Uses the PastryNode and Network classes defined in this repo.
"""
import math
import sys
import random
import hashlib
from pastry_node import PastryNode
from modules.network import Network

if len(sys.argv) == 2:
    print('Please enter required number of arguments')
    sys.exit(0)

# Global Variables
num_nodes = int(sys.argv[1])
read_from_file = bool(int(sys.argv[2]))
nodes = []

l = 6
b = 4
num_queries = 1000


def hash_int(integer):
    """Hash the given integers and trim to l digits
    
    Arguments:
        integer {Integer}
    
    Returns:
        String -- string of l digits, hash of integer
    """
    name = str(integer)
    m = hashlib.sha1(name.encode('utf-8'))
    node_hash = m.hexdigest()[:l]
    return node_hash


def init_network(network, num_nodes):
    """Initialize network by adding nodes
    
    Arguments:
        network {Network}
        num_nodes {Integer} -- Number of nodes
    """
    num_added = 0
    for i in range(2 * num_nodes):
        print("Adding node " + str(i))
        node_hash = hash_int(i)
        print(node_hash)

        pn = PastryNode(i, node_hash, l, b)
        is_added = network.add_node(pn)
        if is_added:
            pn.expanding_multicast(network)
            num_added += 1
            nodes.append(i)
        if num_added == num_nodes:
            break


def search_queries(network, num_queries):
    """Run search queries for num_queries times
    
    Arguments:
        network {Network}
        num_queries {Integer} -- Number of queries
    """
    # Search queries
    num_epoch = 0
    flag = 0
    for q in range(num_queries):
        if (q % 100 == 0):
            num_epoch += 1
            print(str(num_epoch) + ' epochs completed')
        q_hash = hash_int(q)
        hit_node = int(hash_int(random.choice(nodes)), 16)
        node = network.get_node(hit_node)
        found = node.search(network, q)
        in_list = q in nodes
        if (in_list and found != -1) or (not in_list and found == -1):
            continue
        flag = 1
        print('Couldn\'t find node ' + str(q) + ' correctly')

    if flag == 0:
        print('All queries ran successfully')


def delete_nodes(network, del_nodes):
    """Simulate deletion of nodes from network
    
    Arguments:
        network {Network}
        del_nodes {Integer} -- Number of nodes to be deleted
    """
    num_deleted = 0
    while num_deleted < del_nodes:
        chosen_node = random.choice(nodes)
        del_node = int(hash_int(chosen_node), 16)
        removed = network.remove_node(del_node)
        if removed:
            num_deleted += 1
            nodes.remove(chosen_node)


# Number of switches :- Max number of nodes that can be added onto the network
num_switches = num_nodes
network = Network(num_switches, read_from_file)

# Initialize network
init_network(network, num_nodes)
search_queries(network, num_queries)
delete_nodes(network, 50)
search_queries(network, num_queries)
