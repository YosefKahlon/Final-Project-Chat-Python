import unittest

from client import client
class test_client(unittest.TestCase):


    def test_one(self):

        c = client(50011)
        c.