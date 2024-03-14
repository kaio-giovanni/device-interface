import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock
)

from .modbus_data_sender import ModbusDataSender


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

    def getValues(self, address, count=1):
        response = super().getValues(address, count=count)
        self.logger.info(f"Callback from getValues with address {address}, count {count} and data {response}")
        self.data_sender.check_values_ready()
        return response

    def validate(self, address, count=1):
        is_valid = super().validate(address, count=count)
        self.logger.info(f"Callback from validate with address {address}, count {count}, data {is_valid}")
        return is_valid
