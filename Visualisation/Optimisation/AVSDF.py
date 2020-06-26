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
        self.nodes_degree = np.array([self._degree(n) for n in self.nodes])
        self.nodes = self.nodes[self.nodes_degree.argsort()]
        self.order = []

    def _degree(self,node):
    # Get degree of vertex/node
        return sum([node in edge for edge in self.edge_list])

    def _adjacent_vertices(self,v):
        # Filter edge list for edges that contain v
        edges = list(filter(lambda x: v in x, self.edge_list))
        # Get adjacent vertices with v
        edge_set = set(chain(*edges))
        edge_set.remove(v)
        return list(edge_set)

    def _count_crossings_edge(self,v,order):
        n_crossings = 0
        edge_cross_list = []
        v_edge_list = [e for e in self.edge_list if v in e]
        for edge in v_edge_list:
            for c_edge in self.edge_list:
                c_edge = sorted(c_edge)
                edge = sorted(edge)

                e_ix = list(order).index(edge[0])
                order_tmp = order[e_ix:] + order[:e_ix]
                e_ix2 = order_tmp.index(edge[1])

                if order_tmp.index(c_edge[0]) < e_ix2 and order_tmp.index(c_edge[1]) > e_ix2:
                    if edge[0] not in c_edge and edge[1] not in c_edge:
                        cross_sort = sorted([edge,c_edge])
                        if cross_sort not in edge_cross_list:
                            n_crossings += 1
                            edge_cross_list.append(cross_sort)
        
        return n_crossings
        
    def _local_adjusting(self):
        edge_crossings = sorted([(e,self._count_crossings_edge(e,self.order)) for e in self.nodes],key=lambda x: x[1])[::-1]
        for edge in edge_crossings:
            min_cross = edge[1]
            pList = self._adjacent_vertices(edge[0])
            cross_res = []
            for p in pList:
                ix_old = list(self.order).index(edge[0])
                ix_swap = list(self.order).index(p)
                local_order = self.order
                local_order[ix_old] = p
                local_order[ix_swap] = edge[0]
                cross_res.append(self._count_crossings_edge(edge[0],local_order))
            
            if min(cross_res) < edge[1]:
                swap_ix = np.argmin(cross_res)
                ix_old = list(self.order).index(edge[0])
                ix_swap = list(self.order).index(pList[swap_ix])
                self.order[ix_old] = pList[swap_ix]
                self.order[ix_swap] = edge[0]
                

    
    def run_AVSDF(self):
        # Initialise an array order[n], and a stack, S.
        #order = np.empty(len(nodes),dtype=str)
        stack = []

        # Get the vertex with the smallest degree from the given graph, and push it into S
        stack.append(self.nodes[np.argmin(self.nodes_degree)])

        # while (S is not empty) do
        while(len(stack)>0):
            # Pop a vertex v, from S
            v = stack.pop()
            # if (v is not in order) then
            if v not in self.order:
                # Append the vertex v into order
                self.order.append(v)

                # Get all adjacent vertices of v; and push those vertices, which are not in order
                # into S with descending degree towards the top of the stack (the vertex with
                # smallest degree is at top of S).
                adjacent_v = np.array(self._adjacent_vertices(v))
                adjacent_degree = np.array([self._degree(n) for n in adjacent_v])

                adjacent_v = adjacent_v[adjacent_degree.argsort()]

                for av in adjacent_v:
                    if av not in self.order:
                        #stack.insert(0,av)
                        stack.append(av)

        self._local_adjusting()

        return self.order