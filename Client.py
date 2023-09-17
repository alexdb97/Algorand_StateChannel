from base64 import b64decode
import base64
from typing import Dict
from algosdk.v2client import algod
from utilites.deserialize import deserialize
from ChainChannel import ChainChannel
from OffChainBalance import OffChainBalance

class Client(algod.AlgodClient):

    def __init__(self,address,private,signer,algod_token: str, algod_address: str, headers: Dict[str, str]| None = None ):
        super().__init__(algod_token, algod_address, headers)
        self.address=address
        self.private=private
        self.signer = signer
        self.opened_channels = dict()
        self.off_channel = dict()
     
    #Chain Operations ---------------------------------------------------------------------------
    def open_channel(self,counterpart):

        with open("./SmartContract/artifacts/approval.teal") as f:
            tmp=f.read()
            compiled = self.compile(tmp)
            app_pro = base64.b64decode(compiled["result"])

        with open("./SmartContract/artifacts/clear.teal") as f:
            tmp=f.read()
            compiled = self.compile(tmp)
            app_clear = base64.b64decode(compiled["result"])


        with open("./SmartContract/artifacts/contract.json") as f:
            tmp=f.read()
            contract = deserialize(tmp)

        c = ChainChannel(app_clear,app_pro,contract,counterpart)
        appid,address= c.open_channel(self)
        self.opened_channels[counterpart]=c

        o = OffChainBalance(self.address,counterpart)
        self.off_channel[counterpart]=o
        
        return contract,appid,address


    def insert_channel(self,contract,app_id,app_address,counterpart):
        #Verify the state of the channel and the code of it is a part that will come later
        c = ChainChannel(contract=contract,app_id=app_id,app_address=app_address,counterpart=counterpart)
        self.opened_channels[counterpart]=c
        o = OffChainBalance(counterpart,self.address)
        self.off_channel[counterpart]=o

    def deposit(self,value,counterpart):
        c:ChainChannel =self.opened_channels[counterpart]
        c.deposit_chain(value,self)
        off:OffChainBalance = self.off_channel[counterpart]
        

    def presentation(self,address,transaction=None):
        c:ChainChannel = self.opened_channels[address]
        c.tryClose(self.off_channel[address].get_transaction().get_contract_payload(),self)
    
    def close_channel(self,address,value=0):
        c:ChainChannel = self.opened_channels[address]
        c.closeChannel(self,value)
    
    #------------------------------------------------------------------------------------------    


    #Off-Chain operations --------------------------------------------------------------
     
    def send(self,counterpart,value=None,deposit=False,create=False):
        offc:OffChainBalance=self.off_channel[counterpart]
        
        #If it is a new transaction
        if create:
            if deposit:
                json_tx =offc.deposit_transaction(self,value)
                return json_tx
            json_tx = offc.create_transaction(self,counterpart,value)
            return json_tx
        
        return offc.get_transaction().serialize()
    
    def receive(self,counterpart,tx,signed=False):
        offc:OffChainBalance = self.off_channel[counterpart]
        if signed:
            
            offc.insert_transaction(tx)
        else:
            txs = offc.sign_transaction(self,tx)
            offc.insert_transaction(txs)

    #--------------------------------------------------------------------------------------