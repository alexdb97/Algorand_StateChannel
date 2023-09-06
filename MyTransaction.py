
import base64
from typing import cast
from nacl.signing import SigningKey
from algosdk import  util,encoding
import json

#from Crypto.Hash import keccak
from pyteal import *


from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner)

class MyTransaction():

  
    def __init__(self,index=None,addr1=None,addr2=None,amnt1=0,amnt2=0,secret=None,secret_proposer=None):
        
        self.index=index
        self.addr1=addr1
        self.addr2 = addr2
        self.amnt1 = util.algos_to_microalgos(amnt1)
        self.amnt2 =util.algos_to_microalgos(amnt2)
        self.secret = secret
        self.secret_proposer = secret_proposer
        self.signature:[bytes] = [None]*2
    

    def sign(self,signer,address):

        if(self.signature.count(None)==0):
            raise TooManySignerException()

        b64_pk = cast(AccountTransactionSigner,signer).private_key
        msg = bytes(self.__body_to_bytearray())
        pk = list(base64.b64decode(b64_pk))
        signing_key = SigningKey(bytes(pk[:32]))
        signed =signing_key.sign(msg).signature

        if(address==self.addr1):
            d = signed.decode('latin-1')
            self.signature[0]=d
        elif(address==self.addr2):
            d = signed.decode('latin-1')
            self.signature[1]=d


    def contract_payload(self):
        payload = self.__body_to_bytearray()
        app:bytes = self.signature[0]
        payload.extend(app.encode('latin-1'))
        app = self.signature[1]
        payload.extend(app.encode('latin-1'))
        return payload            


    def __body_to_bytearray(self):
        body = bytearray()
        body.extend(self.index.to_bytes(8,'big'))
        body.extend(self.amnt1.to_bytes(8,'big'))
        body.extend(self.amnt2.to_bytes(8,'big'))
        body.extend(self.secret.to_bytes(8,'big'))
        body.extend(encoding.decode_address(self.secret_proposer))
        return body
    


    def serialize(self):
        attributes_to_include = ['index', 'addr1', 'addr2', 'amnt1', 'amnt2', 'secret', 'secret_proposer']
        js = {attr: getattr(self, attr) for attr in attributes_to_include}
        js['sig1'] = self.signature[0]
        js['sig2'] = self.signature[1]

        ser =json.dumps(js)
        return ser
    

    def deserialize(self,str):
        d = json.loads(str)
        attributes = ['index', 'addr1', 'addr2', 'amnt1', 'amnt2', 'secret', 'secret_proposer']
        for attr in attributes:
            setattr(self,attr,d[attr])
        self.signature[0]=d['sig1']
        self.signature[1]=d['sig2']
        

 
class TooManySignerException(Exception):
    def __init__(self, message, errors):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        
