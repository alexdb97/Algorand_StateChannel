
from base64 import b64decode
from algosdk import transaction, abi, logic, util
from MyTransaction import MyTransaction
import hashlib


from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,      
)


class ChainChannel() :

    """
    ChainChannel class is the interface with the algorand blockchain, therefore, through algorand transactions, it will

    provide the methods to create, interact and destroy the chain channel.

    """ 
    
    def __init__(self,algod,clear=None,app=None,contract=None,counterpart=None,app_id=None,app_address=None):
        
        self.algod=algod
        self.app_teal = app
        self.clear_teal = clear
        self.contract:abi.Contract = contract
        self.counterpart = counterpart
        self.app_id = app_id
        self.app_address = app_address
        

    """
    open_channel, the method that will create the chain channel, it will be formed of two address,

    the one that will create the transaction will provide also the minimum balance  of 1 algo required for the


    :param algod: an istance of the client is passed for validating the algo transactions
    return app_id,app_address: this are the endpoints of the contract, they are used for interacting and monitoring
                               inside the blockchain 
    """ 

    def open_channel(self):
        
        #Create the smart contract on the blockchain
        sp = self.algod.suggested_params()

        app_tx = transaction.ApplicationCreateTxn(
            self.algod.address,
            sp,
            on_complete=0,
            approval_program=self.app_teal,
            clear_program=self.clear_teal,
            global_schema=transaction.StateSchema(10,10),
            local_schema=transaction.StateSchema(0,0)
            )

        signed =app_tx.sign(self.algod.private)
        txid = self.algod.send_transaction(signed)
        result = transaction.wait_for_confirmation(self.algod, txid, 4)
        
        #Inizialization of application contest
        self.app_id = result['application-index']
        self.app_address =logic.get_application_address(self.app_id)

       
        #Strictly open the channel
        signer = AccountTransactionSigner(self.algod.private)
        atc = AtomicTransactionComposer()

        #Put inside  1 algo, it is required for the transactions executed by the smart contract itself
        tx = transaction.PaymentTxn(self.algod.address,sp=sp,receiver=self.app_address,amt=util.algos_to_microalgos(1))
        tws = TransactionWithSigner(tx,signer)

        
        atc.add_method_call(
            app_id=self.app_id,
            method = self.contract.get_method_by_name("open_channel"),
            sender=self.algod.address,
            sp=sp,
            signer=signer,
            accounts=[self.algod.address,self.counterpart],
            method_args=[tws],
        )

        result = atc.execute(self.algod, 10)  # Wait for 10 rounds

        return self.app_id, self.app_address

      

    """
    deposit, the method that will create the chain channel, it will be formed of two address,

    the one that will create the transaction will provide also the minimum balance  of 1 algo required for the


    :param algod: an istance of the client is passed for validating the algo transactions
    return app_id,app_address: this are the endpoints of the contract, they are used for interacting and monitoring
                               inside the blockchain 
    """
    def deposit_chain(self,amount):

        algo_to_micro =util.algos_to_microalgos(amount)

        sp:transaction.SuggestedParams = self.algod.suggested_params()

        signer = AccountTransactionSigner(self.algod.private)
        atc = AtomicTransactionComposer()
    
        tx = transaction.PaymentTxn(self.algod.address,sp=sp,receiver=self.app_address,amt=algo_to_micro)
        tws = TransactionWithSigner(tx,signer)
        
        atc.add_method_call(
            app_id=self.app_id,
            method = self.contract.get_method_by_name("deposit"),
            sender=self.algod.address,
            sp=sp,
            signer=signer,
            method_args=[tws]
        )
    
        group_result =atc.execute(self.algod,2)
        return group_result.abi_results[0]


    #Try Close
    def tryClose(self,my_tx):

        sp:transaction.SuggestedParams = self.algod.suggested_params()
        signer = AccountTransactionSigner(self.algod.private)

        

        atc = AtomicTransactionComposer()
        atc.add_method_call(
            app_id=self.app_id,
            method = self.contract.get_method_by_name("tryClose"),
            sender=self.algod.address,
            sp=sp,
            method_args=[my_tx],
            signer=signer,
        )

        #Reaching the budget of EdVerify using no-op transaction
        for x in range(0,5):
            txi = transaction.ApplicationNoOpTxn(self.algod.address,sp,self.app_id,note=str(x).encode('utf-8'))
            tws = TransactionWithSigner(txi,signer)
            atc.add_transaction(tws) 

        group_result = atc.execute(self.algod, 4)
        return group_result.abi_results[0]


        


    #Close channel
    def closeChannel(self,secret=None):
         sp:transaction.SuggestedParams = self.algod.suggested_params()
         
         if(secret==None):
            secret= bytes(32)
         h=hashlib.sha3_256()
         h.update(secret)
         digest=h.digest()
         signer = AccountTransactionSigner(self.algod.private)
         atc = AtomicTransactionComposer()
        
         atc.add_method_call(
             app_id=self.app_id,
             method = self.contract.get_method_by_name("closeChannel"),
             sender=self.algod.address,
             sp=sp,
             signer=signer,
             method_args=[digest],
             accounts=[self.algod.address,self.counterpart]

         )

         result = atc.execute(self.algod,4)

         #Delete Transaction
         """ deletetx = transaction.ApplicationDeleteTxn(self.algod.address,sp,self.app_id)
         signed =deletetx.sign(self.algod.private)
         txid = self.algod.send_transaction(signed)
         result = transaction.wait_for_confirmation(algod, txid, 4) """


         def get_info_contract():
             pass