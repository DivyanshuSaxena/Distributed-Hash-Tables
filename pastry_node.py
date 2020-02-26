"""Class Definition"""
import math
import hashlib
import itertools
from modules.network import Node, Network


def common_prefix(key, node_id):
    """Find the common prefix between two hex digit numbers
    
    Arguments:
        key {Hex String}
        node_id {Hex String}

    Returns:
        Integer -- Length of common prefix
    """
    prefix = key
    while node_id[:len(prefix)] != prefix and prefix:
        prefix = prefix[:len(prefix) - 1]
    return len(prefix[2:])


class PastryNode(Node):
    """Implementation Class for PastryNode, a single node instance, 
       running the Pastry Protocol"""
    def __init__(self, node_hash, l, b):
        """Constructor for PastryNode

        Arguments:
            node_hash {Integer} -- SHA1 nodeId
            l {Integer} -- length of the SHA1 nodeId
            b {Integer} -- Pastry parameter
        """
        super().__init__(node_hash)
        L = math.pow(2, b)
        self.routing_table = []
        self.leaf_set = []
        self.neighborhood_set = []
        for _ in range(l):
            row = [-1] * L
            self.routing_table.append(row)

    def get_routing_table(self):
        """Return the routing table to whoever wants this table
        
        Returns:
            Array -- Routing Table
        """
        return self.routing_table

    def get_neighborhood_set(self):
        """Return the neighborhood set to when wanted
        
        Returns:
            Array -- Neighborhood Set
        """
        return self.neighborhood_set

    def get_leaf_set(self):
        """Return the leaf set to when wanted
        
        Returns:
            Array -- Leaf Set
        """
        return self.leaf_set

    def __repair_leaf_set(self, network, failed_node):
        """Repair the leaf set of a node when a node in leaf set fails
        
        Arguments:
            network {Network}
            failed_node {Integer} -- Hash of the node which failed
        """
        # Find on which side the failed node is, in the leaf set
        num_smaller = 0
        for leaf in self.leaf_set:
            if failed_node > leaf:
                num_smaller += 1
        is_smaller = num_smaller > len(self.leaf_set) / 2
        if is_smaller:
            get_ls_from = min(self.leaf_set)
        else:
            get_ls_from = max(self.leaf_set)

        # Get the leaf set from this node
        leaf_node = (PastryNode)(network.get_node(get_ls_from))
        if is_smaller:
            # Get fromthe min in the leaf set
            min_diff = 0
            min_node = 0
            for leaf in leaf_node.get_leaf_set():
                diff = leaf - min(self.leaf_set)
                if diff < 0 and (abs(diff) < abs(min_diff) or min_diff == 0):
                    min_diff = diff
                    min_node = leaf
            self.leaf_set.remove(failed_node)
            self.leaf_set.append(min_node)
        else:
            # Get from the max in the leaf set
            min_diff = 0
            min_node = 0
            for leaf in leaf_node.get_leaf_set():
                diff = leaf - max(self.leaf_set)
                if diff > 0 and (abs(diff) < abs(min_diff) or min_diff == 0):
                    min_diff = diff
                    min_node = leaf
            self.leaf_set.remove(failed_node)
            self.leaf_set.append(min_node)

    def __repair_neighborhood_set(self, network, failed_node):
        """Repair the neighborhood set of a node when another one fails
        
        Arguments:
            network {Network}
            failed_node {Integer} -- Hash of the node which failed
        """
        # Find the nearest node
        nearest = -1
        nearest_node = -1
        for neighbor in self.neighborhood_set:
            # Don't consider if the neighbor is the failed node
            if neighbor == failed_node: continue
            distance = network.proximity(self.get_num(), neighbor)
            if nearest == -1 or distance < nearest:
                nearest = distance
                nearest_node = neighbor

        # Find the nearest node that hasn't yet been included
        neighborhood_set = network.get_node(
            nearest_node).get_neighborhood_set()
        nearest = -1
        nearest_node = -1
        for node in neighborhood_set:
            if node not in self.neighborhood_set:
                # Find the nearest such node
                distance = network.proximity(self.get_num(), node)
                if nearest == -1 or distance < nearest:
                    nearest = distance
                    nearest_node = node
        self.neighborhood_set.remove(failed_node)
        self.neighborhood_set.append(nearest_node)

    def repair(self, network, failed_node):
        # First repair leaf and neighborhood set in the wake of failed node
        if failed_node in self.leaf_set:
            self.__repair_leaf_set(network, failed_node)
        if failed_node in self.neighborhood_set:
            self.__repair_neighborhood_set(network, failed_node)

        # Find the entry in the routing table
        l = d = 0
        contact_list = []
        for row_index in range(len(self.routing_table)):
            row = self.routing_table[row_index]
            for node_index in range(len(row)):
                if row[node_index] == failed_node:
                    l = row_index
                    d = node_index
        for node in itertools.chain(self.routing_table[l],
                                    self.routing_table[l + 1]):
            if node != failed_node:
                contact_list.append(node)

        replacement = failed_node
        # Contact each of these nodes to find replacement for the failed node
        for node_hash in contact_list:
            contact_node = (PastryNode)(network.get_node(node_hash))
            # Check if the alternate node is alive
            alternate_node = contact_node.get_routing_table()[l][d]
            if network.is_alive(
                    alternate_node) and alternate_node != failed_node:
                replacement = alternate_node
                break
        self.routing_table[l][d] = replacement

    def __route(self, key_hash):
        """
        Internal function to find the suitable candidate, to send request
        Implemented following the Pastry Protocol

        Arguments:
            key_hash {Integer} -- Hash of the key to be found
        
        Returns:
            Integer -- NodeId of the next node to which the request is to be
                       forwarded (returns -1 if not present)
        """
        # Find if the key is in the leaf set
        if key_hash >= min(self.leaf_set) and key_hash <= max(self.leaf_set):
            min_diff = key_hash
            min_node = 0x0
            for node in self.leaf_set:
                if abs(node - key_hash) < min_diff:
                    min_diff = abs(node - key_hash)
                    min_node = node
            return min_node
        else:
            # Not found in leaf set: route to the most suitable next node
            l = common_prefix(hex(key_hash), hex(self.node_id))
            if self.routing_table[l][hex(key_hash)[l + 2]]:
                return self.routing_table[l][hex(key_hash)[l + 2]]
            else:
                min_diff = abs(self.node_id - key_hash)
                # Check in leaf set and neighbourhood set
                for node in itertools.chain(self.leaf_set,
                                            self.neighborhood_set):
                    diff = abs(node - key_hash)
                    prefix = common_prefix(hex(key_hash), hex(node))
                    if diff < min_diff and prefix >= l:
                        return node
                # Check in routing table
                for row in self.routing_table:
                    for node in row:
                        diff = abs(node - key_hash)
                        prefix = common_prefix(hex(key_hash), hex(node))
                        if diff < min_diff and prefix >= l:
                            return node
                # Key not located in the DHT
                return -1

    def route(self, network, key_hash):
        """Public Function to route the request to the next node
        
        Arguments:
            network {Network} -- Pastry Network instance
            key_hash {String} -- Hash of the key to be searched
        
        Returns:
            Integer -- Integer hash of the next node to ping
        """
        # Check if the node is alive.
        next_node = self.__route(key_hash)
        if not network.is_alive(next_node):
            # Node has failed/departed. Follow repair protocol
            self.repair(network, next_node)
            next_node = self.__route(key_hash)
        return next_node

    def node_arrival(self, x):
        """Function Call that shall be made when node X enters the network and
           contacts current node
        
        Arguments:
            x {Integer} -- nodeId of the newly arrived node
        """
        # Send all routing tables, A's neighbourhood set and Z's leaf set to X
        routing_tables = []
        routing_tables.append(self.get_routing_table())
        next_node = self.route(x)
        while next_node != -1:
            routing_tables.append(next_node.get_routing_table())
            next_node = next_node.route(x)

        leaf_set = self.get_leaf_set()
        neighborhood_set = next_node.get_neighborhood_set()
        return leaf_set, neighborhood_set, routing_tables
