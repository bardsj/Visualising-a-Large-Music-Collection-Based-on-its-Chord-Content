from collections import namedtuple

Transaction = namedtuple('Transaction',['tid','items'])
UtilListItem = namedtuple('UtilListItem',['tid','iutil','rutil'])

class FHM:
    """
        Implementation of the FHM high utility frequent itemset mining algorithm:

        "Fournier-Viger, P., Wu, C.-W., Zida, S., Tseng, V. S.: FHM: Faster high-utility
        itemset mining using estimated utility co-occurrence pruning. In: Proc. 21st Intern.
        Symp. on Methodologies for Intell. Syst., pp. 83{92 (2014)"

        Parameters
        ----------
        transactions : list
            List of transaction tuples in the form (tid,t_items) where tid is the transaction id and
            t_items is a list of items in the form of a key/value pair of (label,frequency)
            e.g. [(1, [("a",4),("b",3)] ), (2, [("c",2)] ), (3, [("a",4),("e",6)] ) ... ]
        eutil : dict
            External utilities for items (i.e. unit profit) e.g. {"a":4.5,"b":0.99 ...}
        minutil : float
            The utlity threshold expressed as a percentage of the total db utility
        
        Attributes
        ----------
        total_db_util : float
            The total utility of all transactions
        hui_list : list
            The calculated high utility frequent itemsets
        util_lists : dict
            The utility lists for each itemset
        TWU_list : list
            The transaction weighted utility list for each item
        order : dict
            The ordering of the TWU list by ascending value
        minutil_pc (optional, default = True) : bool
            Use the actual utility value threshold (false) or set the threshold as a 
            percentage of the total database utilities

    """
    def __init__(self,transactions,eutil,minutil,minutil_pc=True):
        self.transactions = [Transaction(t[0],t[1]) for t in transactions]
        self.eutil = eutil
        self.total_db_util = self._totalDBUtility()
        # Check if real or percentage minutil specified and set minutil val accordingly
        self.minutil_pc = minutil_pc
        if minutil_pc:
            self.minutil = minutil*self.total_db_util
        else:
            self.minutil = minutil
        self.hui_list = []
        self.util_lists = {}
        self.TWU_list = sorted([(x,self._TWU([x])) for x in self.eutil.keys()],key=lambda x: x[1])
        self.order = {x[0]:i for i,x in enumerate(self.TWU_list)}


    def _totalDBUtility(self):
        """
            Calculate the total DB utility

            Parameters
            ----------
            T : list
                List of all trasactions
            
            Returns
            -------
            float
                The total utility for the database
        """
        return sum([sum([self.eutil[x[0]]*x[1] for x in t.items]) for t in self.transactions])


    def _TU(self,t):
        """
            Calculate the individual transaction utility

            Parameters
            ----------
            t : Transaction
                Transaction as named tuple
            
            Returns
            -------
            float
                The utility total for a transaction
        """
        return sum(sorted([self.eutil[x[0]]*x[1] for x in t.items],reverse=True))

    def _TWU(self,x):
        """
            Calculate the TWU for item x in transactions
            
            Parameters
            ----------
            x : set
                Itemset to calculate
            
            Returns
            -------
            float
                Transaction weighted utilization
        """
        t_subset = list(filter(lambda t: set(x).issubset([j[0] for j in t.items]),self.transactions))
        return sum([self._TU(x) for x in t_subset])


    def _utilListItem(self,t,x):
        """
            Calculate the utility list tuple for a transaction (t)/set (x) pair

            Paramters
            ---------
            t : Transaction
                Single transaction as named tuple
            x : set
                Itemset of interest
            
            Returns
            -------
            utilListItem
                Single row of utility list in form (tid,iutil,rutil)
        """
        iutil = sum([self.eutil[j[0]]*j[1] for j in filter(lambda i: i[0] in x,t.items)])
        rutil_list = [x[0] for x in self.TWU_list]
        ix = max([rutil_list.index(j) for j in x])
        rutil_list = rutil_list[ix:]
        rutil = sum([self.eutil[j[0]]*j[1] for j in filter(lambda i: (i[0] not in x) and (i[0] in rutil_list),t.items)])
        return UtilListItem(t.tid,iutil,rutil)

    def _createUtilList(self,x):
        """
            Create utility list for itemset x from transactions T

            Parameters
            ----------
            x : set
                Itemset to calculate

            Returns
            -------
            dict
                Utility list for itemset x with key value set to transaction id
        """
        return {t.tid:self._utilListItem(t,x) for t in filter(lambda i: set(x).issubset([j[0] for j in i.items]),self.transactions)}


    def _FHM_construct(self,P,Px,Py):
        """
            Construct algorithm for joining utility lists for Px and Py to 
            generate utility list for Pxy
        """
        Pxy_util_list = {}
        for ex in self.util_lists[frozenset(Px)].values():
            # Search for matching key, set to none if not present
            try:
                ey = self.util_lists[frozenset([Py])][ex.tid]
            except:
                ey = None
            if ey:
                if P:
                    e = self.util_lists[frozenset(P)][ex.tid]
                    exy = UtilListItem(ex.tid,ex.iutil+ey.iutil-e.iutil,ey.rutil)
                else:
                    exy = UtilListItem(ex.tid,ex.iutil+ey.iutil,ey.rutil)
                Pxy_util_list[exy.tid] = exy

        return Pxy_util_list


    def _FHM_search(self,P,extensionsOfP,EUCS):
        """
            Recursive search algorithm for high utility itemsets
        """
        for Px in extensionsOfP:
            utility_list_px = self.util_lists[frozenset(Px)]
            Px_iutils = [x.iutil for x in utility_list_px.values()]
            Px_rutils = [x.rutil for x in utility_list_px.values()]

            if sum(Px_iutils) >= self.minutil:
                # Return as pc value or actual value
                if self.minutil_pc:
                    self.hui_list.append((Px,sum(Px_iutils)/self.total_db_util))
                else:
                    self.hui_list.append((Px,sum(Px_iutils)))

            if sum(Px_iutils) + sum(Px_rutils) >= self.minutil:
                Py_list = [x[-1] for x in extensionsOfP]
                Py_list = sorted(Py_list,key=lambda x: self.order[x])
                Py_list.remove(Px[-1])
                extensionsOfPx = []
                for Py in Py_list[self.order[Px[-1]]:]:
                    if EUCS[Px[-1]][Py] >= self.minutil:
                        Pxy = Px + [Py]
                        self.util_lists[frozenset(Pxy)] = self._FHM_construct(P,Px,Py)
                        extensionsOfPx.append(list(Pxy))

                self._FHM_search(Px,extensionsOfPx,EUCS)


    def run_FHM(self):
        """
            Run the FHM algorithm

            Returns
            -------
            hui_list : list
                List of high utility frequent itemsets with associated utility values
        """
        # Scan D to create a list of utliity lists for each item
        for x in self.TWU_list:
            self.util_lists[frozenset([x[0]])] = self._createUtilList([x[0]])
        # Create EUCS structure as dict of dicts
        EUCS = {k:{j:self._TWU([k,j]) for j in self.eutil.keys() if j != k} for k in self.eutil.keys()}
        # Start recursive search with empty set and list of extensions
        self._FHM_search([],[[x[0]]for x in self.TWU_list],EUCS)
        return self.hui_list
