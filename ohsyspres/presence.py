# pylint: disable=too-few-public-methods,too-many-instance-attributes
import logging
import socketserver
import click
import requests
from requests.exceptions import RequestException
from pyparsing import ParseException
from librouteros import connect
from librouteros.query import Key

from .parsers import MikrotikParser


class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def __init__(self, *args, **kwargs) -> None:
        # These values are already checked by click on the way in,
        # however mypy doesn't like when you try to do operations on
        # potentially 'None' variables.
        self.openhab_url = click.get_current_context().params.get(  # type: ignore
            'openhab_url').rstrip('/')
        self.watched_devices = dict(
            click.get_current_context().params.get('watch_device'))  # type: ignore
        self.ignored_devices = list(
            click.get_current_context().params.get('ignore_device'))  # type: ignore
        self.guest_networks = list(
            click.get_current_context().params.get('guest_network'))  # type: ignore
        self.router_host = click.get_current_context().params.get(  # type: ignore
            'router_host'
        )
        self.router_user, self.route_pass = click.get_current_context().params.get(  # type: ignore
            'router_creds'
        )
        self.append_network = click.get_current_context().params.get(  # type: ignore
            'append_network'
        )
        super().__init__(*args, **kwargs)

    @property
    def routeros(self):
        return connect(
            username=self.router_user,
            password=self.route_pass,
            host=self.router_host,
        )

    def watched(self, device, switch, network):
        item = self.watched_devices.get(device)
        if item is None:
            logging.debug("'%s' not in watched device list", device)
            return None, None

        if self.append_network:
            item = f'{item}_{network}'.replace('-', '_')

        return item, switch

    def wireless_guest(self):
        mac_address = Key('mac-address')
        interface = Key('interface')
        macs = [mac_address != x for x in [*self.ignored_devices, *self.watched_devices]]
        results = self.routeros.path('/interface/wireless/registration-table').select(
            mac_address, interface).where(interface == 'Guest', *macs)
        return 'Total_Connected_Guests', str(len(list(results)))

    def caps_guest(self):
        mac_address = Key('mac-address')
        interface = Key('interface')
        macs = [mac_address != x for x in [*self.ignored_devices, *self.watched_devices]]
        results = []
        for network in self.guest_networks:
            devices = self.routeros.path('/caps-man/registration-table').select(
                mac_address, interface).where(interface == network, *macs)
            results.extend(devices)
        logging.debug(results)
        return 'Total_Connected_Guests', str(len(list(results)))

    def handle(self):
        data = bytes.decode(self.request[0].strip(), encoding="utf-8")
        try:
            parsed = MikrotikParser().parse(data)
        except ParseException:
            logging.debug("Could not parse '%s'", data)
            return

        topic = parsed.get('topic', 'wireless')
        device = parsed.get('device')
        switch = parsed.get('switch')
        network = parsed.get('network')

        if device in self.ignored_devices:
            logging.info("Device '%s' in ignored device list",
                         device)
            return

        item, data = self.watched(device, switch, network)
        if not item and network in self.guest_networks:
            item, data = getattr(self, f'{topic}_guest')()
            logging.info('Current guest count: %s', data)
        elif not item:
            return

        item_url = '{}/rest/items/{}'.format(
            self.openhab_url, item)
        try:
            result = requests.post(item_url, data=data,
                                   headers={'Content-Type': 'text/plain'})
        except RequestException as exception:
            logging.error('Web request exception %s', exception)

        if result.status_code > 299:
            logging.error('Item update failed: %s (%s)',
                          result.reason, result.status_code)
            logging.debug(result.text)
        else:
            logging.info("'%s' updated '%s' with state '%s'",
                         device, item, data)


class OpenhabSyslogPresence:

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server = socketserver.UDPServer(
            (self.host, self.port), SyslogUDPHandler)

    def run(self) -> None:
        try:
            self.server.serve_forever(poll_interval=0.5)
        except (IOError, SystemExit) as exception:
            raise Exception("Syslog Server Failed") from exception
        except KeyboardInterrupt:
            print("Crtl+C Pressed. Shutting down.")
