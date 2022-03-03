import unittest
from unittest import TestCase

import server
from client import client, Client


class test_client(TestCase):
    """
        for this set up i require to run the server (to get the ip of the server)!
        notice : The "import" opens a new client
    """

    def setUp(self) -> None:
        PORT = 50011
        self.client = Client(PORT)

    # self.client2 = Client(PORT) #for nickname test2

    """ test: if the client haveing the corret port   """

    def test_port(self):
        print("-------Test port----------")
        self.assertEqual(self.client.port, 50011)
        print("PASSED!")

    """  for this test i manually enter the name yossi """

    def test_nickame(self):
        print("-------Test nickname----------")
        self.assertEqual(self.client.nickname, "yossi")
        print("PASSED!")

        # for i in server.server_files:
        #     print(i)
        # self.assertEqual(self.client.nickname, )

        print("test2")
        # self.assertEqual(self.client2.nickname, "gal")
        # print("PASSED!")

    """ 
    For this test you need to replace it with the server's IP address
    """

    # def test_host(self):
    #     print("-------Test host----------")
    #     self.assertEqual(self.client.host, "192.168.1.31")
    #     print("PASSED!")

    # def test_list(self):
    #     for i in server.server_files:
    #         print(i)
    #     self.assertEqual(1, 1)
