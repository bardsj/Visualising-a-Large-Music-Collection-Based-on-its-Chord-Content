import sys
import os
sys.path.append(os.getcwd())

from Project.Data.Optimisation.AVSDF import AVSDF
import unittest

class CircularLogicTest(unittest.TestCase):
    def setUp(self):
        self.edge_list1 = [
            ["A","B"]
        ]
        self.order1 = ["A","B"]

    def test_total_crossing_number_count1(self):
        self.assertEqual(AVSDF([])._count_all_crossings(self.order1,self.edge_list1),0)