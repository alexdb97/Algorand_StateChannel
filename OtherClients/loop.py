'''To make the network dynamic we need a client that makes transactions 
in order to going on with rounds and update the current state of the Blockchain'''
import time
from algosdk import transaction, abi, logic, util
from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client

import signal
import sys

count=0

def handler(signum, frame):
    signame = signal.Signals(signum).name
    print(f'Signal handler called with signal {signame} ({signum})')
    print(f'number of transaction sent {count}')
    sys.exit(0)


signal.signal(signal.SIGINT, handler)



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
acct2 = accts.pop()
acct3 = accts.pop()

private_key, address,signer1 = acct3.private_key, acct3.address,acct3.signer

while(1):

    sp=algod_client.suggested_params()
    tx = transaction.PaymentTxn(address,sp=sp,receiver=address,amt=util.algos_to_microalgos(1))
    txs = tx.sign(private_key)
    algod_client.send_transaction(txs)
    time.sleep(0.5)
    count = count+1
   











