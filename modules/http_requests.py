import asyncio
import logging

import requests
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class HttpRequests:

    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"Using the API Url: {base_url}")

    async def sendData(self, address, values) -> bool:
        data = self.build_request(address, values)
        http_response = await asyncio.to_thread(requests.post, self.base_url, json=data)
        if http_response.ok:
            self.logger.info(f"The JSON: {data} was successfully sent to the endpoint: {self.base_url}")
            return True
        else:
            self.logger.error(f"The API returned an error message when trying to send the json: {data} to endpoint {self.base_url}")
            raise requests.exceptions.HTTPError

    def build_request(self, address, values):
        batch_value = self.decode_batch_value(values[6])
        return {
            'ready': values[0], # esse nao vai no json
            'operacao': values[1],
            'extracao': values[2],
            'bipartimento': values[3],
            'largura': values[4],
            'altura': values[5],
            'lote': batch_value,
        }

    def decode_batch_value(self, data):
        decoder = BinaryPayloadDecoder.fromRegisters(data, Endian.Big, Endian.Big)
        return decoder.decode_string()


"""
BinaryPayloadDecoder.fromRegisters(res2.registers, Endian.Big, Endian.Big).decode_32bit_float()
BinaryPayloadDecoder.fromRegisters(res3.registers, Endian.Big, Endian.Little).decode_16bit_int()
BinaryPayloadDecoder.fromRegisters(res4.registers, Endian.Big, Endian.Little).decode_16bit_int()
BinaryPayloadDecoder.fromRegisters(res5.registers, Endian.Big, Endian.Little).decode_bits()
"""