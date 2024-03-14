import asyncio
import logging
import os

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from .http_requests import HttpRequests
from .utils import Utils

"""

This class is an implementation of the Singleton pattern.
If you want to instantiate this class, use the class method instance() instead of using the constructor method __init__
Ex: obj = ModbusDataSender.instance()
"""


class ModbusDataSender():
    _instance = None

    def __init__(self):

        self.map_values = {}
        self.json = {
            "lot": None,
            "inputs": [
                {
                    "propertyName": "lot1",
                    "value": None
                },
                {
                    "propertyName": "lot2",
                    "value": None
                },
                {
                    "propertyName": "lot3",
                    "value": None
                },
                {
                    "propertyName": "lot4",
                    "value": None
                },
                {
                    "propertyName": "lot5",
                    "value": None
                }
            ]
        }
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_map_values(self, address, value):
        self.map_values[address] = value

    def set_json_values(self):
        self.json["lot"] = self.decode_batch_value(self.map_values[6])
        for item in self.json["inputs"]:
            if item["propertyName"] == "lot1":
                item["value"] = str(self.map_values[2])
            elif item["propertyName"] == "lot2":
                item["value"] = str(self.map_values[4])
            elif item["propertyName"] == "lot3":
                item["value"] = str(self.map_values[5])
            elif item["propertyName"] == "lot4":
                item["value"] = str(self.map_values[3])
            elif item["propertyName"] == "lot5":
                item["value"] = str(self.map_values[1])

    def clear(self):
        self.map_values.clear()
        self.json["lot"] = None
        for item in self.json["inputs"]:
            item["value"] = None

    def check_values_ready(self):  # Check if values are ready to be sent
        if self.map_values[0] == 1:
            self.set_json_values()

    def check_json(self) -> bool:
        if self.json["lot"] == None:
            return False
        for item in self.json["inputs"]:
            if item["value"] == None:
                return False
        return True

    async def send_data_to_api(self):
        api_endpoint = os.environ["HOST_API_ENDPOINT"]
        req = HttpRequests(api_endpoint)
        await req.sendData(self.json)

    def decode_batch_value(self, registers):
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, Endian.Big, Endian.Big)
            return decoder.decode_string()
        except Exception as exc:
            self.logger.error(f"Unable to decode value from registers: {registers}")
            return "Invalid batch"

    def done_callback(self, t):
        self.clear()
        if t.result():
            self.logger.info("API returned a success message")
        else:
            self.logger.info("API returned an unsuccessful message")

    def create_task(self):
        try:
            if self.check_json():
                loop = Utils.get_event_loop()

                if loop and loop.is_running():
                    task = loop.create_task(self.send_data_to_api())
                    task.add_done_callback(self.done_callback)
                else:
                    self.logger.info("Starting a new event loop")
                    asyncio.run(self.send_data_to_api())
                    self.clear()
        except Exception as exc:
            self.logger.error(f"Error while trying to process data from registers. {exc}")
