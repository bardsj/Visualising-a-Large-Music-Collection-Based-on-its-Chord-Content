import numpy as np
from itertools import chain

class AVSDF:
    """
    Implementation of the AVSDF (Adjacent Vertex with Smallest Degree First) algorithm with local adjusting as proposed in:
    
        "He, H. & Sykora, O., 2009. New circular drawing algorithms. [Online] Available at: https://repository.lboro.ac.uk/articles/New_circular_drawing_algorithms/9403790"
    """

    def __init__(self,edge_list,local_adjusting=False):
        self.edge_list = edge_list
        self.nodes = np.unique(np.array(edge_list))
        self.nodes_degree = np.array([self._degree(n) for n in self.nodes])
        self.nodes = self.nodes[self.nodes_degree.argsort()]
        self.order = []
        self.local_adjusting = local_adjusting


    def _degree(self,node):
        """
            Return number of edges containing each vertex (i.e. the degree)
        """
        # Get degree of vertex/node
        return len(self._adjacent_vertices(node))


    def _adjacent_vertices(self,v):
        """
            Return filtered list of edges containing vertex v
        """
        # Filter edge list for edges that contain v
        edges = list(filter(lambda x: v in x, self.edge_list))
        # Get adjacent vertices with v
        #edge_set = set(chain(*edges))
        #edge_set.remove(v)
        return list(edges)


    def _count_all_crossings(self,order,edge_list):
        """
            Count total number of crossings
        """
        # Map of index values in order for items
        ix_map = {x:i for i,x in enumerate(order)}
        #edge_list_sorted = sorted(edge_list,key=lambda x: ix_map[x[0]])

        edge_mat = np.zeros((len(edge_list),len(edge_list)))

        for i,edge in enumerate(edge_list):
            edge_s = sorted([ix_map[edge[0]],ix_map[edge[1]]])
            for j,comp in enumerate(edge_list):
                comp_s = sorted([ix_map[comp[0]],ix_map[comp[1]]])
                # If any edges share a vertices they cannot cross
                if (edge_s[0] in comp_s) or (edge_s[1] in comp_s):
                    pass
                # If one edge vertex ix falls between the other edge vertices and the other does not then they must cross
                elif (edge_s[0] < comp_s[0] < edge_s[1]) and not (edge_s[0] < comp_s[1] < edge_s[1]) or \
                    (edge_s[0] < comp_s[1] < edge_s[1]) and not (edge_s[0] < comp_s[0] < edge_s[1]):
                    edge_mat[i][j] = 1
        # Return upper triangle of matrix (no duplicate crossing counts)
        return np.triu(edge_mat).sum()
        

    def _count_crossings_edge(self,order,edge_list,edge):
        """
            Count number of crossings for a particular edge
        """
        # Map of index values in order for items
        ix_map = {x:i for i,x in enumerate(order)}

        #edge_list_sorted = sorted(edge_list,key=lambda x: ix_map[x[0]])
        edge_mat = np.zeros(len(edge_list))

        edge_s = sorted([ix_map[edge[0]],ix_map[edge[1]]])
        for j,comp in enumerate(edge_list):
            comp_s = sorted([ix_map[comp[0]],ix_map[comp[1]]])
            # If any edges share a vertices they cannot cross
            if (edge_s[0] in comp_s) or (edge_s[1] in comp_s):
                pass
            # If one edge vertex ix falls between the other edge vertices and the other does not then they must cross
            elif (edge_s[0] < comp_s[0] < edge_s[1]) and not (edge_s[0] < comp_s[1] < edge_s[1]) or \
                (edge_s[0] < comp_s[1] < edge_s[1]) and not (edge_s[0] < comp_s[0] < edge_s[1]):
                edge_mat[j] = 1
        # Return sum of crossings
        return edge_mat.sum()


    def _local_adjusting(self):
        """
            Run local adjusting algorithm
        """
        # For every vertex calculate the crossings on edges incident to them
        v_crossings = {}
        for vertex in self.nodes:
            v_crossings[vertex] = sum([self._count_crossings_edge(self.order,self.edge_list,e) for e in self._adjacent_vertices(vertex)])
        # Sort the vertices according to descending number of crossings
        v_crossings_sort = sorted(v_crossings,key=v_crossings.get,reverse=True)
        # Let variable, currentV, point to the vertex whose incident edges have the largest number of crossings.
        # for (all vertices) do
        for currentV in v_crossings_sort:
            # Get the positions of adjacent vertices of currentV into pList array.
            pList = list(np.unique(self._adjacent_vertices(currentV)))
            pList.remove(currentV)
            # Try all these positions and calculate the crossing number to find the best location for currentV
            crossNo = v_crossings[currentV]
            for newV in pList:
                # Original position index of currentV
                op_ix = self.order.index(currentV)
                # New position index of adjacent vertex
                np_ix = self.order.index(newV)
                # Swap places in order
                order_temp = self.order
                order_temp[op_ix] = newV
                order_temp[np_ix] = currentV
                # Calculate new no. edge crossings
                newCrossNo = sum([self._count_crossings_edge(order_temp,self.edge_list,e) for e in self._adjacent_vertices(currentV)])
                # If cross number is smaller then swap in order
                if newCrossNo < crossNo:
                    crossNo = newCrossNo
                    self.order[np_ix] = currentV
                    self.order[op_ix] = newV
    

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
                adjacent_v = list(np.unique(self._adjacent_vertices(v)))
                adjacent_v.remove(v)
                adjacent_degree = np.array([self._degree(n) for n in adjacent_v],dtype=int)
                adjacent_v = np.array(adjacent_v)[adjacent_degree.argsort()]

                for av in adjacent_v:
                    if av not in self.order:
                        #stack.insert(0,av)
                        stack.append(av)

        if self.local_adjusting:
            self._local_adjusting()

        return self.order