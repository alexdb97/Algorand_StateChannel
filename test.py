from ast import Dict
from base64 import b64decode
import base64
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client
from utilites.deserialize import deserialize
from Client import Client
from MyTransaction import MyTransaction
import time
import unittest
class Test(unittest.TestCase):

    def __init__(self,methodName='runTest') -> None:
        
        # Call the superclass constructor with the methodName parameter
        super().__init__(methodName=methodName)

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
        private_key, self.address,signer1 = acct1.private_key, acct1.address,acct1.signer


        acct2 = accts.pop()
        private_key2,self.address2,signer2 = acct2.private_key,acct2.address,acct2.signer
        account_info = algod_client.account_info(self.address)

        self.c1 = Client(self.address,private_key,signer1,algod_token,algod_address,headers={"X-API-Key": algod_token})
        self.c2 = Client(self.address2,private_key2,signer2,algod_token,algod_address,headers={"X-API-Key": algod_token})

    '''
    First test example : c1 opens
    '''
    def test_example(self):

        account_info: Dict[str, Any] = self.c1.account_info(self.c1.address)
        print(f"Account balance address: {account_info.get('amount')} microAlgos")

        account_info: Dict[str, Any] = self.c2.account_info(self.c2.address)
        print(f"Account balance address2: {account_info.get('amount')} microAlgos")

        contract,appid,appaddr=self.c2.open_channel(self.address)
        self.c1.insert_channel(contract,appid,appaddr,self.address2)


        #First step Deposit Transaction, c2 must give a signed transaction - OffChain
        txs=self.c1.send(self.address2,100,deposit=True,create=True)
        self.c2.receive(self.address,txs,signed=False)
        txs=self.c2.send(self.address)
        self.c1.receive(self.address2,txs,signed=True)
        #(On chain) deposit
        self.c1.deposit(100,self.address2)


        #Second step
        #Sending the secret of the former transaction - Offchain
        s=self.c1.send_secret(self.address2)
        self.c2.receive_secret(self.address,s)
        # C1 --(10 algos)-->C2 - Offchain
        txs=self.c1.send(self.address2,50,create=True)
        self.c2.receive(self.address,txs)
        txs=self.c2.send(self.address)
        self.c1.receive(self.address2,txs,signed=True)

        #Third step
        #Sending the secret of the former transaction -Offchain
        s=self.c1.send_secret(self.address2)
        self.c2.receive_secret(self.address,s)
        # C2 --(1 algos)-->C1 - Offchain
        txs=self.c2.send(self.address,5,create=True)
        self.c1.receive(self.address2,txs)
        txs=self.c1.send(self.address2)
        self.c2.receive(self.address,txs,signed=True)

       
        # Closing step - OnChain 
        self.c1.presentation(self.address2)
        #self.c1.close_channel(self.address2)
        

        account_info: Dict[str, Any] = self.c1.account_info(self.c1.address)
        print(f"Account balance address: {account_info.get('amount')} microAlgos")

        account_info: Dict[str, Any] = self.c2.account_info(self.c2.address)
        print(f"Account balance address2: {account_info.get('amount')} microAlgos")
        


if __name__ == '__main__':
    unittest.main()


