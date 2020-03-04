"""
Run Experiments for the Chord DHT Protocol
Uses the ChordNode and Network classes defined in this repo.
"""
import math
import sys
import random
import hashlib
import matplotlib.pyplot as plt
from chord_node import ChordNode
from modules.network import Network

if len(sys.argv) == 2:
    print('Please enter required number of arguments')
    sys.exit(0)

# Global Variables
num_nodes = int(sys.argv[1])
read_from_file = bool(int(sys.argv[2]))
nodes = []
data_store = {}

l = 6
m = 24
num_points = 10000
num_queries = 1000000


def plot_histogram(dict):
    plt.bar(dict.keys(), dict.values())
    plt.xlim(0, 14)
    plt.ylim(0, 0.6)
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

        pn = ChordNode(i, node_hash, network, m)
        is_added = network.add_node(pn)
        if is_added:
            pn.join()
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
    hops_hist = {}
    num_epoch = 0
    flag = 0
    count = 0
    for _ in range(100):
        for q in data_store:
            flag = 0
            count += 1
            if (count % 10000 == 0):
                num_epoch += 1
                print(str(num_epoch) + ' epochs completed')
            hit_node = int(hash_int(random.choice(nodes)), 16)
            node = network.get_node(hit_node)
            hops, chord_value, path = node.search(q)
            print('Lookup ' + str(q) + ': ' + str(path))
            # Add in histogram
            hops = 12 if hops > 12 else hops
            if hops in hops_hist:
                hops_hist[hops] += 1
            else:
                hops_hist[hops] = 1

            if chord_value == -1:
                try:
                    global_value = data_store[q]
                    flag = 1
                    print(
                        str(q) + ': Found ' + str(global_value) +
                        ' when not stored')
                except:
                    continue
            else:
                try:
                    global_value = data_store[q]
                    if (chord_value != global_value):
                        print(
                            str(q) + ': Found ' + str(global_value) +
                            ' when ' + str(chord_value) + ' stored')
                        flag = 1
                except:
                    flag = 1
            if flag == 1:
                print('Couldn\'t find node ' + str(q) + ' correctly')
            if count >= num_queries:
                break
        if count >= num_queries:
            break

    if flag == 0:
        print('All queries ran successfully')

    new_dict = {}
    avg_hops = 0
    for k in hops_hist:
        new_dict[k] = hops_hist[k] / num_queries
        avg_hops += (new_dict[k] * k)
    print(avg_hops)
    plot_histogram(new_dict)


def store_keys(network, num_keys):
    """Store keys in the Chord Network
    
    Arguments:
        network {Network}
        num_keys {Integer}
    """
    global num_points
    count = 0
    for key in range(2 * num_keys):
        value = random.randint(0, 2 * num_keys)
        # Choose a random node and store in it
        rand_node = int(hash_int(random.choice(nodes)), 16)
        node = network.get_node(rand_node)
        is_stored = node.store_key(key, value)
        if is_stored == 0:
            # Also store in the global array
            count += 1
            data_store[key] = value
            if count == num_points:
                break


def delete_nodes(network, del_nodes):
    """Simulate deletion of nodes from network
    
    Arguments:
        network {Network}
        del_nodes {Integer} -- Number of nodes to be deleted
    """
    num_deleted = 0
    while num_deleted < del_nodes:
        chosen_node = random.choice(nodes)
        del_node = network.get_node(int(hash_int(chosen_node), 16))
        removed = del_node.depart_network()
        if removed:
            num_deleted += 1
            nodes.remove(chosen_node)


# Number of switches :- Max number of nodes that can be added onto the network
num_switches = num_nodes
network = Network(num_switches, read_from_file)

# Initialize network
init_network(network, num_nodes)
store_keys(network, num_points)
search_queries(network, num_queries)
delete_nodes(network, num_nodes // 2)
search_queries(network, num_queries)

print('Total number of nodes: ' + str(num_nodes))
print('Total number of data points: ' + str(num_points))
print('Total number of search queries: ' + str(num_queries))
print('Total number of node add queries: ' + str(num_nodes))
print('Total number of node delete queries: ' + str(num_nodes // 2))
print('Total number of data add queries: ' + str(num_queries))
