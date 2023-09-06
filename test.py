from base64 import b64decode
import base64
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client
from utilites.deserialize import deserialize
from Client import Client
from MyTransaction import MyTransaction

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

""" 
---------------------------------Retrive Contract------------------------------------ """

sp = algod_client.suggested_params()

with open("./artifacts/approval.teal") as f:
     tmp=f.read()
     compiled = algod_client.compile(tmp)
     app_pro = base64.b64decode(compiled["result"])


with open("./artifacts/clear.teal") as f:
     tmp=f.read()
     compiled = algod_client.compile(tmp)
     app_clear = base64.b64decode(compiled["result"])


with open("./artifacts/contract.json") as f:
     tmp=f.read()
     contract = deserialize(tmp)
"-----------------------------------------------------------------------------------------------"




c1 = Client(address,private_key,algod_client)
c2 = Client(address2,private_key2,algod_client)


print(address)
print(address2)

#Create the SmartContract
channelid,channel_address =c1.open_channel(address2,app_pro,app_clear,contract)
#Depenency Injection of contract
c2.set_contract(channelid,channel_address,contract,address)

#Deposit of 101 algos -> 100 for the cannell 1 for the payment of the logic cost
c1.deposit(101)

# Off-Chain Transaction --------------------------------------------------------------------
#First exchange -> c1 gives one algo
t1 = MyTransaction(1,address,address2,99,1,12,address)
t1.sign(signer2,address2)
t1.sign(signer1,address)

#second exchange -> c1 gives 50algos
#Exchange of the secret
t2 = MyTransaction(2,address,address2,50,50,5,address)
t2.sign(signer2,address2)
t2.sign(signer1,address)

# ---------------------------------------------------------------------------------------------

c1.tryClose(t2)
#close the Smart contract  withdraw the ammount deposited
c1.closeChannel(0)