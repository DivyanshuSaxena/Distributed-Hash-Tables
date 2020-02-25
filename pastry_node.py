"""Class Definition
"""
import math


class PastryNode:
    """Implementation Class for PastryNode, a single node instance, running the Pastry Protocol
    """
    def __init__(self, nid, l, b):
        """Constructor for PastryNode

        Arguments:
            nid {Integer} -- nodeId for the current PastryNode
            l {Integer} -- length of the SHA1 nodeId
            b {Integer} -- Pastry parameter
        """
        L = math.pow(2, b)
        self.node_id = nid
        self.routing_table = []
        self.leaf_set = []
        self.neighborhood_set = []
        for _ in range(l):
            row = [-1] * L
            self.routing_table.append(row)

    def route(self, key_hash):
        pass

    def node_arrival(self, x):
        pass