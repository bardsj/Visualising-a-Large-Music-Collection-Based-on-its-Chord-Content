from Project.Data.HighUtilityItemset.FHM import FHM
import unittest

class FHMTest(unittest.TestCase):
    def setUp(self):
        self.transactions =[(i,x) for i,x in enumerate([
                [("Coke 12oz", 6), ("Chips", 2), ("Dip", 1)],
                [("Coke 12oz", 1)],
                [("Coke 12oz", 2), ("Chips", 1)],
                [("Chips", 1)],
                [("Chips", 2)],
                [("Coke 12oz", 6), ("Chips", 1)]
            ])]
        

        self.external_utilities = {
                "Coke 12oz": 1.29,
                "Chips": 2.99,
                "Dip": 3.49
            }

    def testFHMMining(self):
        hui = FHM(self.transactions,self.external_utilities,20,minutil_pc=False).run_FHM()
        self.assertEqual(hui,[(['Coke 12oz', 'Chips'], 30.02), (['Chips'], 20.93)])