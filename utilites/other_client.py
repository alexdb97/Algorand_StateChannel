'''To make the network dynamic we need a client that makes transactions 
in order to going on with rounds and update the current state of the Blockchain'''
import time
from algosdk import transaction, abi, logic, util
from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client


'''The (time) rounds in the local blockchain are dependent on the transaction
sent to the local blockcahin we need a function that loops and does trivial transaction

'''
def aux_other_client():


    #Create a new algod client, configured to connect to our local sandbox
    algod_address= "http://localhost:4001"
    algod_token="a"*64
    algod_client=algod.AlgodClient(algod_token,algod_address)

    # Create a new client with an alternate api key header
    special_algod_client = algod.AlgodClient(
    "", algod_address, headers={"X-API-Key": algod_token})

    #example: ALGOD_CREATE_CLIENT
    algod_client = get_algod_client()
    accts = get_accounts()

    acct1 = accts.pop()
    acct2 = accts.pop()
    acct3 = accts.pop()

    private_key, address,signer1 = acct3.private_key, acct3.address,acct3.signer
    count=0

    while(1):

        sp=algod_client.suggested_params()
        tx = transaction.PaymentTxn(address,sp=sp,receiver=address,amt=util.algos_to_microalgos(1))
        txs = tx.sign(private_key)
        algod_client.send_transaction(txs)
        time.sleep(2)
        count = count+1