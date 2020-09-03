import logging
from typing import Dict

import click

from .presence import OpenhabSyslogPresence


class DeviceTuple(click.Tuple):
    name = "device"

    def convert(self, value, param, ctx):
        return (
            value[0].replace(':', '').lower(),
            value[1]
        )


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
    '--watch-device', '-w', nargs=2, type=DeviceTuple([str, str]), multiple=True,
    help="devices to watch/item names. ie -w 846969F9D00F Phone -w 07559D07C215 Laptop",
)
@click.option(
    '--append-network', is_flag=True, default=False,
    help='Append Wifi Network to item, ie Phone_MyWiFi',
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
