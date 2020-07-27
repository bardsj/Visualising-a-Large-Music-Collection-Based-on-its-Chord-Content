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
        return len(self._adjacent_edges(node))

    def _adjacent_vertices(self,v):
        av = list(set(chain(*self._adjacent_edges(v))))
        return av

    def _adjacent_edges(self,v):
        """
            Return filtered list of edges containing vertex v
        """
        # Filter edge list for edges that contain v
        edges = list(filter(lambda x: v in x, self.edge_list))
        # Get adjacent vertices with v
        #edge_set = set(chain(*edges))
        #edge_set.remove(v)
        return edges


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
            for j,comp in enumerate(edge_list[i:]):
                comp_s = sorted([ix_map[comp[0]],ix_map[comp[1]]])
                # If any edges share a vertices they cannot cross
                if (edge_s[0] in comp_s) or (edge_s[1] in comp_s):
                    pass
                # If one edge vertex ix falls between the other edge vertices and the other does not then they must cross
                elif (edge_s[0] < comp_s[0] < edge_s[1]) and not (edge_s[0] < comp_s[1] < edge_s[1]) or \
                    (edge_s[0] < comp_s[1] < edge_s[1]) and not (edge_s[0] < comp_s[0] < edge_s[1]):
                    edge_mat[i][j] = 1
        # Return upper triangle of matrix (no duplicate crossing counts)
        return (edge_mat).sum()
        

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
        crossNo = []
        # For every vertex calculate the crossings on edges incident to them
        incident_crossings = []
        for node in self.nodes:
            sum_incident_crossings = sum([self._count_crossings_edge(self.order,self.edge_list,e) for e in filter(lambda x: node in x,self.edge_list)])
            incident_crossings.append([node,sum_incident_crossings])
        # Sort the vertices according to descending number of crossings. Let variable, currentV,
        # point to the vertex whose incident edges have the largest number of crossings.
        vertices_desc_crossings = [x[0] for x in sorted(incident_crossings,key=lambda x: x[1],reverse=True)]
        # for (all vertices) do
        for currentV in vertices_desc_crossings:
            # Get current number of crossings
            cross_no = self._count_all_crossings(self.order,self.edge_list)
            old_ix_edge_cross_no = sum([self._count_crossings_edge(self.order,self.edge_list,v) for v in self._adjacent_edges(currentV)])
            # Index of current v in order
            ix_old = self.order.index(currentV)
            # Get the positions of adjacent vertices of currentV into pList array.
            pList = self._adjacent_vertices(currentV)  
            opt_order = self.order.copy()     
            for p in pList:
                temp_order = self.order.copy()
                ix_new = self.order.index(p)
                temp_order[ix_new] = currentV
                temp_order[ix_old] = p
                new_ix_edge_cross_no = sum([self._count_crossings_edge(temp_order,self.edge_list,v) for v in self._adjacent_edges(currentV)])
                if (cross_no - old_ix_edge_cross_no + new_ix_edge_cross_no) < cross_no:
                    opt_order = temp_order.copy()
            
            self.order = opt_order.copy()
                


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