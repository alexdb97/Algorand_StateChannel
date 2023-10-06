from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from algosdk import mnemonic,account, atomic_transaction_composer,transaction
from  Client import Client
import time

from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,      
)

with open("/home/ale/Desktop/Access/mnemonicA.txt") as fd:
    mnemonA = fd.read()
    mA=mnemonA.replace(',','')
    fd.close()

with open("/home/ale/Desktop/Access/mnemonicB.txt") as fd:
    mnemonB = fd.read()
    mB=mnemonB.replace(',','')
    fd.close()

pkA =mnemonic.to_private_key(mA)
addressA= account.address_from_private_key(pkA)
signerA = atomic_transaction_composer.AccountTransactionSigner(pkA)


pkB =mnemonic.to_private_key(mB)
addressB= account.address_from_private_key(pkB)
signerB = atomic_transaction_composer.AccountTransactionSigner(pkB)

#Reading the access token to testnet
with open("/home/ale/Desktop/Access/token.txt") as fd:
    file = fd.read()
    algod_token=file.replace('\n','')
    fd.close()


algod_url = "https://testnet-algorand.api.purestake.io/ps2"


headers = {
   "X-API-Key": algod_token,
}


Alice = Client(addressA,pkA,signerA,algod_token,algod_url,headers)
Bob = Client(addressB,pkB,signerB,algod_token,algod_url,headers)

contract,appid,appaddr=Alice.open_channel(Bob.address) #Cost 2000 microAlgos
print("Application identifier :",appid)
Bob.join_channel(contract,appid,appaddr,Alice.address)
#First step Deposit Transaction, Bob must give a signed transaction - OffChain
print("Alice deposits 5 algos on the channel")
txs=Alice.send(Bob.address,5,deposit=True,create=True)
Bob.receive(Alice.address,txs,signed=False)
txs=Bob.send(Alice.address)
Alice.receive(Bob.address,txs,signed=True)
#(On chain) deposit
Alice.deposit(5,Bob.address) #cost 2000 microAlgo
#Before of the second transaction there will be the phase of secret reveal
secret=Alice.send_secret(Bob.address)
Bob.receive_secret(Alice.address,secret)
print("Alice sends 5 algos to Bob")
#Alice gives 3 algos to Bob
txs=Alice.send(Bob.address,5,create=True)
Bob.receive(Alice.address,txs,signed=False)
txs=Bob.send(Alice.address)
Alice.receive(Bob.address,txs,signed=True)
#Before of the transaction there will be the phase of secret reveal
secret=Alice.send_secret(Bob.address)
Bob.receive_secret(Alice.address,secret)
#Bob gives 1 algos to Alice
print("Bob sends 0 algos to Alice")
txs=Bob.send(Alice.address,0,create=True)
Alice.receive(Bob.address,txs,signed=False)
txs=Alice.send(Bob.address)
Bob.receive(Alice.address,txs,signed=True)
# Closing step - OnChain
print("closing the channel")
Bob.presentation(Alice.address) #cost 6000 microalgo
Alice.close_channel(Bob.address) #cost 1000 microAlgos
Bob.delete(Alice.address )


""" contract,appid,appaddr=Alice.open_channel(Bob.address) #Cost 2000 microAlgos
Bob.join_channel(contract,appid,appaddr,Alice.address)
print("Application identifier :",appid)

#First step Deposit Transaction, Alice must give back a signed transaction before opening - OffChain
txs=Bob.send(Alice.address,20,deposit=True,create=True)
Alice.receive(Bob.address,txs,signed=False)
txs=Alice.send(Bob.address)
Bob.receive(Alice.address,txs,signed=True)
#(On chain) deposit
Bob.deposit(20,Alice.address) #cost 2000 microAlgo
print("Bob deposits 20 algos on the channel")
#Before of the second transaction there will be the phase of secret reveal
secret=Bob.send_secret(Alice.address)
Alice.receive_secret(Bob.address,secret)
#Bob sends 20 algos to Alice
print("Bob sends 10 algos to Alice")
txs=Bob.send(Alice.address,10,create=True)
Alice.receive(Bob.address,txs,signed=False)
txs=Alice.send(Bob.address)
Bob.receive(Alice.address,txs,signed=True)
#Before of the transaction there will be the phase of secret reveal
secret=Bob.send_secret(Alice.address)
Alice.receive_secret(Bob.address,secret)
#Alice sends 5 algos to Bob
print("Alice sends 5 algos to Bob")
txs=Alice.send(Bob.address,5,create=True)
Bob.receive(Alice.address,txs,signed=False)
txs=Bob.send(Alice.address)
Alice.receive(Bob.address,txs,signed=True)

# Closing step - OnChain 
Bob.presentation(Alice.address,0) #cost 6000 microalgo


#Alice gives back the secret and can punish Bob taking all the money
Alice.close_channel(Bob.address,0) #cost 1000 microAlgos
Alice.delete(Bob.address) """


