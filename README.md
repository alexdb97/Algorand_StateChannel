# Algorand_StateChannel
Implementation of an architectural solution for devloping state channels, using Pyteal  on Algorand blockchain.

# Prerequisites
Make sure you have installed on your machine docker, an open source containerization technology, it is used for the creation of the local blockchain (https://docs.docker.com/engine/install/).
Morover is required python3.10+ (https://www.python.org/downloads/) interpreter and pip as a package manager.
After installed pip it is foundamental to install pipx (https://github.com/pypa/pipx),it is another package manager it is used for installing Algokit, 

The second step is to install Algokit, it is a tool that creates a local isolated Algorand Network so is it possible to simulate real transactions and Smart Contract execution on your computer it is done using the command ```pipx install algokit``` verify the installation typing  ``` algokit --version```.

# Code execution 
For the execution of the code is suggested to install all the libraries in a virtual environment (venv), after creating the venv ```python3 -m venv venv``` and activated it ```source venv/bin/activate``` you can install all the package listed inside the requirements file ```pip install -r requirements.txt```.
For the execution of the test provided you have first to initialize the localnet
```algokit localnet start```,
then compile the SmartContract written in pyTeal ```python3 SmartContract/Contract.py``` secondly execute the test ```python3 test.py``` or ```python3 test.py```





