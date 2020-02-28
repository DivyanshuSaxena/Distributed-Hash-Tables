"""Class Definition for PastryNode"""
import math
import time
import hashlib
import itertools
from modules.network import Node, Network

# NOTE: Node Instances may call and use instance variables from other nodes,
# without sending network packets. [Five Instances in the File]
# TODO: Simulate number of packets in the network accordingly.

length = 0
B = 0


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


def circular_between(start, bet, end):
    """Finds if bet is in between start and end
    
    Arguments:
        start {Integer}
        bet {Integer}
        end {Integer}
    
    Returns:
        Boolean -- True if it is in between, else False
    """
    if end > start:
        return (bet > start and bet < end)
    elif end < start:
        return (bet > start or bet < end)


def circular_abs(node1, node2):
    """Find how numerically closer node1 and node2 are
    
    Arguments:
        node1 {Integer} -- Node Id
        node2 {Integer} -- Node Id
    
    Returns:
        Integer -- Circular Absolute Difference
    """
    global length
    return min(abs(node1 - node2), math.pow(16, length) - abs(node1 - node2))


def hex_code(int_val):
    """Returns six digit hex code
    
    Arguments:
        int_val {Integer}
    
    Returns:
        String -- Hex String of length digits
    """
    global length
    hex_string = hex(int_val)[2:]
    while len(hex_string) != length:
        hex_string = '0' + hex_string
    ret = '0x' + hex_string
    return ret


