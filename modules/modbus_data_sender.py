import asyncio
import logging
import os

from .http_requests import HttpRequests
from .utils import Utils

"""

This class is an implementation of the Singleton pattern.
If you want to instantiate this class, use the class method instance() instead of using the constructor method __init__
Ex: obj = ModbusDataSender.instance()
"""


class ModbusDataSender():
    _instance = None
    data_is_ready = False

    def __init__(self):

        self.map_values = {}
        self.json = {
            "lot": None,
            "inputs": [
                {
                    "propertyName": "opticalFiberExtraction",
                    "value": None
                },
                {
                    "propertyName": "width",
                    "value": None
                },
                {
                    "propertyName": "height",
                    "value": None
                },
                {
                    "propertyName": "bipartition",
                    "value": None
                },
                {
                    "propertyName": "heightnosteel",
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

    def convert_values(self, address):
        values = self.map_values[address]
        decoded_value = Utils.decode_16bit_word_to_float(values)
        return str(decoded_value) if isinstance(self.map_values[address], list) else self.map_values

    def set_json_values(self):
        op = self.convert_values(3) if 3 in self.map_values else None
        width = self.convert_values(5) if 5 in self.map_values else None
        height = self.convert_values(6) if 6 in self.map_values else None
        bipartition = self.convert_values(4) if 4 in self.map_values else None
        heightnosteel = self.convert_values(2) if 2 in self.map_values else None
        lot = self.map_values[7] if 7 in self.map_values else None
        self.json["lot"] = self.decode_batch_value(lot)

        for item in self.json["inputs"]:
            if item["propertyName"] == "opticalFiberExtraction":
                item["value"] = op
            elif item["propertyName"] == "width":
                item["value"] = width
            elif item["propertyName"] == "height":
                item["value"] = height
            elif item["propertyName"] == "bipartition":
                item["value"] = bipartition
            elif item["propertyName"] == "heightnosteel":
                item["value"] = heightnosteel

    def clear_json(self):
        self.json["lot"] = None
        for item in self.json["inputs"]:
            item["value"] = None

    def check_values_ready(self, address, values):
        self.map_values[address] = values
        if ModbusDataSender.data_is_ready:
            self.set_json_values()
            self.create_task()
            ModbusDataSender.data_is_ready = False

    def check_json(self) -> bool:
        if self.json["lot"] is None:
            return False
        for item in self.json["inputs"]:
            if item["value"] is None:
                return False
        return True

    async def send_data_to_api(self):
        api_endpoint = os.environ["HOST_API_ENDPOINT"]
        req = HttpRequests(api_endpoint)
        return await req.send_data(self.json)

    def decode_batch_value(self, registers):
        try:
            return Utils.words_to_string(registers)
        except Exception as exc:
            self.logger.error(f"Unable to decode value from registers: {registers} - {exc}")
            return "Batch value invalid"

    def done_callback(self, t):
        self.map_values.clear()
        self.clear_json()
        self.logger.info(f"Http callback result: {t}")
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
                    self.clear_json()
            else:
                self.logger.info(f"Unable to send data. JSON invalid: {self.json}")
        except Exception as exc:
            self.logger.error(f"Error while trying to process data from registers. {exc}")
