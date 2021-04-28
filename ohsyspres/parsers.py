# pylint: disable=too-few-public-methods
import logging
from typing import Dict
from pyparsing import (
    Word,
    alphas,
    Suppress,
    nums,
    string,
    Regex,
)


class MikrotikParser:

    def __init__(self) -> None:
        topic = Word(string.ascii_lowercase) + Suppress(",")
        level = Word(string.ascii_lowercase)
        device = Word(alphas + nums + "_" + "-" + "." + ":") + Suppress("@")
        network = Word(alphas + '-') + Suppress(":")
        state = Word(alphas) + Suppress(",")
        message = Regex(".*")

        # pattern build
        self.__pattern = topic + level + device + network + state + message

    def parse(self, line: str) -> Dict:
        parsed = self.__pattern.parseString(line)

        payload = {}
        payload["topic"] = parsed[0]
        payload["level"] = parsed[1]
        payload["device"] = parsed[2].replace(':', '').lower()
        payload["network"] = parsed[3].replace('-', '_')
        payload["state"] = parsed[4]
        payload["switch"] = 'ON' if parsed[4] == 'connected' else 'OFF'
        payload["message"] = parsed[5]

        direction = 'to' if parsed[4] == 'connected' else 'from'
        logging.debug('%s %s %s %s', parsed[2],
                      parsed[4], direction, parsed[3])

        return payload
