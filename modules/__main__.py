import logging
import os

from dotenv import load_dotenv

from .modbus_rtu_server import ModbusRtuServer

logging.basicConfig(filename='application.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.info('Initializing the project...')

    load_dotenv()
    port = os.getenv('MODBUS_SERVER_PORT', "/dev/ttyUSB0")

    modbusClient = ModbusRtuServer(port=port)
    modbusClient.main()
