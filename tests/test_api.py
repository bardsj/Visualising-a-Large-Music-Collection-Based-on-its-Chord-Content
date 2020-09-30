"""
Test API routes working
"""
from Project.Data.API.app import app
import unittest

class ApiTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_circular_route(self):
        r = self.app.get("/circular")
        self.assertEqual(r.status_code,200)

    def test_parallel_route(self):
        r = self.app.get("/parallel")
        self.assertEqual(r.status_code,200)

    def test_circHier_route(self):
        r = self.app.get("/circHier")
        self.assertEqual(r.status_code,200)
    
    def test_circClust_route(self):
        r = self.app.get("/circClust")
        self.assertEqual(r.status_code,200)

    def test_parallelClust_route(self):
        r = self.app.get("/parallelClust")
        self.assertEqual(r.status_code,200)

    def test_query_data(self):
        r = self.app.get("/queryData")
        self.assertEqual(r.status_code,200)