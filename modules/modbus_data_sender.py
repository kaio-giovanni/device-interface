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

API_IDLE_STATUS = 0
API_RESPONSE_SUCCESS_STATUS = 1
API_RESPONSE_FAILED_STATUS = 2


class ModbusDataSender:
    _instance = None

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
        self.api_response_successful = API_IDLE_STATUS
        self.server_api_availabillity = API_RESPONSE_SUCCESS_STATUS

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_map_values(self, address, value):
        self.map_values[address] = value

    def convert_values(self, address):
        values = self.map_values[address]
        if not isinstance(values, list):
            return str(values)
        else:
            if len(values) == 1:
                return str(values[0])
            elif len(values) == 2:
                decoded_value = Utils.decode_16bit_word_to_float(values)
                return "{:.2f}".format(decoded_value)
            else:
                return str(values)

    def set_json_values(self):
        op = self.convert_values(3) if 3 in self.map_values else None
        width = self.convert_values(7) if 7 in self.map_values else None
        height = self.convert_values(9) if 9 in self.map_values else None
        bipartition = self.convert_values(5) if 5 in self.map_values else None
        heightnosteel = self.convert_values(2) if 2 in self.map_values else None
        lot = self.map_values[18] if 18 in self.map_values else None
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

    def pack_and_send_data(self):
        self.logger.info("Packing and sending data to the API")
        self.set_json_values()
        self.create_task()

    def check_json(self) -> bool:
        if self.json["lot"] is None:
            return False
        for item in self.json["inputs"]:
            if item["value"] is None:
                return False
        return True

    def check_api_response(self):
        return self.api_response_successful

    def restore_api_response_status(self):
        self.api_response_successful = API_IDLE_STATUS
        self.logger.info(f"Resetting the API response status to default value: {self.api_response_successful}")

    def check_server_availabillity(self):
        return self.server_api_availabillity

    async def send_data_to_api(self):
        api_endpoint = os.environ["API_ENDPOINT"]
        req = HttpRequests(api_endpoint)
        return await req.send_data(self.json)

    def decode_batch_value(self, registers):
        try:
            return Utils.words_to_string(registers)
        except Exception as exc:
            self.logger.error(f"Unable to decode value from registers: {registers} - {exc}")
            return "Batch value invalid"

    def api_done_callback(self, t):
        self.map_values.clear()
        self.clear_json()
        self.logger.info(f"Http callback result: {t}")
        if t.result():
            self.logger.info("API returned a success message")
            self.api_response_successful = API_RESPONSE_SUCCESS_STATUS
        else:
            self.logger.info("API returned an unsuccessful message")
            self.api_response_successful = API_RESPONSE_FAILED_STATUS

    def ping_done_callback(self, t):
        if t.result():
            self.server_api_availabillity = API_RESPONSE_SUCCESS_STATUS
        else:
            self.server_api_availabillity = API_RESPONSE_FAILED_STATUS

    def create_task(self):
        try:
            if self.check_json():
                loop = Utils.get_event_loop()

                if loop and loop.is_running():
                    task = loop.create_task(self.send_data_to_api())
                    task.add_done_callback(self.api_done_callback)
                else:
                    self.logger.info("Starting a new event loop")
                    asyncio.run(self.send_data_to_api())
                    self.clear_json()
            else:
                self.logger.info(f"Unable to send data. JSON invalid: {self.json}")
                self.api_response_successful = API_RESPONSE_FAILED_STATUS
        except Exception as exc:
            self.logger.error(f"Error while trying to process data from registers. {exc}")
            self.clear_json()
            self.api_response_successful = API_RESPONSE_FAILED_STATUS

    def create_periodic_task(self):
        while True:
            try:
                if loop and loop.is_running():
                    task = loop.create_task(Utils.check_server_periodically())
                    task.add_done_callback(self.ping_done_callback)
            except Exception as exc:
                self.logger.info("The server is offline")
                self.server_api_availabillity = API_RESPONSE_FAILED_STATUS