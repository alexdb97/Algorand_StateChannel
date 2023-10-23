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

#Reading the access token and the endpoint testnet
with open("/home/ale/Desktop/Access/tokenAPI.txt") as fd:
    str = fd.readline()
    algod_token=str.replace('\n','')
    str=fd.readline()
    algod_url=str.replace('\n','')
    print(algod_url)
    fd.close()


headers = {
   "X-API-Key": algod_token,
}

def Onchain(number):
    #10 interaction with the blockchain
    for i in range (0,number):
        alg = algod.AlgodClient(algod_token,algod_url,headers)
        sp = alg.suggested_params()
        tx = transaction.PaymentTxn(addressA,sp,addressB,1)
        txs = tx.sign(pkA)
        txn_res=alg.send_transaction(txs)
        res = transaction.wait_for_confirmation(alg,txn_res,1000)


def State_Channel_Payments(number):
    Alice = Client(addressA,pkA,signerA,algod_token,algod_url,headers)
    Bob = Client(addressB,pkB,signerB,algod_token,algod_url,headers)

    contract,appid,appaddr=Alice.open_channel(Bob.address) #Cost 2000 microAlgos
    print("Application identifier :",appid)
    Bob.join_channel(contract,appid,appaddr,Alice.address)
    #Create the cotract
    #First step Deposit Transaction, Bob must give a signed transaction - OffChain
    digest = Bob.send_digest(Alice.address)
    Alice.receive_digest(Bob.address,digest)

    txs=Alice.send(Bob.address,10**6,deposit=True,create=True)
    Bob.receive(Alice.address,txs,signed=False)
    txs=Bob.send(Alice.address)
    Alice.receive(Bob.address,txs,signed=True)
    #(On chain) deposit
    Alice.deposit(10**6,Bob.address) #cost 2000 microAlgos

    for i in range(0,number):
        #Bob gives the new secret
        digest = Bob.send_digest(Alice.address)
        Alice.receive_digest(Bob.address,digest)
        #The transaction is created and sent to Bob
        txs=Alice.send(Bob.address,1,create=True)
        Bob.receive(Alice.address,txs,signed=False)
        #Bob gives back the transaction signed
        txs=Bob.send(Alice.address)
        Alice.receive(Bob.address,txs,signed=True)
        #Bob gives the revocation secret of the previous transaction
        secret=Bob.send_secret(Alice.address)
        Alice.receive_secret(Bob.address,secret)
        #Alice gives the revocation secret of the previous transaction
        secret=Alice.send_secret(Bob.address)
        Bob.receive_secret(Alice.address,secret)
        
    # Closing step - OnChain 
    Alice.presentation(Bob.address) #cost 6000 microalgos
    Bob.close_channel(Alice.address) #cost 1000 microAlgos
    Alice.delete(Bob.address)


#State_Channel_Payments(1000)
Onchain(1000)



