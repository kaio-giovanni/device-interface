import logging
import os

from dotenv import load_dotenv

from .modbus_rtu_server import ModbusRtuServer

logging.basicConfig(filename='application.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.debug('Runnning project...')
    # load all the variables found as environment variables
    load_dotenv()

    # Get values from .env file
    port = os.environ['MODBUS_SERVER_PORT']
    baudrate = os.environ['BAUDRATE']

    # Run main function
    modbusClient = ModbusRtuServer(port=port, baudrate=baudrate)
    modbusClient.main()
