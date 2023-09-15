from MyTransaction import MyTransaction

import sys

class OffChannel():

    def __init__(self,address1,address2) -> None:
        self.transactions = []
        self.address1 = address1
        self.address2 = address2
        self.amnt1 = 0
        self.amnt2 = 0
        self.index=0



    def deposit_transaction(self,algod,value):
        
        if(algod.address==self.address1):
            self.amnt1=self.amnt1+value
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,10,self.address1)
            tx.sign(algod.signer,self.address1)
            return tx.serialize()
        else:
            self.amnt2=self.amnt2+self.amnt2
            self.index=self.index+1
            tx= MyTransaction(self.index,self.address1,self.address2,self.amnt1,self.amnt2,10,self.address2)
            tx.sign(algod.signer,self.address2)
            return tx.serialize()
            


    def create_transaction(self,algod,address,value):
        
        if(algod.address==self.address1):
            if(self.amnt1>value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1-value,self.amnt2+value,10,self.address1)
                tx.sign(algod.signer,self.address1)
                return tx.serialize()
        else:
             if(self.amnt2>value):
                self.index=self.index+1
                tx = MyTransaction(self.index,self.address1,self.address2,self.amnt1+value,self.amnt2-value,10,self.address2)
                tx.sign(algod.signer,self.address2)
                return tx.serialize()


    def sign_transaction(self,algod,str):
        #Chek all the parameter
        tx = MyTransaction()
        tx.deserialize(str)
        if(algod.address==self.address1):
            tx.sign(algod.signer,self.address1)
        else:
            tx.sign(algod.signer,self.address2)
        return tx.serialize()
        

    def insert_transaction(self,str):
        #Insert the transaction in the list of transaction authenticated from both
        tx = MyTransaction()
        tx.deserialize(str)
        self.index = tx.get_index()
        self.amnt1=tx.get_amnt1()
        self.amnt2 = tx.get_amnt2()
        self.transactions.append(tx)


    def get_last_transaction(self):
        tx:MyTransaction = self.transactions.pop()
        return tx.contract_payload()


