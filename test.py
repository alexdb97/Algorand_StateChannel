from ast import Dict
from base64 import b64decode
from typing import Any
from algosdk.v2client import algod
from utilites.util import get_accounts, get_algod_client
from utilites.deserialize import deserialize
from Client import Client
from MyTransaction import MyTransaction
import time
import unittest
import math

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

        self.Alice = Client(self.address,private_key,signer1,algod_token,algod_address,headers={"X-API-Key": algod_token})
        self.Bob = Client(self.address2,private_key2,signer2,algod_token,algod_address,headers={"X-API-Key": algod_token})

    '''
    First test example :  Alice puts the money, Bob goes away attempt to let her money stucked
    '''
    def test_open_and_leave(self):

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t1 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t1 = account_info.get('amount')

        contract,appid,appaddr=self.Alice.open_channel(self.address2) #Cost 2000 microAlgos
        self.Bob.insert_channel(contract,appid,appaddr,self.address)


        #First step Deposit Transaction, Bob must give a signed transaction - OffChain
        txs=self.Alice.send(self.address2,100,deposit=True,create=True)
        self.Bob.receive(self.address,txs,signed=False)
        txs=self.Bob.send(self.address)
        self.Alice.receive(self.address2,txs,signed=True)
        #(On chain) deposit
        self.Alice.deposit(100,self.address2) #cost 2000 microAlgos

        # Closing step - OnChain 
        self.Alice.presentation(self.address2) #cost 6000 microalgos

        #In this case after the presentation he must wait normally 24h, as we are testing
        #the smart contract it is set 20 seconds on the smart contract
        time.sleep(10)
        self.Alice.close_channel(self.address2) #cost 1000 microAlgos
        self.Alice.delete(self.address2) #cost 1000 microalgos
        
        

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t2 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t2 = account_info.get('amount')

        #Bob has no costs, alices will have the money back and will pay the cost of all channels operations
        assert( amntBob_t2-amntBob_t1==0  and  amntAlice_t2-amntAlice_t1==-15000)
        

    '''
    Second test example : After opening the channel there will be some ping pong transactions and finally close the

    the channel without any fraud
    '''
    def test_normal_use(self):

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t1 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t1 = account_info.get('amount')

        contract,appid,appaddr=self.Alice.open_channel(self.address2) #Cost 2000 microAlgos
        self.Bob.insert_channel(contract,appid,appaddr,self.address)


        #First step Deposit Transaction, Bob must give a signed transaction - OffChain
        txs=self.Alice.send(self.address2,100,deposit=True,create=True)
        self.Bob.receive(self.address,txs,signed=False)
        txs=self.Bob.send(self.address)
        self.Alice.receive(self.address2,txs,signed=True)
        #(On chain) deposit
        self.Alice.deposit(100,self.address2) #cost 2000 microAlgos

        #Before of the second transaction there will be the phase of secret reveal
        secret=self.Alice.send_secret(self.address2)
        self.Bob.receive_secret(self.address,secret)
        #Alice gives 50 algos to Bob
        txs=self.Alice.send(self.address2,50,create=True)
        self.Bob.receive(self.address,txs,signed=False)
        txs=self.Bob.send(self.address)
        self.Alice.receive(self.address2,txs,signed=True)

        #Before of the transaction there will be the phase of secret reveal
        secret=self.Alice.send_secret(self.address2)
        self.Bob.receive_secret(self.address,secret)
        #Bob gives 25 algos to Alice
        txs=self.Bob.send(self.address,25,create=True)
        self.Alice.receive(self.address2,txs,signed=False)
        txs=self.Alice.send(self.address2)
        self.Bob.receive(self.address,txs,signed=True)



        # Closing step - OnChain 
        self.Alice.presentation(self.address2) #cost 6000 microalgos

        self.Alice.close_channel(self.address2) #cost 1000 microAlgos
        self.Alice.delete(self.address2)
        
        
        

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t2 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t2 = account_info.get('amount')

        assert(amntBob_t2-amntBob_t1==25000000 and amntAlice_t2-amntAlice_t1==-25015000)
        


    '''
    Third test example : After opening the channel there will be some ping pong transactions and finally Bob will put the first

    transactions that it is favorable for him
    '''
    def test_open_skam(self):

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t1 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t1 = account_info.get('amount')

        contract,appid,appaddr=self.Alice.open_channel(self.address2) #Cost 2000 microAlgos
        self.Bob.insert_channel(contract,appid,appaddr,self.address)


        #First step Deposit Transaction, Alice must give back a signed transaction before opening - OffChain
        txs=self.Bob.send(self.address,100,deposit=True,create=True)
        self.Alice.receive(self.address2,txs,signed=False)
        txs=self.Alice.send(self.address2)
        self.Bob.receive(self.address,txs,signed=True)
        #(On chain) deposit
        self.Bob.deposit(100,self.address) #cost 2000 microAlgos

        #Before of the second transaction there will be the phase of secret reveal
        secret=self.Bob.send_secret(self.address)
        self.Alice.receive_secret(self.address2,secret)
        #Alice gives 50 algos to Bob
        txs=self.Bob.send(self.address,50,create=True)
        self.Alice.receive(self.address2,txs,signed=False)
        txs=self.Alice.send(self.address2)
        self.Bob.receive(self.address,txs,signed=True)

        #Before of the transaction there will be the phase of secret reveal
        secret=self.Bob.send_secret(self.address)
        self.Alice.receive_secret(self.address2,secret)
        #Bob gives 25 algos to Alice
        txs=self.Alice.send(self.address2,25,create=True)
        self.Bob.receive(self.address,txs,signed=False)
        txs=self.Bob.send(self.address)
        self.Alice.receive(self.address2,txs,signed=True)

        


        # Closing step - OnChain 
        self.Bob.presentation(self.address,0) #cost 6000 microalgos

        #Alice tries to close the contract should raise the (exception gloabal_round<future_accepts)
        with self.assertRaises(Exception):
            self.Bob.close_channel(self.address)

        #Alice gives back the secret and can punish Bob taking all the money
        self.Alice.close_channel(self.address2,0) #cost 1000 microAlgos
        self.Alice.delete(self.address2)
       
        
        

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t2 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t2 = account_info.get('amount')

     
        assert((amntBob_t2-amntBob_t1)==-(100000000+8000) and (amntAlice_t2-amntAlice_t1)==(101000000-1006000))


    '''
    Fourth test example : Trying to forge a different transaction with different values
    '''
    def test_open_forging(self):

        account_info: Dict[str, Any] = self.Alice.account_info(self.Alice.address)
        amntAlice_t1 = account_info.get('amount')

        account_info: Dict[str, Any] = self.Bob.account_info(self.Bob.address)
        amntBob_t1 = account_info.get('amount')

        contract,appid,appaddr=self.Bob.open_channel(self.address) #Cost 2000 microAlgos
        self.Alice.insert_channel(contract,appid,appaddr,self.address2)


        #First step Deposit Transaction, Alice must give back a signed transaction before opening - OffChain
        txs=self.Bob.send(self.address,100,deposit=True,create=True)
        self.Alice.receive(self.address2,txs,signed=False)
        txs=self.Alice.send(self.address2)
        self.Bob.receive(self.address,txs,signed=True)
        #(On chain) deposit
        self.Bob.deposit(100,self.address) #cost 2000 microAlgos

        #Before of the second transaction there will be the phase of secret reveal
        secret=self.Bob.send_secret(self.address)
        self.Alice.receive_secret(self.address2,secret)
        #Alice gives 50 algos to Bob
        txs=self.Bob.send(self.address,60,create=True)

        #Alice before storing the transaction will change the values
        txs=txs.replace("60000000","100000000")
        txs=txs.replace("40000000","0")

        self.Alice.receive(self.address2,txs,signed=False)
        txs=self.Alice.send(self.address2)
        self.Bob.receive(self.address,txs,signed=True)

     
        #Presentation raise the exception on Verfication of signature
        with self.assertRaises(Exception): 
            self.Bob.presentation(self.address) #cost 6000 microalgos

        #close channel raise the exception on assertion on the flag is not possible to close witthout
        # the presentation step
        with self.assertRaises(Exception): 
            self.Bob.close_channel(self.address2) #cost 1000 microAlgos
        
        #Delete reaise the exception for the same reason of the former operations
        with self.assertRaises(Exception): 
            self.Alice.delete(self.address2)
       

    
       
if __name__ == '__main__':
    unittest.main()


