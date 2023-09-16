
import base64
from typing import cast
from nacl.signing import SigningKey
from algosdk import  util,encoding
import json
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
  
    def __init__(self,index=None,addr1=None,addr2=None,amnt1=0,amnt2=0,secret=None,secret_proposer=None):
        
        self.index=index
        self.addr1=addr1
        self.addr2 = addr2
        self.amnt1 = util.algos_to_microalgos(amnt1)
        self.amnt2 =util.algos_to_microalgos(amnt2)
        self.secret = secret
        self.secret_proposer = secret_proposer
        self.signature:[bytes] = [None]*2
    

    """
    sign method will extract from the transaction the so called body, it is formed by the main informations of the transaction,

    the method  will add to the transaction the signature of the caller that could be one of the two address.


    :param signer: the private key of the address
    :param address: address of the signer
    """ 
    def sign(self,signer,address):

        if(self.signature.count(None)==0):
            raise TooManySignerException("It is not possible to sign more than 2 times")

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
        attributes_to_include = ['index', 'addr1', 'addr2', 'amnt1', 'amnt2', 'secret', 'secret_proposer']
        js = {attr: getattr(self, attr) for attr in attributes_to_include}
        js['sig1'] = self.signature[0]
        js['sig2'] = self.signature[1]

        json_transaction =json.dumps(js)
        return json_transaction
    
    """
    deserialize is the inverse process of serialization, therefore it takes a string in a json format, then all the information

    are transfered to the internal state of the object.
    
     :param str: json transaction
    """ 
    def deserialize(self,str):
        d = json.loads(str)
        attributes = ['index', 'addr1', 'addr2', 'amnt1', 'amnt2', 'secret', 'secret_proposer']
        for attr in attributes:
            setattr(self,attr,d[attr])
        self.signature[0]=d['sig1']
        self.signature[1]=d['sig2']


    """
    get_contract_payload is the function that transform the transaction in a byte transaction, the one that is sent to the

    Smart Contract.


    return: byte payload
    """
    def get_contract_payload(self):
    
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
    
    """
    get_amnt1: getter method for retriving the amount of the first address1

    return: amnt1
    """
    def get_amnt1(self):
        return util.microalgos_to_algos(self.amnt1)
    
    """
    get_amnt2: getter method for retriving the amount of the first address2

    return: amnt2
    """
    def get_amnt2(self):
        return util.microalgos_to_algos(self.amnt2)
    

    """
    body_to_bytearray is a private method of the class used for extracting the body of the transaction, it is used in the sign method.


    return: body
  
    """
    def __body_to_bytearray(self):
        body = bytearray()
        body.extend(self.index.to_bytes(8,'big'))
        body.extend(self.amnt1.to_bytes(8,'big'))
        body.extend(self.amnt2.to_bytes(8,'big'))
        body.extend(self.secret.to_bytes(8,'big'))
        body.extend(encoding.decode_address(self.secret_proposer))
        return body
        

 
class TooManySignerException(Exception):
    def __init__(self, message, errors):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)




        
