# Device Interface

This project is a POC demo of using Modbus RTU to connect devices. To test it, you can use two or more devices.  
In this project, I use a Raspberry Pi 3b+ as a Modbus slave client, to receive data from an HMI (Human-Machine Interface) Modbus master client.
After the Modbus master client requests to write data into the registers, the Modbus slave client will get these data and send them to an external API for further processing.


### Dependencies

- Python

### Setup

- Config the Raspberry Pi to enable serial connection:

```bash

sudo raspi-config
```

- Install the virtualenv library using the package installer for Python (PIP):

```bash

pip install -r virtualenv
```

- Run the following command to create a Python Virtual Environment to install packages. This command will create
  a folder named '.venv' with all required libraries to run the project.

```bash
python -m virtualenv .venv
```

- Run the following command to enter in the Python Virtual Environment

```bash

# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activate
```

- After that, you can install the required packages. Run the following commands:

```bash
pip install --require-virtualenv -r ./requirements.txt
```

- Create a .env file in the root folder and set the env variables according to the [env example](.env.example)

- All project logs will be stored in the [logfile](./application.log). To watch a .log file in real-time, run the command below:

```bash

# Linux
sudo tail -f [path/to/logfile.log]

# Windows (PowerShell)
type -wait [path/to/logfile.log]

```

### Modbus Function codes

| Function Code | Register Type                    |
|---------------|----------------------------------|
| 1	            | Read Coil                        |
| 2	            | Read Discrete Input              |
| 3	            | Read Holding Registers           |
| 4	            | Read Input Registers             |
| 5	            | Write Single Coil                |
| 6	            | Write Single Holding Register    |
| 15	           | Write Multiple Coils             |
| 16	           | Write Multiple Holding Registers |

### How to run

- After finishing all the steps above, connect the raspberry with the HMI and run the project:

```bash

python -m modules
```

