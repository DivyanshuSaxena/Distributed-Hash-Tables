"""Class Definition"""
import math
import hashlib
import itertools
from modules import network


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


class PastryNode(network.Node):
    """Implementation Class for PastryNode, a single node instance, running the Pastry Protocol
    """
    def __init__(self, ip_addr, node_hash, l, b):
        """Constructor for PastryNode

        Arguments:
            ip_addr {array[4]} -- ip address for the current PastryNode
            node_hash {Integer} -- SHA1 nodeId
            l {Integer} -- length of the SHA1 nodeId
            b {Integer} -- Pastry parameter
        """
        super().__init__()
        super().set_ip(ip_addr)
        self.node_id = node_hash
        L = math.pow(2, b)
        self.routing_table = []
        self.leaf_set = []
        self.neighborhood_set = []
        for _ in range(l):
            row = [-1] * L
            self.routing_table.append(row)

    def route(self, key_hash):
        """Route the request to find the key, to the suitable candidate
        
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

    def node_arrival(self, x):
        pass