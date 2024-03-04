import logging

import pymodbus.client as modbusClient
from pymodbus import ModbusException
from pymodbus.transaction import ModbusRtuFramer


class ModbusRtuClient:
    def __init__(self, port: str, baudrate=9600, stopbits=1, timeout=1, bytesize=8, parity='N'):
        self.port = port
        self.baudrate = baudrate
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.parity = parity
        self.logger = logging.getLogger(__name__)
        self.client = None

    def startConnection(self) -> bool:
        self.logger.info('Connecting to the server...')
        self.client = modbusClient.AsyncModbusSerialClient(
            port=self.port,
            framer=ModbusRtuFramer,
            timeout=self.timeout,
            retries=5,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
        )

        self.client.connect()
        return self.client.connected

    def closeConnection(self):
        self.logger.info('Closing the connection...')
        self.client.close()

    def write_registers(self, register_address, data_to_write, slave_address):
        try:
            response = self.client.write_registers(register_address,
                                                   data_to_write,
                                                   unit=slave_address)

        except ModbusException as exc:
            self.logger.error(f"Received ModbusException({exc}) from library")
            self.closeConnection()
            return
        if isinstance(rr, ExceptionResponse):
            self.logger.error(f"Received Modbus library exception ({rr})")
            self.closeConnection()
        else:
            self.logger.info("Write successfully!!")

    def read_from_registers(self, register_address, num_registers, slave_address):
        response = self.client.read_holding_registers(register_address,
                                                      num_registers,
                                                      unit=slave_address)
        if not response.isError():
            self.logger.info("Read successful:", response.registers)
        else:
            self.logger.error("Error reading registers:", response)

