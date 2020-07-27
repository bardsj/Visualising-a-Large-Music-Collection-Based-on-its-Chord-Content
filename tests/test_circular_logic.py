from Project.Data.Optimisation.AVSDF import AVSDF
import unittest

class CircularLogicTest(unittest.TestCase):
    def setUp(self):
        self.edge_list1 = [
            ["A","B"]
        ]
        self.order1 = ["A","B"]

        self.edge_list2 = [
            ["B","H"],
            ["H","D"],
            ["C","F"],
            ["D","G"]
        ]
        self.order2 = ["A","B","C","D","E","F","G","H"]

        self.edge_list3 = [
            ["A","B"],
            ["A","C"],
            ["A","D"],
            ["A","E"],
            ["A","F"],
            ["A","G"],
            ["A","H"],
            ["H","B"]
        ]
        self.order3 = ["A","B","C","D","E","F","G","H"]

    def test_total_crossing_number_count1(self):
        self.assertEqual(AVSDF([])._count_all_crossings(self.order1,self.edge_list1),0)

    def test_total_crossing_number_count2(self):
        self.assertEqual(AVSDF([])._count_all_crossings(self.order2,self.edge_list2),2)

    def test_total_crossing_number_count3(self):
        self.assertEqual(AVSDF([])._count_all_crossings(self.order3,self.edge_list3),5)

    def test_edge_crossings_number1(self):
        self.assertEqual(AVSDF([])._count_crossings_edge(self.order2,self.edge_list2,["H","D"]),1)

    def test_edge_crossings_number2(self):
        self.assertEqual(AVSDF([])._count_crossings_edge(self.order2,self.edge_list2,["H","B"]),0)
    
    def test_edge_crossings_number3(self):
        self.assertEqual(AVSDF([])._count_crossings_edge(self.order2,self.edge_list2,["F","C"]),2)

    def test_edge_crossings_number3(self):
        self.assertEqual(AVSDF([])._count_crossings_edge(self.order3,self.edge_list3,["A","C"]),1)

    def test_adj_edges1(self):
        self.assertEqual(AVSDF(self.edge_list1)._adjacent_edges("A"),[["A","B"]])

    def test_adj_edges1_1(self):
        self.assertEqual(AVSDF(self.edge_list1)._adjacent_edges("C"),[])

    def test_adj_edges2(self):
        self.assertCountEqual(AVSDF(self.edge_list2)._adjacent_edges("H"),[["H","D"],["B","H"]])

    def test_adj_edges3(self):
        self.assertCountEqual(AVSDF(self.edge_list3)._adjacent_edges("A"),[["A","B"],["A","C"],["A","D"],["A","E"],["A","F"],["A","G"],["A","H"]])

    def test_adj_vertex1(self):
        self.assertCountEqual(AVSDF(self.edge_list1)._adjacent_vertices("C"),[])
    
    def test_adj_vertex2(self):
        self.assertCountEqual(AVSDF(self.edge_list2)._adjacent_vertices("D"),["G","H","D"])

    def test_adj_vertex3(self):
        self.assertCountEqual(AVSDF(self.edge_list3)._adjacent_vertices("B"),["B","H","A"])

    def test_degree1(self):
        self.assertEqual(AVSDF(self.edge_list1)._degree("B"),1)

    def test_degree2(self):
        self.assertEqual(AVSDF(self.edge_list2)._degree("D"),2)

    def test_degree2_2(self):
        self.assertEqual(AVSDF(self.edge_list2)._degree(55),0)

    def test_degree3(self):
        self.assertEqual(AVSDF(self.edge_list3)._degree("A"),7)