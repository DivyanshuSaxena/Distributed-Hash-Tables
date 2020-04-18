# Distributed Hash Tables

Implementation of the Pastry ([paper](http://rowstron.azurewebsites.net/PAST/pastry.pdf)) and Chord ([paper](https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf)) DHT Protocols, as part of assignment for course [COL819 - Spring 2020](http://www.cse.iitd.ac.in/~srsarangi/courses/2020/col_819_2020/index.html) at IIT Delhi.

## Repository Structure
.  
├── chord_node.py  
├── chord.py  
├── LICENSE  
├── links.dat  
├── modules  
│   ├── __ init__.py  
│   └── network.py  
├── pastry_node.py  
├── pastry.py  
└── README.md  

For further details, check the docstring in each of the python files.

## How to run

### Pastry Object Location Service

```bash
python pastry.py <num-nodes-in-network> <whether-to-read-network-configuration-from-file (0/1)>
```

#### Parameters
The default parameters are as follows:
```
l = 6  # Length of hash code
b = 4  # Parameter to set Leaf Set and Neighborhood Set
num_points = 10000  # Number of data points in Pastry
num_queries = 1000000  # Number of queries made
```
To change the parameters, go to [pastry.py](https://github.com/DivyanshuSaxena/Distributed-Hash-Tables/blob/master/pastry.py#L23)

### Chord Peer to Peer DHT

```bash
python chord.py <num-nodes-in-network> <whether-to-read-network-configuration-from-file (0/1)>
```

#### Parameters
The default parameters are as follows:
```
l = 6  # Hashing scheme for Nodes (Not required for Chord DHT, but to verify correctness)
m = 24  # Number of entries in Finger Table
num_points = 10000   # Number of data points to store in Chord
num_queries = 1000000  # Number of queries made on the DHT
```
To change the parameters, go to [chord.py](https://github.com/DivyanshuSaxena/Distributed-Hash-Tables/blob/master/chord.py#L23)

## Network Simulation

Both of the services, Pastry and Chord are implemented, using an underlying network simulation, with a definite measure  of geographical distance (or proximity metric) between the nodes. The Network has been simulated by keeping **a graph of interconnected vertices**. Each vertex may logically correspond to a Pastry/Chord Node. The physical distance between two Pastry/Chord Nodes is hence kept as the distance between the corresponding vertices in the network graph.

At each run, a new Network is initiated and the links (or edges) are stored in a file `links.dat`. The network configuration can be read from this file in a subsequent run, by specifying the respective argument. See the section [How to run](#how-to-run).

The `Network` class implemention and code can be found in the `modules.network` script. The Network Class utilizes the `Node` class definition, which is the base class for the `PastryNode` and `ChordNode` classes, used in Pastry and Chord respectively.

The `Network` instance has been used for three major functions:
```python
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
        # ... Code to get the distance between the associated logical vertices in the graph
        return distance
    except:
        return -1
```

## Contributing

Feel free to fork, make your changes and submit a pull request on this repo.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
