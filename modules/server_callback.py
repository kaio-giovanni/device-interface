import asyncio
import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock
)

from .utils import Utils


class CallbackDataBlock(ModbusSequentialDataBlock):
    http_request_success = None

    def __init__(self, queue, addr, values, callback_function):
        self.queue = queue
        self.callback_function = callback_function
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        super().__init__(addr, values)

    def setValues(self, address, values):
        super().setValues(address, values)
        self.logger.info(f"Callback from setValues with address {address}, values {values}")

    def getValues(self, address, count=1):
        response = super().getValues(address, count=count)

        if Utils.data_ready_to_be_sent(response):
            loop = Utils.get_event_loop()

            if loop and loop.is_running():
                task = loop.create_task(self.callback_function(address, response))
                task.add_done_callback(self.done_callback)
            else:
                self.logger.info("Starting a new event loop")
                asyncio.run(self.callback_function(address, values))

        feedback = self.return_feedback(response)
        self.logger.info(f"Callback from getValues with address {address}, count {count}, data {feedback}")
        return feedback


    def validate(self, address, count=1):
        is_valid = super().validate(address, count=count)
        self.logger.info(f"Callback from validate with address {address}, count {count}, data {is_valid}")
        return is_valid

    def done_callback(self, r):
        self.logger.info(f"HTTP request result: {r.result()}")
        if r.done() and r.result() != None:
            # dados salvos na api
            CallbackDataBlock.http_request_success = True
        elif r.done() and r.result() == None:
            # A API retornou um erro ao tentar salvar os dados
            CallbackDataBlock.http_request_success = False

    def return_feedback(self, response):
        try:
            if len(response) >= 8 and \
                    CallbackDataBlock.http_request_success != None and \
                    CallbackDataBlock.http_request_success == True:
                response[0] = 1  # sinalizador de que os dados foram salvos corretamente
                CallbackDataBlock.http_request_success = None
            elif len(response) >= 8 and \
                    CallbackDataBlock.http_request_success != None and \
                    CallbackDataBlock.http_request_success == False:
                response[0] = -1  # sinalizador de que os dados não foram salvos corretamente
                CallbackDataBlock.http_request_success = None
        except Exception as exc:
            self.logger.error("Error when trying to return HTTP request result feedback to Modbus Client")

        return response
