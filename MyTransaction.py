
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

    """
    MyTransaction class implements the customed transaction, it will interact with the smart contract,

    this class will provide methods for creating, validate, and store the transaction without lousing the informations

    and security inside. MyTransaction are slightly different from the classic transaction style, infact it will contains

    the balance of both accounts.
    """
    def __init__(self,index=None,addr1=None,addr2=None,amnt1=0,amnt2=0,secret=None,secret2=None,app_id=None):
        
        self.index=index
        self.addr1=addr1
        self.app_id=app_id
        self.addr2 = addr2
        self.amnt1 = amnt1
        self.amnt2 =amnt2
        self.secret = secret
        self.secret2=secret2
        self.signature:[bytes] = [None]*2
    
    """
    sign method will extract from the transaction the so called body, it is formed by the main informations of the transaction,

    the method  will add to the transaction the signature of the caller that could be one of the two address.


    :param signer: the private key of the address
    :param address: address of the signer
    """ 
    def sign(self,signer,address):

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

    
    """
    serialize method is done for putting the state of the transaction in a json format, it is done for storing the transaction

    or for sending it trought a connection.

    return : json_transaction
    """ 
    def serialize(self):
        attributes_to_include = ['index','app_id','addr1', 'addr2', 'amnt1', 'amnt2']
        js = {attr: getattr(self, attr) for attr in attributes_to_include}
        js['secret']=self.secret.decode('latin-1')
        js['secret2']=self.secret2.decode('latin-1')
        js['sig1'] = self.signature[0]
        js['sig2'] = self.signature[1]
        
        ser =json.dumps(js)
        
        return ser
    
    """
    deserialize is the inverse process of serialization, therefore it takes a string in a json format, then all the information

    are transfered to the internal state of the object.
    
    :param json_tx: json transaction
    """
    def deserialize(self,str):
       
        d = json.loads(str)
        attributes = ['index', 'app_id','addr1', 'addr2', 'amnt1', 'amnt2']
        for attr in attributes:
            setattr(self,attr,d[attr])
        self.secret = d['secret'].encode('latin-1')
        self.secret2 = d['secret2'].encode('latin-1')        
        self.signature[0]=d['sig1']
        self.signature[1]=d['sig2']
    
    """
    contract_payload is the function that transform the transaction in a byte transaction, the one that is sent to the

    Smart Contract.

    return: byte payload
    """
    def contract_payload(self):
        payload = self.__body_to_bytearray()
        app:bytes = self.signature[0]
        payload.extend(app.encode('latin-1'))
        app = self.signature[1]
        payload.extend(app.encode('latin-1'))
       
        return payload  
    
    """
    get_index: getter method for retriving the index 

    return: index
    """
    def get_index(self):
        return self.index
    
    
    def get_amnt1(self):
        return self.amnt1
    

    """
    get_amnt2: getter method for retriving the amount of the first address2

    return: amnt2
    """
    def get_amnt2(self):
        return self.amnt2
    

    """
    body_to_bytearray is a private method of the class used for extracting the body of the transaction, it is used in 
    
    the sign method.

    return: body
  
    """
    def __body_to_bytearray(self):
        body = bytearray()
        body.extend(self.index.to_bytes(8,'big'))
        body.extend(self.amnt1.to_bytes(8,'big'))
        body.extend(self.amnt2.to_bytes(8,'big'))
        body.extend(self.secret)
        body.extend(self.secret2)
        body.extend(self.app_id.to_bytes(8,'big'))
        return body
        

 

        