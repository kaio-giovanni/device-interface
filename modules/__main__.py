import logging
import os

from dotenv import load_dotenv

from .modbus_rtu_server import ModbusRtuServer

logging.basicConfig(filename='application.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.debug('Runnning project...')

    load_dotenv()
    port = os.environ['MODBUS_SERVER_PORT']
    baudrate = os.environ['BAUDRATE']
    num_registers = os.environ['NUM_REGISTERS']

    modbusClient = ModbusRtuServer(port=port, baudrate=baudrate, num_registers=num_registers)
    modbusClient.main()