class PastryNode(Node):
    """Implementation Class for PastryNode, a single node instance, 
       running the Pastry Protocol"""
    def __init__(self, node_id, node_hash, network, l, b):
        """Constructor for PastryNode

        Arguments:
            node_id {Integer} -- Network Id of the node
            node_hash {String} -- SHA1 nodeId
            network {Network}
            l {Integer} -- length of the SHA1 nodeId
            b {Integer} -- Pastry parameter
        """
        global length, B
        super().__init__(node_id, node_hash, network)
        self.L = int(math.pow(2, b))
        self.routing_table = []
        self.leaf_set = []
        self.neighborhood_set = []
        length = l
        B = b
        for _ in range(l):
            row = [-1] * self.L
            self.routing_table.append(row)

        # Update routing table to include self entry
        hash_string = hex_code(self.get_num())[2:]
        for index in range(length):
            digit = hash_string[index]
            self.routing_table[index][int(digit, 16)] = self.get_num()

    def __str__(self):
        """Print the PastryNode instance"""
        print(
            '\n-------------------------------------------------------------')
        print('PastryNode: ' + str(self.get_num()) + ' | ' +
              hex_code(self.get_num()))
        ls_string = [hex_code(x)[2:] for x in self.leaf_set]
        print('Leaf Set: ' + str(ls_string))
        for row in self.routing_table:
            for entry in row:
                if entry != -1:
                    print(hex_code(entry)[2:], end='\t')
                else:
                    print(-1, end='\t')
            print('\n')
        print('-------------------------------------------------------------')
        return ''

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

    def __extreme_leaf_set(self, extreme, failed_nodes=None):
        """Get the extremes of the current node's leaf set
        
        Arguments:
            extreme {Integer} -- -1 for min (right extreme),
                                  1 for max (left extreme)

        Keyword Arguments:
            failed_nodes {List} -- List of Node Ids of a failed nodes
                                   (default: {None})

        Returns:
            Integer -- Node Id of the extreme node
        """
        greater_list = []
        lower_list = []
        for node in self.leaf_set:
            if failed_nodes and node in failed_nodes: continue
            if node > self.get_num():
                greater_list.append(node)
            else:
                lower_list.append(node)
        greater_list.sort()
        lower_list.sort()

        if len(greater_list) + len(lower_list) < self.L:
            if extreme == -1:
                if len(lower_list) != 0:
                    return lower_list[0]
            else:
                if len(greater_list) != 0:
                    return greater_list[-1]
            return self.get_num()
        else:
            if extreme == -1:
                if len(lower_list) >= self.L / 2:
                    return lower_list[-self.L // 2]
                else:
                    return greater_list[self.L // 2]
            else:
                if len(greater_list) >= self.L / 2:
                    return greater_list[self.L // 2 - 1]
                else:
                    return lower_list[-self.L // 2 - 1]

    def __merge_leaf_set(self, array, failed_nodes=None):
        """
        Merge the array into the current node's leaf set, choosing the right
        nodes.
        
        Arguments:
            array {List} -- List of leaf nodes that can potentially be added

        Keyword Arguments:
            failed_nodes {List} -- List of Node Ids of a failed nodes
                                   (default: {None})
        """
        greater_list = []
        lower_list = []
        for node in itertools.chain(self.leaf_set, array):
            if failed_nodes:
                if node in failed_nodes or (
                        not self.network_api.is_alive(node)):
                    continue
            if node > self.get_num() and (node not in greater_list):
                greater_list.append(node)
            elif node < self.get_num() and (node not in lower_list):
                lower_list.append(node)
        greater_list.sort()
        lower_list.sort()

        # Merge the two lists to get the final leaf set
        if len(greater_list) + len(lower_list) <= self.L:
            greater_list.extend(lower_list)
            self.leaf_set = greater_list
        else:
            if len(greater_list) < self.L / 2:
                num_needed = int(self.L / 2 - len(greater_list))
                greater_list.extend(lower_list[:num_needed])
                lower_list = lower_list[num_needed:]
            if len(lower_list) < self.L / 2:
                num_needed = int(self.L / 2 - len(lower_list))
                lower_list.extend(greater_list[-num_needed:])
                greater_list = greater_list[:-num_needed]
            if len(greater_list) > self.L / 2:
                greater_list = greater_list[:self.L // 2]
            if len(lower_list) > self.L / 2:
                lower_list = lower_list[-self.L // 2:]
            greater_list.extend(lower_list)
            self.leaf_set = greater_list

    def __repair_leaf_set(self, failed_node):
        """Repair the leaf set of a node when a node in leaf set fails
        
        Arguments:
            failed_node {Integer} -- Hash of the node which failed
        """
        # Find on which side the failed node is, in the leaf set
        # Check if failed_node is between min_leaf and node
        is_smaller = circular_between(self.__extreme_leaf_set(-1), failed_node,
                                      self.get_num())
        if is_smaller:
            get_ls_from = self.__extreme_leaf_set(-1)
        else:
            get_ls_from = self.__extreme_leaf_set(1)

        # Get the leaf set from this node, if alive else search for other nodes
        failed_nodes = [failed_node]
        while not self.network_api.is_alive(get_ls_from):
            failed_nodes.append(get_ls_from)
            is_smaller = circular_between(
                self.__extreme_leaf_set(-1, failed_nodes), failed_node,
                self.get_num())
            if is_smaller:
                get_ls_from = self.__extreme_leaf_set(-1, failed_nodes)
            else:
                get_ls_from = self.__extreme_leaf_set(1, failed_nodes)

        leaf_node = (self.network_api.get_node(get_ls_from))
        # Delete the failed node and then, merge
        self.leaf_set.remove(failed_node)
        self.__merge_leaf_set(leaf_node.get_leaf_set(),
                              failed_nodes=failed_nodes)

    def __repair_neighborhood_set(self, failed_node):
        """Repair the neighborhood set of a node when another one fails
        
        Arguments:
            failed_node {Integer} -- Hash of the node which failed
        """
        self.neighborhood_set.remove(failed_node)

        # Find the nearest node
        nearest = -1
        nearest_node = -1
        for neighbor in self.neighborhood_set:
            distance = self.network_api.proximity(self.get_num(), neighbor)
            if distance != -1 and (nearest == -1 or distance < nearest):
                nearest = distance
                nearest_node = neighbor

        # Find the nearest node that hasn't yet been included
        neighborhood_set = self.network_api.get_node(
            nearest_node).get_neighborhood_set()
        nearest = -1
        nearest_node = -1
        for node in neighborhood_set:
            if node not in self.neighborhood_set:
                # Find the nearest such node
                distance = self.network_api.proximity(self.get_num(), node)
                if distance != -1 and (nearest == -1 or distance < nearest):
                    nearest = distance
                    nearest_node = node
        if nearest_node != -1:
            self.neighborhood_set.append(nearest_node)

    def __repair(self, failed_node):
        """Repair the leaf and neighborhoodsets and the routing table
        
        Arguments:
            failed_node {Integer} -- Hash of the node which has failed
        """
        global length
        # First repair leaf and neighborhood set in the wake of failed node
        if failed_node in self.leaf_set:
            self.__repair_leaf_set(failed_node)
        if failed_node in self.neighborhood_set:
            self.__repair_neighborhood_set(failed_node)

        # Find the entry in the routing table
        l = d = -1
        contact_list = []
        for row_index in range(length):
            row = self.routing_table[row_index]
            for node_index in range(len(row)):
                if row[node_index] == failed_node:
                    l = row_index
                    d = node_index
        if l != -1 and d != -1:
            for node in itertools.chain(self.routing_table[l],
                                        self.routing_table[l + 1]):
                if node != failed_node and self.network_api.is_alive(node):
                    contact_list.append(node)

            replacement = failed_node
            # Contact each of these nodes to find replacement for the failed node
            for node_hash in contact_list:
                contact_node = (self.network_api.get_node(node_hash))
                # Check if the alternate node is alive
                alternate_node = contact_node.get_routing_table()[l][d]
                if self.network_api.is_alive(
                        alternate_node) and alternate_node != failed_node:
                    replacement = alternate_node
                    break

            if replacement == failed_node:
                self.routing_table[l][d] = -1
            else:
                self.routing_table[l][d] = replacement

        # State after repair
        # print("After repair: ", self)  # Debug

    def __route(self, key_hash):
        """
        Internal function to find the suitable candidate, to send request
        Implemented following the Pastry Protocol

        Arguments:
            key_hash {Integer} -- Hash of the key to be found
        
        Returns:
            Integer -- NodeId of the next node to which the request is to be
                       forwarded
                       (returns -1 if not present and 16^length if found)
        """
        global length
        l = common_prefix(hex_code(key_hash), hex_code(self.get_num()))
        if l == length:
            return int(math.pow(16, length))

        # print("Running Internal Route at node " + hex_code(self.get_num()) +
        #       " to search " + hex_code(key_hash))  # Debug
        # Find if the key is in the leaf set
        ls_string = [hex_code(x)[2:] for x in self.leaf_set]
        if circular_between(self.__extreme_leaf_set(-1), key_hash,
                            self.__extreme_leaf_set(1)):
            min_diff = -1
            min_node = 0x0
            diff_arr = []
            for node in self.leaf_set:
                diff_arr.append(circular_abs(node, key_hash))
                if circular_abs(node, key_hash) < min_diff or min_diff == -1:
                    min_diff = circular_abs(node, key_hash)
                    min_node = node
            # Route only if min_node is closer than current node
            diff = circular_abs(self.get_num(), key_hash)
            if diff > min_diff:
                return min_node
            return -1

        # print("Not found in leaf set") # Debug
        # Not found in leaf set: route to the most suitable next node
        digit = hex_code(key_hash)[2:][l]
        if self.routing_table[l][int(digit, 16)] != -1:
            # print("Found " + hex_code(key_hash) + " in routing table of ",
            #       hex_code(self.get_num()),
            #       hex_code(self.routing_table[l][int(digit, 16)]), l,
            #       digit)  # Debug
            return self.routing_table[l][int(digit, 16)]
        else:
            min_diff = circular_abs(self.get_num(), key_hash)
            # Check in leaf set and neighbourhood set
            for node in itertools.chain(self.leaf_set, self.neighborhood_set):
                diff = circular_abs(node, key_hash)
                prefix = common_prefix(hex_code(key_hash), hex_code(node))
                if diff < min_diff and prefix >= l:
                    return node
            # Check in routing table
            for row in self.routing_table:
                for node in row:
                    diff = circular_abs(node, key_hash)
                    prefix = common_prefix(hex_code(key_hash), hex_code(node))
                    if diff < min_diff and prefix >= l:
                        return node
            # Key not located in the DHT
            return -1

    def route(self, key_hash):
        """Public Function to route the request to the next node
        
        Arguments:
            key_hash {String} -- Hash of the key to be searched
        
        Returns:
            Integer -- Integer hash of the next node to ping
                       (returns -1 if not present and 16^length if found)
        """
        global length
        next_node = self.__route(key_hash)
        # Search query found
        if next_node == int(math.pow(16, length)) or next_node == -1:
            return next_node

        # Check if the node is alive.
        while (not self.network_api.is_alive(next_node)):
            # Node has failed/departed. Follow repair protocol
            # print('Failed Node: ' + hex_code(next_node))
            self.__repair(next_node)
            next_node = self.__route(key_hash)
            if next_node == int(math.pow(16, length)) or next_node == -1:
                return next_node
        return next_node

    def node_init(self, routing_tables, leaf_set, neighborhood_set):
        """Initialize routing table, leaf set and neighborhood set of a newly
        added node
        
        Arguments:
            routing_tables {Array} -- List of routing tables from A -> Z
            leaf_set {List} -- Leaf set of Z (Numerically Closest Node)
            neighborhood_set {List} -- Neighborhood set of A (Closest Node)
        
        Returns:
            Iterable -- Iterable of nodes to which the update of this node
            is to be sent
        """
        global length, B
        # Add into leaf set
        self.__merge_leaf_set(leaf_set)

        # Also fetch from extreme nodes
        min_extreme = self.__extreme_leaf_set(-1)
        max_extreme = self.__extreme_leaf_set(1)
        min_node = self.network_api.get_node(min_extreme)
        max_node = self.network_api.get_node(max_extreme)
        self.__merge_leaf_set(min_node.get_leaf_set())
        self.__merge_leaf_set(max_node.get_leaf_set())

        # Select the neighborhood set
        # Remove the farthest node, if neighborhood set is large
        if len(neighborhood_set) > math.pow(2, B + 1):
            farthest = -1
            farthest_node = -1
            for node in neighborhood_set:
                distance = self.network_api.proximity(self.get_num(), node)
                if distance != -1 and (farthest < distance or farthest == -1):
                    farthest = distance
                    farthest_node = node
            neighborhood_set.remove(farthest_node)
        self.neighborhood_set = neighborhood_set

        # Update from the routing tables received
        routing_table_nodes = []
        for index in range(len(routing_tables)):
            for node_index in range(self.L):
                self.routing_table[index][node_index] = routing_tables[index][
                    index][node_index]
                node = self.routing_table[index][node_index]
                if (node != -1) and (node not in self.leaf_set) and (
                        node not in self.neighborhood_set):
                    routing_table_nodes.append(node)

        # Update leaf_set and neighborhood_set nodes in routing table
        for node in itertools.chain(leaf_set, neighborhood_set):
            l = common_prefix(hex_code(node), hex_code(self.get_num()))
            # If match till lth level, add in routing table
            digit = hex_code(node)[2:][l]
            if l >= 1 and self.routing_table[l][int(digit, 16)] == -1:
                self.routing_table[l][int(digit, 16)] = node

        # Update routing table to include self entry
        hash_string = hex_code(self.get_num())[2:]
        for index in range(length):
            digit = hash_string[index]
            self.routing_table[index][int(digit, 16)] = self.get_num()

        # Send the node state to other nodes
        return itertools.chain(routing_table_nodes, self.leaf_set,
                               self.neighborhood_set)

    def node_arrival(self, x):
        """Function Call that shall be made when node X enters the network and
           contacts current node
        
        Arguments:
            x {Integer} -- nodeId of the newly arrived node

        Returns:
            [Integer, list, list, list] --
                Num hops, Routing Tables, Leaf Set, Neighborhood Set
                (Returns the id if already exists)
        """
        global length
        # print("Running Node Arrival for key " + hex_code(x) + " on " +
        #       hex_code(self.get_num()))  # Debug
        # Send all routing tables, A's neighbourhood set and Z's leaf set to X
        routing_tables = []
        next_node = self.get_num()
        z_node_id = next_node

        num_times = 32
        while next_node != -1:
            # Add the routing table as many times as there are matching
            # new digits with the key
            l = common_prefix(hex_code(x), hex_code(next_node))
            node = (self.network_api.get_node(next_node))
            for i in range(l - len(routing_tables) + 1):
                routing_tables.append(node.get_routing_table())
            z_node_id = next_node
            next_node = node.route(x)
            if num_times == 0 or next_node == int(math.pow(16, length)):
                break
            num_times -= 1

        z_node = (self.network_api.get_node(z_node_id))
        if num_times == 0:
            return (32 - num_times), [], [], []
        if next_node == int(math.pow(16, length)):
            return (32 - num_times), [z_node.get_id()]

        leaf_set = z_node.get_leaf_set().copy()
        neighborhood_set = self.get_neighborhood_set().copy()

        # Send the routing table, leaf set and neighborhood set, including the
        # respective nodes.
        leaf_set.append(z_node.get_num())
        neighborhood_set.append(self.get_num())
        return (32 - num_times), routing_tables, leaf_set, neighborhood_set

    def node_update(self, x):
        """Update Routing Table, Leaf Set and Neighborhood Set when a new node
        is added to the network
        
        Arguments:
            x {Integer} -- Hash of the new node that has been added
        """
        global B
        # Add into routing table, at all levels where x can be added
        l = common_prefix(hex_code(x), hex_code(self.get_num()))
        hash_string = hex_code(x)[2:]
        for i in range(l):
            digit = hash_string[i]
            if self.routing_table[i][int(digit, 16)] == -1:
                self.routing_table[i][int(digit, 16)] = x
        # Definitely, add at the maximum level of match
        digit = hash_string[l]
        self.routing_table[l][int(digit, 16)] = x

        # Add into leaf set
        self.__merge_leaf_set([x])

        # Add into neighborhood set
        farthest = -1
        farthest_node = -1
        for node in self.neighborhood_set:
            distance = self.network_api.proximity(self.get_num(), node)
            if distance != -1 and (farthest < distance or farthest == -1):
                farthest = distance
                farthest_node = node
        # Replace the farthest node, if node is nearer and set is large enough
        if len(self.neighborhood_set) > math.pow(2, B + 1):
            x_distance = self.network_api.proximity(self.get_num(), x)
            if x_distance < farthest:
                self.neighborhood_set.remove(farthest_node)
        self.neighborhood_set.append(x)

    def join(self):
        """Implementation for expanding multicast search"""
        # Check till depth 500
        for depth in range(500):
            found_node = self.network_api.hop(self.get_num(), depth + 1)
            if found_node != -1:
                break

        if found_node != -1:
            a_node = (self.network_api.get_node(found_node))
            num_hops, r_t, l_s, n_s = a_node.node_arrival(self.get_num())
            it = self.node_init(r_t, l_s, n_s)
            list_it = list(set(it))
            for node_id in list_it:
                node = (self.network_api.get_node(node_id))
                node.node_update(self.get_num())
        print('Added node: ', end='')
        print(self)
        print('=============================================================')

    def search(self, key):
        """Searches the Pastry DHT for the key
        
        Arguments:
            key {Integer} -- Node that is to be searched
        
        Returns:
            [Integer, Integer] -- Num hops, Node Id of the node if present,
                                  else -1
        """
        global length
        name = str(key)
        m = hashlib.sha1(name.encode('utf-8'))
        key_hash = m.hexdigest()[:length]
        r = self.node_arrival(int(key_hash, 16))
        if len(r) == 2:
            return r[0], r[1]
        else:
            return r[0], -1
