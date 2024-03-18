import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock
)

from .modbus_data_sender import ModbusDataSender

TRIGGER_ADDRESS = 1
TRIGGER_VALUE = [1]
API_STATUS_ADDRESS = 0


class CallbackDataBlock(ModbusSequentialDataBlock):

    def __init__(self, queue, addr, values):
        self.queue = queue
        self.data_sender = ModbusDataSender.instance()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        super().__init__(addr, values)

    def setValues(self, address, values):
        super().setValues(address, values)
        self.logger.info(f"Callback from setValues with address {address}, values {values}")
        self.data_sender.set_map_values(address, values)
        if address == TRIGGER_ADDRESS and values == TRIGGER_VALUE:
            self.data_sender.pack_and_send_data()

    def getValues(self, address, count=1):
        response = super().getValues(address, count=count)
        self.data_sender.set_map_values(address, response)
        if address == API_STATUS_ADDRESS:
            api_response_status = self.data_sender.check_api_response()
            response[0] = api_response_status
            self.logger.info(f"Returning HTTP response status in the address {address} with value {api_response_status}. - {response}")
            self.data_sender.restore_api_response_status()
        return response

    def validate(self, address, count=1):
        valid = super().validate(address, count=count)
        if not valid:
            self.logger.info(f"Invalid request to address {address}, with count {count}")
        return valid
