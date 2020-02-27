"""Network Simulation Implementation"""
import random


def add_to_dict(dict, key, val):
    """Function to add key-value to a dictionary
    
    Arguments:
        dict {Dict}
        key {Any Type}
        val {Any Type}
    """
    if key in dict.keys():
        if val not in dict[key]:
            dict[key].append(val)
    else:
        dict[key] = [val]


class Node:
    """Implementation for Base Class of the Node"""
    def __init__(self, node_hash):
        """        
        Arguments:
            node_hash {String} -- Hash of the node id
        """
        self.hash = node_hash  # Default ip addr

    def get_num(self):
        """        
        Returns:
            Integer -- Hash of the node id
        """
        return int(self.hash, 16)


class Network:
    """Implementation of the network topology, using nodes and switches"""
    def __init__(self,
                 num_switches,
                 read_from_file=False,
                 file_name='links.dat'):
        """Initialize the network nodes and switches
        
        Arguments:
            num_nodes {Integer} -- Number of nodes in the network

        Keyword Arguments:
            read_from_file {boolean} -- whether to read the network connections
                                        from given file (default: {False})
            file_name {str} -- file from which network connections are to be
                                        read (default: {'links.dat'})
        """
        self.num_nodes = 0
        self.nodes = {}

        # Switches have ids 1,2,....,<num_switches>
        self.num_switches = num_switches

        links = []
        if read_from_file:
            # Read network connections from file, if required
            with open(file_name) as f:
                conn = f.readlines()
            links = [[int(x) for x in x.strip().split(',')] for x in conn]
        else:
            # Create a ring of links and then generate random remaining links
            max_links = random.randrange(8 * num_switches, 16 * num_switches)
            for i in range(num_switches):
                links.append([i, (i + 1) % num_switches])
            for link in range(max_links - num_switches):
                src = random.randint(0, num_switches - 1)
                dest = src
                while dest == src:
                    dest = random.randint(0, num_switches - 1)
                links.append([src, dest])

            # Save the links in the given file
            with open(file_name, 'w') as f:
                for link in links:
                    f.write(str(link[0]) + ',' + str(link[1]) + '\n')

        # Generate dict of edges
        self.dict = {}
        for link in links:
            add_to_dict(self.dict, link[0], link[1])
            add_to_dict(self.dict, link[1], link[0])
        self.switch_to_node = {}

    def add_node(self, n):
        """Add a new Node to the Network
        
        Arguments:
            n {Node} -- Node instance to be added to the network
        
        Returns:
            Boolean -- Returns True if node could be added
        """
        if n.get_num() not in self.nodes:
            self.nodes[n.get_num()] = n
            switch = random.randint(0, self.num_switches - 1)
            while switch in self.switch_to_node.values():
                switch = random.randint(0, self.num_switches - 1)
            self.switch_to_node[n.get_num()] = switch
            return True
        return False

    def get_node(self, node_id):
        """Get the node at node id on the nodes array
        
        Arguments:
            node_id {Integer} -- Hash of the node
        
        Returns:
            Node -- Associated Node
        """
        return self.nodes[node_id]

    def is_alive(self, n):
        """Checks if a given node n is alive in the network
        
        Arguments:
            n {Integer} -- Node Id of the node
        
        Returns:
            Boolean -- True if node is alive else False
        """
        if n in self.nodes:
            return True
        return False

    def proximity(self, n1, n2):
        """Define the proximity metric between two Node instances on the network
        
        Currently using the modulo additive inverse for the metric
        
        Arguments:
            n1 {Integer} -- Hash of node n1
            n2 {Integer} -- Hash of node n2

        Returns:
            Integer -- the proximity metric (Returns -1 if node not alive)
        """
        try:
            s1 = self.switch_to_node[n1]
            s2 = self.switch_to_node[n2]
            return abs(s2 - s1)
        except:
            return -1

    def hop(self, node_id, max_depth):
        """Hops through the network upto depth max_depth
        
        Arguments:
            node_id {Integer} -- Node to start the hops from
            max_depth {Integer} -- Maximum depth upto which search is to be made
        
        Returns:
            Integer -- Node Id of the node at most max_depth hops away
        """
        switch = self.switch_to_node[node_id]

        # bfs query
        visited = {}
        queue = self.dict[switch]
        for _q in queue:
            visited[_q] = 1
        visited[switch] = 1
        found_switch = -1
        depth = 1
        while depth <= max_depth:
            next_queue = []
            for next_switch in queue:
                if next_switch in self.switch_to_node.values():
                    found_switch = next_switch
                    break
                _nq = self.dict[next_switch]
                for _sw in _nq:
                    if _sw not in visited:
                        next_queue.append(_sw)
                        visited[_sw] = 1
            if found_switch != -1:
                break
            depth += 1
            queue = next_queue
        if found_switch == -1:
            return -1
        return list(self.switch_to_node.keys())[list(
            self.switch_to_node.values()).index(found_switch)]
