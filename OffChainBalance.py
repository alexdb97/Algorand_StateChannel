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
        self.digest=None
        self.algod=algod
        self.transactions = []
        self.address1 = address1
        self.address2 = address2
        self.amnt1 = 0
        self.amnt2 = 0
        self.index=0



    """
    deposit_transaction, is the first transaction that will fill the current balance.

    :param value: the amount of money that is inserted inside the balance
    """ 
    def deposit_transaction(self,value):
        hash = hashlib.sha3_256()
        random_bytes = secrets.token_bytes(32)
        hash.update(random_bytes)
        digest1 = hash.digest()
        
  

        if(self.algod.address==self.address1):
            self.amnt1=self.amnt1+value
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,digest1,self.digest)
            tx.sign(self.algod.signer,self.algod.address)
            self.secrets.append([random_bytes,None])
            return tx.serialize()
        else:
            self.amnt2=self.amnt2+value
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,self.digest,digest1)
            tx.sign(self.algod.signer,self.algod.address)
            self.secrets.append([None,random_bytes])
            return tx.serialize()


    """
    create_transaction will check the current balance and create the transaction.

    :param value: the amount of money that is inserted inside the balance
    """ 
    def create_transaction(self,value,deposit=False):
        hash = hashlib.sha3_256()
        random_bytes = secrets.token_bytes(32)
        hash.update(random_bytes)
        digest1 = hash.digest()
     
    
        if(self.algod.address==self.address1):
            if(self.amnt1>=value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1-value,self.amnt2+value,digest1,self.digest)
                tx.sign(self.algod.signer,self.address1)
                self.secrets.append([random_bytes,None])
                self.digest=None
                return tx.serialize()
        else:
             if(self.amnt2>=value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1+value,self.amnt2-value,self.digest,digest1)
                tx.sign(self.algod.signer,self.address2)
                self.secrets.append([None,random_bytes])
                self.digest=None
            
                return tx.serialize()


    """
    sign_transaction will sign the transaction provided

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
    get_transaction will return the last transaction inserted from the list of the transaction, if index is specified it will

    return the transaction at the position given.

    :param index: position 
    """
    def get_transaction(self, index=-1):
        tx: MyTransaction = self.transactions[index]
        return tx

    
    """
    get_my_secret will return the last secret to share with the other counterpart

    """
    def get_my_secret(self):
        if(self.algod.address==self.address1):
            return self.secrets[-2][0]
        else:
            return self.secrets[-2][1]
    
    """
    get_secret will return the secret with the index from the list of secrets, if index is specified it will

    return the secret at the position given.

    :param index: position 
    """
    def get_secret(self,index):
        if(self.algod.address==self.address1):
            return self.secrets[index][1]
        else:
            return self.secrets[index][0]

                    

    """
    insert_secret will append to the list of secrets the last one.

    :param  secret: secret
    """
    def insert_secret(self,secret):
        if(self.algod.address==self.address1):
            self.secrets[-2][1]=secret
        else:
            self.secrets[-2][0]=secret
    

    def get(self):
        import base64
        f=lambda a : [base64.b64encode(a[0]).decode('UTF-8'),base64.b64encode(a[1]).decode('UTF-8')]
        r = map(f,self.secrets[0:-1])
        return list(r)
    
    """
    insert_digest will update the digest on the state

    :param  secret: digest
    """
    def insert_digest(self,digest):
        self.digest=digest

    """
    generate_digest will generate a digest to send to the counterpart that is packing the transaction, it will return the new digest and store the secret
    """
    def generate_digest(self):

        hash = hashlib.sha3_256()
        secret = secrets.token_bytes(32)
        hash.update(secret)
        digest = hash.digest()

         
        if(self.algod.address==self.address1):
            self.secrets.append([secret,None])
        else:
             self.secrets.append([None,secret])
        
        
        return digest


 
    




   

