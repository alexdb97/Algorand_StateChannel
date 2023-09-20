from MyTransaction import MyTransaction
import secrets
import hashlib

class OffChainBalance():



    """
    OffChainBalance class trace all the exchange operations done via offchain channel, therefore it will update the state of transaction
    
    and the current balance.
    """ 


    def __init__(self,algod,address1,address2) -> None:
        self.secrets = []
        self.algod=algod
        self.transactions = []
        self.address1 = address1
        self.address2 = address2
        self.amnt1 = 0
        self.amnt2 = 0
        self.index=0



    """
    deposit_transaction, is the first transaction that will fill the current balance.


    :param algod: an istance of the client is passed for validating the transaction and discriminate the balance
    :param value: the amount of money that is inserted inside the balance
    """ 
    def deposit_transaction(self,value):
        hash = hashlib.sha3_256()
        random_bytes = secrets.token_bytes(32)
        hash.update(random_bytes)
        digest = hash.digest()
        self.secrets.append(random_bytes)

        if(self.algod.address==self.address1):
            self.amnt1=self.amnt1+value
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,digest,self.address1)
            tx.sign(self.algod.signer,self.address1)
            return tx.serialize()
        else:
            self.amnt2=self.amnt2+self.amnt2
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,digest,self.address2)
            tx.sign(self.algod.signer,self.address2)
            return tx.serialize()
            

    """
    create_transaction will check the current balance and create the transaction.

    :param algod: an istance of the client is passed for validating the transaction and discriminate the balance
    :param value: the amount of money that is inserted inside the balance
    """ 
    def create_transaction(self,value):
        hash = hashlib.sha3_256()
        random_bytes = secrets.token_bytes(32)
        hash.update(random_bytes)
        digest = hash.digest()
        self.secrets.append(random_bytes)
    
        if(self.algod.address==self.address1):
            if(self.amnt1>value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1-value,self.amnt2+value,digest,self.address1)
                tx.sign(self.algod.signer,self.address1)
                return tx.serialize()
        else:
             if(self.amnt2>value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1+value,self.amnt2-value,digest,self.address2)
                tx.sign(self.algod.signer,self.address2)
                return tx.serialize()


    """
    sign_transaction will sign the transaction provided

    :param algod: an istance of the client is passed for validating the transaction
    :param json_tx: json format of the transaction
    """ 
    def sign_transaction(self,json_tx):
        #Chek all the parameter
        tx = MyTransaction()
        tx.deserialize(json_tx)
        tx.sign(self.algod.signer,self.algod.address)
        return tx.serialize()

        
    """
    insert_transaction will append to the list of the transaction the last one.

    :param json_tx: json format of the transaction
    """
    def insert_transaction(self,json_tx):
        #Insert the transaction in the list of transaction authenticated from both
        tx = MyTransaction()
        tx.deserialize(json_tx)
        self.index = tx.get_index()
        self.amnt1=tx.get_amnt1()
        self.amnt2 = tx.get_amnt2()
        self.transactions.append(tx)


    """
    get_transaction will retrive from the list of the transaction the last transaction inserted, if index is specified it will

    retrive the transaction at the position given.

    :param index: position of the transaction to retrive
    """
    def get_transaction(self, index=None):
        try:
            index = index or len(self.transactions)-1  # Use 0 as the default index if index is None or falsy
            tx: MyTransaction = self.transactions.pop(index)
            return tx
        except (IndexError):
            raise ValueError("Index is out of range or None for self.transactions.")

    def get_secret(self,value):
        return self.secrets[value]
    
    def insert_secret(self,secret):
        self.secrets.append(secret)

