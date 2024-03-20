import asyncio
import logging
import os
import struct
from urllib.parse import urlparse


class Utils:
    _logger = logging.getLogger(__name__)

    @staticmethod
    def get_event_loop() -> asyncio.events.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    @staticmethod
    def split_word(word, byte_order):
        byte1 = (word >> 8) & 0xFF
        byte0 = word & 0xFF
        if byte_order == 'BIG':
            return byte0, byte1
        else:
            return byte1, byte0

    @staticmethod
    def words_to_string(word_array, byte_order='BIG'):
        bytes_list = []
        for word in word_array:
            byte1, byte0 = Utils.split_word(word, byte_order)
            bytes_list.append(byte1)
            bytes_list.append(byte0)
        return ''.join(chr(byte) for byte in bytes_list)

    @staticmethod
    def decode_16bit_word_to_float(words):
        t = tuple(words)
        packed_string = struct.pack('HH', *t)
        return struct.unpack('f', packed_string)[0]

    @staticmethod
    def ping_server() -> bool:
        try:
            Utils._logger.info("Pinging server...")
            url = os.environ["HOST_API_URL"]
            hostname = urlparse(url).netloc
            response = os.system(f"ping -c 1 {hostname}")
            Utils._logger.info(f"Server status: {"ONLINE" if response == 0 else "OFFLINE"})")
            if response == 0:
                return True
            else:
                return False
        except Exception as exc:
            Utils._logger.info(f"Error trying to ping the server {exc}")
            return False
