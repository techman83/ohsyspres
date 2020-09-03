import logging
from typing import Dict

import click

from .presence import OpenhabSyslogPresence

# HOST, PORT = "0.0.0.0", 1514
# formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(message)s')
#
#
# def setup_logger(name, log_file, level=logging.INFO, console=False):
#    """To setup as many loggers as you want"""
#
#    handler = logging.FileHandler('/tmp/' + log_file)
#    handler.setFormatter(formatter)
#
#    logger = logging.getLogger(name)
#    logger.setLevel(level)
#    logger.addHandler(handler)
#    if console:
#        console_handler = logging.StreamHandler(sys.stdout)
#        console_handler.setFormatter(formatter)
#        logger.addHandler(console_handler)
#
#    return logger
#
#
# logger = setup_logger('mikrotik', 'mikrotik.log', console=True)


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
def run(host: str, port: int, debug: bool, **kwargs: Dict) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level, format='[%(asctime)s] [%(levelname)-8s] %(message)s')
    logging.debug(
        'host (%s) / port (%s) / **kwargs (%s)',
        host, port, kwargs
    )

    OpenhabSyslogPresence(host, port).run()
