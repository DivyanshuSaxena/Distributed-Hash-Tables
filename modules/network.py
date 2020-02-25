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
        dict[key].append(val)
    else:
        dict[key] = [val]


class Node:
    """Implementation for Base Class of the Node"""
    def __init__(self):
        self.ip_addr = [10, 10, 0, 0]  # Default ip addr

    def get_num(self):
        return ''.join(self.ip_addr)

    def set_ip(self, ip_addr):
        """        
        Arguments:
            ip_addr {array[4]} -- ip address of the node as array of 4 integers
        """
        self.ip_addr = ip_addr


class Network:
    """Implementation of the network topology, using nodes and switches"""
    def __init__(self,
                 num_switches,
                 read_from_file=false,
                 file_name='links.dat'):
        """Initialize the network nodes and switches
        
        Arguments:
            num_nodes {Integer} -- Number of nodes in the network

        Keyword Arguments:
            read_from_file {boolean} -- whether to read the network connections
                                        from given file (default: {false})
            file_name {str} -- file from which network connections are to be
                                        read (default: {'links.dat'})
        """
        self.num_nodes = 0
        self.num_switches = num_switches  # Switches have ids 1,2,....,<num_switches>

        links = []
        if read_from_file:
            # Read network connections from file, if required
            with open(file_name) as f:
                conn = f.readlines()
            links = [[int(x) for x in x.trim().split(',')] for x in conn]
        else:
            # Create a ring of links and then generate random remaining links
            max_links = random.randrange(num_switches + 1, 2 * num_switches)
            for i in range(num_switches - 1):
                links.append([i + 1, (i + 2) % num_switches])
            for link in range(max_links - num_nodes + 1):
                src = random.randint(1, num_nodes)
                dest = src
                while dest == src:
                    dest = random.randint(1, num_nodes)
                links.append([src, dest])

            # Save the links in the given file
            with open(file_name) as f:
                for link in self.links:
                    f.write(link[0] + ',' + link[1] + '\n')

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
        """
        switch = random.randint(1, self.num_switches)
        while switch in self.switch_to_node.values():
            switch = random.randint(1, self.num_switches)
        self.switch_to_node[n.get_num()] = switch

    def proximity(self, n1, n2):
        """Define the proximity metric between two Node instances on the network
        
        Currently using the modulo additive inverse for the metric
        
        Arguments:
            n1 {Node}
            n2 {Node}

        Returns:
            Integer -- the proximity metric
        """
        s1 = self.switch_to_node[n1.get_num()]
        s2 = self.switch_to_node[n2.get_num()]
        return abs(s2 - s1)
