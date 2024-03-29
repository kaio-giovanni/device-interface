import asyncio

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartSerialServer
from pymodbus.transaction import ModbusRtuFramer

from .server_callback import CallbackDataBlock


class ModbusRtuServer:

    def __init__(self, port: str, baudrate=9600, num_registers=100, parity='N', bytesize=8, stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.num_registers = num_registers
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.server_identity = ModbusDeviceIdentification(info_name={
            "VendorName": "Revolution PI",
            "ProductCode": "RevPi Connect SE",
            "VendorUrl": "https://revolutionpi.com/shop/en/revpi-connect-se",
            "ProductName": 'RevPi Connect SE',
            "ModelName": 'RevPi Connect SE',
            "MajorMinorRevision": '1.0.0',
        })
        self.server = None

    def start_serial_server(self):
        queue = asyncio.Queue()
        datablock = CallbackDataBlock(queue, 0x00, [0] * self.num_registers)
        store = ModbusSlaveContext(
            di=datablock,
            co=datablock,
            hr=datablock,
            ir=datablock)
        context = ModbusServerContext(slaves=store, single=True)
        self.server = StartSerialServer(context=context,
                                        identity=self.server_identity,
                                        port=self.port,
                                        framer=ModbusRtuFramer,
                                        baudrate=self.baudrate,
                                        parity='N',
                                        stopbits=1,
                                        bytesize=8,
                                        retry_on_empty=True,
                                        retries=5,
                                        close_comm_on_error=False,
                                        message_wait_milliseconds=50,
                                        delay=1,
                                        timeout=1,
                                        )

    def main(self):
        asyncio.run(self.start_serial_server(), debug=True)
