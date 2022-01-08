import logging
from typing import Dict

import click

from .presence import OpenhabSyslogPresence


class DeviceTuple(click.Tuple):
    name = "device"

    def convert(self, value, param, ctx):
        mac = value[0].upper().replace(':', '')
        return (
            ':'.join(mac[i:i+2] for i in range(0, 12, 2)),
            value[1]
        )


class MacAddress(click.ParamType):
    name = 'macaddress'

    def convert(self, value: str, param, ctx):
        if value:
            value = value.upper().replace(':', '')
            return ':'.join(value[i:i+2] for i in range(0, 12, 2))
        return None


@click.command()
@click.option(
    '--host', help='IP to advertise on, default 0.0.0.0', envvar='OHSYSLOG_HOST', default='0.0.0.0'
)
@click.option(
    '--port', help='Port to listen on, default 1514', envvar='OHSYSLOG_PORT', default=1514
)
@click.option(
    '--openhab-url', help='URL for OpenHAB', envvar='OHSYSLOG_URL', required=True,
)
@click.option(
    '--router-host', help='Router ip for guest count lookup', envvar='ROUTER_HOST'
)
@click.option(
    '--router-creds', nargs=2, type=click.Tuple([str, str]), envvar='ROUTER_CREDS',
    default=[None] * 2,
    help=('Username Password for router, Scoped Read Only account recommended,'
          'export ROUTER_CREDS="username reallygoodropassword')
)
@click.option(
    '--watch-device', '-w', nargs=2, type=DeviceTuple([str, str]), multiple=True,
    help="devices to watch/item names. ie -w 846969F9D00F Phone -w 07559D07C215 Laptop",
)
@click.option(
    '--append-network', is_flag=True, default=False,
    help='Append Wifi Network to item, ie Phone_MyWiFi',
)
@click.option(
    '--ignore-device', '-i', type=MacAddress(), multiple=True,
    help="Devices to ignore. ie -i 846969F9D01F"
)
@click.option(
    '--guest-network', '-g', multiple=True,
    help='Guest networks for simple device counts'
)
@click.option(
    '--debug', is_flag=True, default=False, help='Enable debug logging'
)
@click.option(
    '--log-file', type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="Path to log file"
)
def run(host: str, port: int, debug: bool, log_file: str, **kwargs: Dict) -> None:
    logging_config = {
        "level": logging.DEBUG if debug else logging.INFO,
        "format": '[%(asctime)s] [%(levelname)-8s] %(message)s'
    }
    if log_file:
        logging_config['filename'] = log_file
    logging.basicConfig(**logging_config)  # type: ignore
    logging.debug(
        'host (%s) / port (%s) / **kwargs (%s)',
        host, port, kwargs
    )

    OpenhabSyslogPresence(host, port).run()
