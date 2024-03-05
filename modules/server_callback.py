import asyncio
import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock
)

class CallbackDataBlock(ModbusSequentialDataBlock):

    def __init__(self, queue, addr, values, callback_function):
        self.queue = queue
        self.callback_function = callback_function
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        super().__init__(addr, values)

    def setValues(self, address, values):
        super().setValues(address, values)
        self.logger.debug(f"Callback from setValues with address {address}, values {values}")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            task = loop.create_task(self.callback_function(address, values))
            task.add_done_callback(
                lambda t: self.logger.debug(f"The data was sent successfully!!")
            )
        else:
            self.logger.debug("Starting a new event loop")
            asyncio.run(self.callback_function(address, values))

    def getValues(self, address, count=1):
        response = super().getValues(address, count=count)
        self.logger.debug(f"Callback from getValues with address {address}, count {count}, data {response}")
        return response

    def validate(self, address, count=1):
        is_valid = super().validate(address, count=count)
        self.logger.debug(f"Callback from validate with address {address}, count {count}, data {is_valid}")
        return is_valid
