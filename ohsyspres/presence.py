# pylint: disable=too-few-public-methods
import logging
import socketserver
import click
import requests
from requests.exceptions import RequestException
from pyparsing import ParseException

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
        self.append_network = click.get_current_context().params.get(  # type: ignore
            'append_network'
        )
        super().__init__(*args, **kwargs)

    def handle(self):
        data = bytes.decode(self.request[0].strip(), encoding="utf-8")
        try:
            parsed = MikrotikParser().parse(data)
        except ParseException:
            logging.debug("Could not parse '%s'", data)
            return

        device = parsed['device']
        switch = parsed['switch']
        item = self.watched_devices.get(device)
        if item is None:
            logging.debug("'%s' not in watched device list", device)
            return

        if self.append_network:
            item = '{}_{}'.format(item, parsed['network'])

        item_url = '{}/rest/items/{}'.format(
            self.openhab_url, item)
        try:
            result = requests.post(item_url, data=switch)
        except RequestException as exception:
            logging.error('Web request exception %s', exception)

        if result.status_code > 299:
            logging.error('Item update failed: %s (%s)',
                          result.reason, result.status_code)
            logging.debug(result.text)
        else:
            logging.info("'%s' updated '%s' with state '%s'",
                         device, item, switch)


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
