from base64 import b64decode
import base64
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client
from utilites.deserialize import deserialize
from Client import Client
from MyTransaction import MyTransaction
import time


#Create a new algod client, configured to connect to our local sandbox
algod_address= "http://localhost:4001"
algod_token="a"*64
algod_client=algod.AlgodClient(algod_token,algod_address)

# Create a new client with an alternate api key header
special_algod_client = algod.AlgodClient(
    "", algod_address, headers={"X-API-Key": algod_token}
)


#example: ALGOD_CREATE_CLIENT
algod_client = get_algod_client()
accts = get_accounts()


acct1 = accts.pop()
private_key, address,signer1 = acct1.private_key, acct1.address,acct1.signer


acct2 = accts.pop()
private_key2,address2,signer2 = acct2.private_key,acct2.address,acct2.signer


account_info = algod_client.account_info(address)

c1 = Client(address,private_key,signer1,algod_token,algod_address,headers={"X-API-Key": algod_token})
c2 = Client(address2,private_key2,signer2,algod_token,algod_address,headers={"X-API-Key": algod_token})

contract,appid,appaddr=c1.open_channel(address2)
c2.insert_channel(contract,appid,appaddr,address)

#First step Deposit Transaction, c2 must give a signed transaction - OffChain
txs=c1.send(address2,100,deposit=True,create=True)
c2.receive(address,txs,signed=False)
txs=c2.send(address)
c1.receive(address2,txs,signed=True)
#(On chain) deposit
c1.deposit(100,address2)


#Second step
#Sending the secret of the former transaction - Offchain
s=c1.send_secret(address2)
c2.receive_secret(address,s)
# C1 --(10 algos)-->C2 - Offchain
txs=c1.send(address2,5,create=True)
c2.receive(address,txs)
txs=c2.send(address)
c1.receive(address2,txs,signed=True)

#Third step
#Sending the secret of the former transaction -Offchain
s=c1.send_secret(address2)
c2.receive_secret(address,s)
# C2 --(5 algos)-->C1 - Offchain
txs=c2.send(address,1,create=True)
c1.receive(address2,txs)
txs=c1.send(address2)
c2.receive(address,txs,signed=True)

# Closing step - OnChain 
c1.presentation(address2)
c1.close_channel(address2)




