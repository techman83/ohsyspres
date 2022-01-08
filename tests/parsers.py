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

    def test_disconnected_network(self):
        self.assertEqual(self.disconnected['network'], 'wifi-network')

    def test_topic(self):
        self.assertEqual(self.disconnected['topic'], 'wireless')


class TestMirkotikCapsParser(BaseTests.Parser):

    @classmethod
    def setUpClass(cls):
        cls.connected = MikrotikParser().parse(
            'caps,info 84:6c:6a:F9:D0:0F@prefix-ap-1 connected, signal strength -36')
        cls.disconnected = MikrotikParser().parse((
            'caps,info 84:6c:6a:F9:D0:0F@prefix-ap-1 disconnected, received deauth: '
            'ending station leaving (3), signal strength -42'))

    def test_connected_state(self):
        self.assertEqual(self.connected['state'], 'connected')

    def test_disconnected_state(self):
        self.assertEqual(self.disconnected['state'], 'disconnected')

    def test_disconnected_network(self):
        self.assertEqual(self.disconnected['network'], 'prefix-ap-1')

    def test_topic(self):
        self.assertEqual(self.disconnected['topic'], 'caps')
