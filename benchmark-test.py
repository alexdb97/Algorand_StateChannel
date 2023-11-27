from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from algosdk import mnemonic,account, atomic_transaction_composer,transaction
from  Client import Client
from utilites.time_dec import bench
import os
import csv

from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,      
)
#REPLACE WITH THE MEMONIC OF YOUR ACCOUNTS
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
""""
    This is an example of tokenAPI.txt 
    (two lines separated by newline one the access token the second the url ) 
    you can create it on the site below purestake.io wheneaver the service is open :D:
    b**************************************j
    https://testnet-algorand.api.purestake.io/ps2

"""
#REPLACE WITH YOUR ACCESS TOKEN
with open("/home/ale/Desktop/Access/tokenAPI.txt") as fd:
    stri = fd.readline()
    algod_token=stri.replace('\n','')
    stri=fd.readline()
    algod_url=stri.replace('\n','')
    print(algod_url)
    fd.close()


headers = {
   "X-API-Key": algod_token,
}

# On chain transactions, it is counted the fee that is only the sum of  sum+=1000 microalgos per transaction.
# it is counted the time with the decorator bench.
@bench
def Onchain(number,wait=True):
    total_fee=0
    for i in range (0,number):
        alg = algod.AlgodClient(algod_token,algod_url,headers)
        sp = alg.suggested_params()
        tx = transaction.PaymentTxn(addressA,sp,addressB,1,note=str(i+number).encode('utf-8'))
        txs = tx.sign(pkA)
        total_fee = total_fee+tx.fee
        txn_res=alg.send_transaction(txs)
        if(wait):
            res = transaction.wait_for_confirmation(alg,txn_res,1000)
    
    return number,total_fee

    

# Payment Channel solution, the fee is constant to 15000 microalgos indipendently from number of transaction.
# Also this function is decorated with the decorator.
@bench
def state_channel(number):
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
        txs=Alice.send(Bob.address,10000,create=True)
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
    return number,15000


if __name__=="__main__":

    if("stats" not in os.listdir("./")):
        os.mkdir("./test-net-data")

    n_txs = [1,5,15,20,50,100]
    for i in n_txs:
        print(Onchain(i))

    with open("./test-net-data/onchain.csv","w") as fd:
        csv_writer=csv.writer(fd)
        for i in n_txs:
            csv_writer.writerow(Onchain(i))
    
    #In this on-chain consecutive we don't wait for the confirmation of
    #the transaction
    with open("./test-net-data/onchain_consecutive.csv","w") as fd:
        csv_writer=csv.writer(fd)
        for i in n_txs:
            csv_writer.writerow(Onchain(i,wait=False))

    
    with open("./test-net-data/state_channel.csv","w") as fd:
        csv_writer=csv.writer(fd)
        for i in n_txs:
            csv_writer.writerow(state_channel(i))
        





