"""
Run Experiments for the Pastry DHT Protocol
Uses the PastryNode and Network classes defined in this repo.
"""
import math
import sys
import random
import hashlib
import matplotlib.pyplot as plt
from pastry_node import PastryNode
from modules.network import Network

if len(sys.argv) == 2:
    print('Please enter required number of arguments')
    sys.exit(0)

# Global Variables
num_nodes = int(sys.argv[1])
read_from_file = bool(int(sys.argv[2]))
nodes = []
nodes_hash = []

l = 6
b = 4
num_queries = 1000000


def plot_histogram(dict):
    plt.bar(dict.keys(), dict.values())
    plt.xlim(0, 12)
    plt.ylim(0, 0.8)
    plt.xlabel('Number of Hops')
    plt.ylabel('Probability')
    plt.show()


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

        pn = PastryNode(i, node_hash, network, l, b)
        is_added = network.add_node(pn)
        if is_added:
            pn.join()
            num_added += 1
            nodes.append(i)
            nodes_hash.append(int(node_hash, 16))
        if num_added == num_nodes:
            break


def search_queries(network, num_queries):
    """Run search queries for num_queries times
    
    Arguments:
        network {Network}
        num_queries {Integer} -- Number of queries
    """
    hops_hist = {}
    num_epoch = 0
    flag = 0
    count = 0
    for _ in range(100):
        for q in range(num_queries // 100):
            count += 1
            if (count % 10000 == 0):
                num_epoch += 1
                print(str(num_epoch) + ' epochs completed')
            hit_node = int(hash_int(random.choice(nodes)), 16)
            node = network.get_node(hit_node)
            hops, found = node.search(q)

            # Add in histogram
            hops = 10 if hops > 10 else hops
            if hops in hops_hist:
                hops_hist[hops] += 1
            else:
                hops_hist[hops] = 1
            q_hash = int(hash_int(q), 16)
            in_list = q_hash in nodes_hash
            if (in_list and found != -1) or (not in_list and found == -1):
                continue
            flag = 1
            print(in_list, found)
            print('Couldn\'t find node ' + str(q) + ' correctly')

    if flag == 0:
        print('All queries ran successfully')

    new_dict = {}
    avg_hops = 0
    for k in hops_hist:
        new_dict[k] = hops_hist[k] / num_queries
        avg_hops += (new_dict[k] * k)
    print(avg_hops)
    plot_histogram(new_dict)


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
            nodes_hash.remove(int(hash_int(chosen_node), 16))


# Number of switches :- Max number of nodes that can be added onto the network
num_switches = num_nodes
network = Network(num_switches, read_from_file)

# Initialize network
init_network(network, num_nodes)
search_queries(network, num_queries)
delete_nodes(network, num_nodes // 2)
search_queries(network, num_queries)
