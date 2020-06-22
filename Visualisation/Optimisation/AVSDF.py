import numpy as np
from itertools import chain

class AVSDF:
    """
    Implementation of the AVSDF (Adjacent Vertex with Smallest Degree First) algorithm as proposed in:
    
        "He, H. & Sykora, O., 2009. New circular drawing algorithms. [Online] Available at: https://repository.lboro.ac.uk/articles/New_circular_drawing_algorithms/9403790"
    """

    def __init__(self,edge_list):
        self.edge_list = edge_list
        self.nodes = np.unique(np.array(edge_list))
        self.nodes_degree = np.array([self._degree(n,edge_list) for n in self.nodes])
        self.nodes = self.nodes[self.nodes_degree.argsort()]

    def _degree(self,node,edge_list):
    # Get degree of vertex/node
        return sum([node in edge for edge in edge_list])

    def _adjacent_vertices(self,v,edge_list):
        # Filter edge list for edges that contain v
        edges = list(filter(lambda x: v in x, edge_list))
        # Get adjacent vertices with v
        edge_set = set(chain(*edges))
        edge_set.remove(v)
        return list(edge_set)
        
    def run_AVSDF(self):
        # Initialise an array order[n], and a stack, S.
        #order = np.empty(len(nodes),dtype=str)
        order = []
        stack = []

        # Get the vertex with the smallest degree from the given graph, and push it into S
        stack.append(self.nodes[np.argmin(self.nodes_degree)])

        # while (S is not empty) do
        while(len(stack)>0):
            # Pop a vertex v, from S
            v = stack.pop()
            # if (v is not in order) then
            if v not in order:
                # Append the vertex v into order
                order.append(v)

                # Get all adjacent vertices of v; and push those vertices, which are not in order
                # into S with descending degree towards the top of the stack (the vertex with
                # smallest degree is at top of S).
                adjacent_v = np.array(self._adjacent_vertices(v,self.edge_list))
                adjacent_degree = np.array([self._degree(n,self.edge_list) for n in adjacent_v])

                adjacent_v = adjacent_v[adjacent_degree.argsort()]

                for av in adjacent_v:
                    if av not in order:
                        #stack.insert(0,av)
                        stack.append(av)

        return order