from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from algosdk import mnemonic,account, atomic_transaction_composer,transaction
from utilites.util import get_accounts, get_algod_client
from utilites.deserialize import deserialize
from Client import client
from MyTransaction import MyTransaction

fd = open("/home/ale/Desktop/memonic.txt")

memon = fd.read()
m=memon.replace(',','')
print(m)
pk =mnemonic.to_private_key(m)
address= account.address_from_private_key(pk)
signer = atomic_transaction_composer.AccountTransactionSigner(pk)
algod_token = "bZbXNYpcwa6gEAFq20RpZ341qt6IdNn9IzVuEFJj"
algod_address = "https://testnet-algorand.api.purestake.io/ps2"

headers = {
   "X-API-Key": algod_token,
}

c = client(address,pk,signer,algod_token,algod_address,headers)







