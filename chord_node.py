"""Class Definition for ChordNode"""
import math
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
            Integer -- Node Id of the next closest finger
        """
        global M
        for i in range(M, 0, -1):
            if circular_between(self.get_num(),
                                self.finger_table[i - 1]['node'], key):
                return self.finger_table[i - 1]['node']
        return self.get_num()

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
            return self.get_num()

        if circular_between(self.get_num(), key,
                            self.get_successor()) or key == self.get_successor(
                            ) or self.get_num() == self.get_successor():
            return self.get_successor(), 1
        else:
            node_id = self.closest_preceding_finger(key)
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
        for key in self.data_store:
            if circular_between(start, key, end) or key == end:
                new_dict[key] = self.data_store[key]
                del self.data_store[key]
        return new_dict

    def __move_keys(self):
        """Transfer keys from successor to current node"""
        successor = self.network_api.get_node(self.get_successor())
        fetch_dict = successor.fetch_keys(self.predecessor, self.get_num())
        for key in fetch_dict:
            self.data_store[key] = fetch_dict[key]

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

        # Fill up the remaining finger table
        for i in range(M - 1):
            if circular_between(self.get_num(),
                                self.finger_table[i + 1]['start'],
                                self.finger_table[i]['node']):
                self.finger_table[i + 1]['node'] = self.finger_table[i]['node']
            else:
                self.finger_table[i + 1]['node'], num_hops = n_dash.find_successor(
                    self.finger_table[i + 1]['start'])

    def __update_finger_table(self, x, i):
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
            predecessor.__update_finger_table(x, i)

    def __update_others(self):
        """Update all nodes of the join of current node"""
        global M
        for i in range(M):
            # The node whose ith finger might be the current node
            prev_id = circular_difference(self.get_num(), int(math.pow(2, i)))
            if self.network_api.is_alive(prev_id):
                prev_node = self.network_api.get_node(prev_id)
                prev_node.__update_finger_table(self.get_num(), i)
            p = self.find_predecessor(prev_id)
            p_node = self.network_api.get_node(p)
            p_node.__update_finger_table(self.get_num(), i)

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
            self.__move_keys()
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
        best_node, num_hops = self.find_successor(key)
        # Check if best_node has key or not
        node = self.network_api.get_node(best_node)
        if key in node.data_store:
            return num_hops, node.data_store[key]
        return num_hops, -1
