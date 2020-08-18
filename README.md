# Secure Charger [![python:v3.7](https://img.shields.io/badge/Python-v3.7-brightgreen.svg)](https://www.python.org/downloads/release/python-370/)

## Requirements
1. Python 3.7 or above
2. Hyperledger Fabric (https://hyperledger-fabric.readthedocs.io/en/release-2.2/prereqs.html)

Additional Libraries Required:
1. Python OCPP (https://pypi.org/project/ocpp/)
2. Python Websockets (https://pypi.org/project/websockets/)
3. Python MyHDL (http://www.myhdl.org/)

Clone the project in the directory you want.
```sh
$ git clone https://github.com/rushang99/SecureCharger
```
## Setting up multi-host Hyperledger 

## Steps to run the server client system
1. To create multiple car profiles for simulation, run [create_car_firebase.py](create_car_firebase.py) (if using firebase) or [create_car_sql.py](create_car_sql.py) (if using local sql database) with argument being the number of cars.
2. Run server.py
```sh
$ python3 server.py
```
3. Set the server’s public IP address in client.py
4. Run [client.py](client.py) to simulate a single car/client or run [multi_clients.py](multi_clients.py) to simulate multiple cars/clients. Set the ‘num’ variable in [multi_cars.py](multi_clients.py) to run required number of clients 
```sh
$ python3 multi_clients.py
```
[fcompact.py](fcompact.py) contains the python implemented fast version of PUF and [fexpand.py](fexpand.py) contains the slow version of PUF. 


[fcompact_hdl](fcompact_hdl.py) and [fexpand_hdl](fexpand_hdl.py) are the corresponding implementations using Python’s myHDL library for FPGA designs. [test_compact.py](test_compact.py) and [test_expand.py](test_expand.py) take a 12-bit challenge as a command line argument and generate a corresponding response using myHDL design of respective functions.

