# pylint: disable=too-few-public-methods,useless-object-inheritance
import unittest
from ohsyspres.parsers import MikrotikParser


class BaseTests:

    class Parser(unittest.TestCase):

        def test_connected_switch(self):
            self.assertEqual(self.connected['switch'], 'ON')

        def test_disconnected_switch(self):
            self.assertEqual(self.disconnected['switch'], 'OFF')

        def test_device(self):
            self.assertEqual(self.disconnected['device'], '84:6C:6A:F9:D0:0F')

        def test_disconnected_network(self):
            self.assertEqual(self.disconnected['network'], 'wifi_network')


class TestMirkotikParser(BaseTests.Parser):

    @classmethod
    def setUpClass(cls):
        cls.connected = MikrotikParser().parse(
            'wireless,info 84:6c:6a:F9:D0:0F@wifi-network: connected, signal strength -85')
        cls.disconnected = MikrotikParser().parse(
            'wireless,info 84:6c:6a:F9:D0:0F@wifi-network: disconnected, signal strength -85')

    def test_connected_state(self):
        self.assertEqual(self.connected['state'], 'connected')

    def test_disconnected_state(self):
        self.assertEqual(self.disconnected['state'], 'disconnected')
