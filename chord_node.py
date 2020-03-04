"""Class Definition for ChordNode"""
import math
import hashlib
from modules.network import Node

M = 0


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


def circular_difference(num1, num2):
    """Cicrular Difference on ring: num1 - num2
    
    Arguments:
        num1 {Integer}
        num2 {Integer}
    
    Returns:
        Integer -- Circular Difference
    """
    global M
    if num1 > num2:
        return num1 - num2
    else:
        return int(math.pow(2, M)) + num1 - num2


def hash_key(integer):
    """Hash the given integers and trim to l digits
    
    Arguments:
        integer {Integer}
    
    Returns:
        Integer -- Hashed Integer Value
    """
    name = str(integer)
    m = hashlib.sha1(name.encode('utf-8'))
    key_hash = m.hexdigest()[:M // 4]
    return int(key_hash, 16)


# Each entry of the finger table is a tuple of two as follows:
#
# X------------------X-----------------X
# |   Finger Start   |   Finger Node   |
# X------------------X-----------------X
#
# Where the finger is from [Start, End) and stored at Node
class ChordNode(Node):
    """Implementation Class for ChordNode, a single node instance, 
       running the Chord Protocol"""
    def __init__(self, node_id, node_hash, network, m):
        global M
        super().__init__(node_id, node_hash, network)

        M = m
        self.finger_table = []
        for i in range(m):
            fi_start = int((self.get_num() + math.pow(2, i)) % math.pow(2, M))
            entry = {'start': fi_start, 'node': 0}
            self.finger_table.append(entry)

        self.predecessor = -1
        self.data_store = {}

    def __str__(self):
        """Print the ChordNode Object"""
        print('ChordNode: ' + str(self.get_num()))
        print(self.predecessor, self.get_successor())
        for entry in self.finger_table:
            print(str(entry['start']) + '\t|\t' + str(entry['node']))
        return ''

    def get_successor(self):
        """Sends the successor of the node to whoever wants it
        
        Returns:
            Integer -- Node Id of the successor
        """
        return self.finger_table[0]['node']

    def get_predecessor(self):
        """Sends the predecessor of the node to whoever wants it
        
        Returns:
            Integer -- Node Id of the predecessor
        """
        return self.predecessor

    def set_successor(self, node):
        """Set node as the successor of the current node
        
        Arguments:
            node {Integer} -- Node id of the new successor
        """
        self.finger_table[0]['node'] = node

    def set_predecessor(self, node):
        """Set node as the predecessor of the current node
        
        Arguments:
            node {Integer} -- Node id of the new predecessor
        """
        self.predecessor = node

    def closest_preceding_finger(self, key):
        """Find the closest preceding finger from node n to the key
        
        Arguments:
            key {Integer} -- Key to be searched
        
        Returns:
            Integer, Integer -- Node Id of the next closest finger,
                                the entry in the finger table
        """
        global M
        for i in range(M, 0, -1):
            if circular_between(self.get_num(),
                                self.finger_table[i - 1]['node'], key):
                return self.finger_table[i - 1]['node'], i - 1
        return self.get_num(), 0

    def find_predecessor(self, key):
        """Find the predecessor of key, as per information with current node
        
        Arguments:
            key {Integer} -- Key whose predecessor is to be found
        
        Returns:
            Integer -- Node Id of the predecessor node
        """
        # Return the predecessor of the node itself when the key is on the node
        # print('Finding predecessor for ' + str(key) + ' at ' +
        #       str(self.get_num()))  # Debug
        if self.get_num() == key:
            return self.predecessor

        key_successor, num_hops = self.find_successor(key)
        n_dash = self.network_api.get_node(key_successor)
        return n_dash.get_predecessor()

    def find_successor(self, key):
        """Find the successor of the key, as per information with current node
        
        Arguments:
            key {Integer} -- Key whose successor is to be found
        
        Returns:
            Integer, Integer -- Node Id of the successor node, Num hops
        """
        # Return the node itself when the key is on the node
        # print('Finding successor for ' + str(key) + ' at ' +
        #       str(self.get_num()))  # Debug
        if self.get_num() == key:
            return self.get_num(), 0

        if circular_between(self.get_num(), key,
                            self.get_successor()) or key == self.get_successor(
                            ) or self.get_num() == self.get_successor():
            return self.get_successor(), 1
        else:
            node_id, i = self.closest_preceding_finger(key)
            i_orig = i
            while not self.network_api.is_alive(node_id):
                node_id, i = self.closest_preceding_finger(node_id - 1)

            # Update the node in the finger table from i_orig to i
            for index in range(i_orig, i + 1):
                self.finger_table[index]['node'] = node_id
            n_dash = self.network_api.get_node(node_id)
            succ, hops = n_dash.find_successor(key)
            return succ, (hops + 1)

    def fetch_keys(self, start, end):
        """Send key-value pair requested by other node
        
        Arguments:
            start {Integer} -- start id
            end {Integer} -- end id
        
        Returns:
            Dict -- Dictionary of key-value pairs to be transferred
        """
        new_dict = {}
        for key in list(self.data_store):
            if circular_between(start, key, end) or key == end:
                new_dict[key] = self.data_store[key]
                del self.data_store[key]
        return new_dict

    def __init_finger_table(self, node_id):
        """Initialize finger table for a node which has just joined
        
        Arguments:
            node_id {Integer} -- The node whose help is being taken to join
        """
        global M
        n_dash = self.network_api.get_node(node_id)

        # Initialize first entry and successor
        self.finger_table[0]['node'], num_hops = n_dash.find_successor(
            self.finger_table[0]['start'])

        # Update successor and predecessor links
        successor = self.network_api.get_node(self.get_successor())
        self.predecessor = successor.get_predecessor()
        predecessor = self.network_api.get_node(self.get_predecessor())
        predecessor.set_successor(self.get_num())
        successor.set_predecessor(self.get_num())

        # Update the finger table using node n_dash
        self.fill_finger_table(node_id)

    def fill_finger_table(self, node_id):
        """
        Update finger table of the current node based on finger table of node_id
        
        Arguments:
            node_id {Integer} -- Node Id of the node whose finger table is to 
            be taken as a reference
        """
        global M
        n_dash = self.network_api.get_node(node_id)

        # Fill up the finger table
        for i in range(M - 1):
            if circular_between(self.get_num(),
                                self.finger_table[i + 1]['start'],
                                self.finger_table[i]['node']):
                self.finger_table[i + 1]['node'] = self.finger_table[i]['node']
            else:
                self.finger_table[i +
                                  1]['node'], num_hops = n_dash.find_successor(
                                      self.finger_table[i + 1]['start'])

    def update_finger_table(self, x, i):
        """Update finger table of the current node when a new node x has arrived
        
        Arguments:
            x {Integer} -- Node id of the new node which has joined
            i {Integer} -- Update ith finger
        """
        # print('Updating node: ' + str(self.get_num()) + ' at position ' +
        #       str(i))  # Debug
        if circular_between(self.finger_table[i]['start'], x,
                            self.finger_table[i]
                            ['node']) or self.finger_table[i]['start'] == x:
            self.finger_table[i]['node'] = x
            predecessor = self.network_api.get_node(self.predecessor)
            predecessor.update_finger_table(x, i)

    def __update_others(self):
        """Update all nodes of the join of current node"""
        global M
        for i in range(M):
            # The node whose ith finger might be the current node
            prev_id = circular_difference(self.get_num(), int(math.pow(2, i)))
            if self.network_api.is_alive(prev_id):
                prev_node = self.network_api.get_node(prev_id)
                prev_node.update_finger_table(self.get_num(), i)
            p = self.find_predecessor(prev_id)
            p_node = self.network_api.get_node(p)
            p_node.update_finger_table(self.get_num(), i)

    def notify(self):
        """Transfer keys from the predecessor to the current node"""
        predecessor = self.network_api.get_node(self.get_predecessor())
        fetch_dict = predecessor.fetch_keys(predecessor.get_predecessor(),
                                            predecessor.get_num())
        for key in fetch_dict:
            self.data_store[key] = fetch_dict[key]

    def depart_network(self):
        """Run method when departing from the network"""
        # Notify successor of departure -- Successor shall transfer the
        # requisite keys
        print('Deleting node: ')
        print(self)
        successor = self.network_api.get_node(self.get_successor())
        successor.notify()

        # Update Predecessor and Successor links
        predecessor = self.network_api.get_node(self.get_predecessor())
        predecessor.set_successor(self.get_successor())
        successor.set_predecessor(self.get_predecessor())

        # Update finger tables of predecessor and successor
        predecessor.fill_finger_table(successor.get_num())
        successor.fill_finger_table(predecessor.get_num())

        # Finally: Depart from network
        return self.network_api.remove_node(self.get_num())

    def join(self):
        """Run when a new node joins the network"""
        global M
        # Discover node through which, can enter the Chord Network
        # Implementation for expanding multicast search - Check till depth 500
        for depth in range(500):
            found_node = self.network_api.hop(self.get_num(), depth + 1)
            if found_node != -1:
                break

        if found_node != -1:
            # Some node has been found
            self.__init_finger_table(found_node)
            self.__update_others()

            # Move keys (predecessor,n] from successor to current node
            successor = self.network_api.get_node(self.get_successor())
            fetch_dict = successor.fetch_keys(self.predecessor, self.get_num())
            for key in fetch_dict:
                self.data_store[key] = fetch_dict[key]
        else:
            # This is the first node in the network
            for i in range(M):
                self.finger_table[i]['node'] = self.get_num()
            self.predecessor = self.get_num()
        print(self)

    def search(self, key):
        """Searches the Chord DHT for the key
        
        Arguments:
            key {Integer} -- Key to be searched
        
        Returns:
            Integer, Integer -- Num hops, Value of the key if present, else -1
        """
        store_key = hash_key(key)
        best_node, num_hops = self.find_successor(store_key)
        # Check if best_node has store_key or not
        node = self.network_api.get_node(best_node)
        if store_key in node.data_store:
            return num_hops, node.data_store[store_key]
        return num_hops, -1

    def store_key(self, key, val):
        """Stores the (key, value) pair at the requisite node on the network
        
        Arguments:
            key {Integer} -- Key Value
            val {Integer} -- Value
        
        Returns:
            Integer -- Returns -1 if key couldn't be stored, else returns 0
        """
        stored_key = hash_key(key)
        key_node, num_hops = self.find_successor(stored_key)
        node = self.network_api.get_node(key_node)
        if stored_key in node.data_store:
            return -1
        node.data_store[stored_key] = val
        return 0
