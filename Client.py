
from base64 import b64decode
from algosdk import transaction, abi, logic, util
from MyTransaction import MyTransaction



from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,      
)


class Client() :
    
    def __init__(self,address,private,algod_client):
        self.address=address
        self.__private=private
        self.algod_client = algod_client

        # TODO Decouple this in a ChainChannell entity
        self.channel = None
        self.contract:abi.Contract = None
        self.channel_address = None
        self.counterpart = None


    #TODO remove and inject in another way
    def set_contract(self,channel,address,contract,address2):
        self.channel=channel
        self.channel_address=address
        self.contract=contract
        self.counterpart=address2
        

    #Open the Bidirectional Channel deploying the smart contract
    def open_channel(self,addr_counterpart,app,clear,contract):
        
        #Create the smart contract on the blockchain
        sp = self.algod_client.suggested_params()

        app_tx = transaction.ApplicationCreateTxn(
            self.address,
            sp,
            on_complete=0,
            approval_program=app,
            clear_program=clear,
            global_schema=transaction.StateSchema(10,10),
            local_schema=transaction.StateSchema(0,0)
            )

        signed =app_tx.sign(self.__private)
        txid = self.algod_client.send_transaction(signed)
        result = transaction.wait_for_confirmation(self.algod_client, txid, 4)
        
        #Inizialization of application contest
        self.channel = result['application-index']
        self.channel_address =logic.get_application_address(self.channel)
        self.counterpart = addr_counterpart
        self.contract=contract

       
        #Strictly open the channel
        signer = AccountTransactionSigner(self.__private)
        atc = AtomicTransactionComposer()
        
        atc.add_method_call(
            app_id=self.channel,
            method = self.contract.get_method_by_name("open_channel"),
            sender=self.address,
            sp=sp,
            signer=signer,
            accounts=[self.address,addr_counterpart],
        )

        result = atc.execute(self.algod_client,2)

        return self.channel, self.channel_address

      

    #Deposit an amount of money inside the application
    def deposit(self,amount):

        algo_to_micro =util.algos_to_microalgos(amount)

        sp:transaction.SuggestedParams = self.algod_client.suggested_params()

        signer = AccountTransactionSigner(self.__private)
        atc = AtomicTransactionComposer()
    
        tx = transaction.PaymentTxn(self.address,sp=sp,receiver=self.channel_address,amt=algo_to_micro)
        tws = TransactionWithSigner(tx,signer)
        
        atc.add_method_call(
            app_id=self.channel,
            method = self.contract.get_method_by_name("deposit"),
            sender=self.address,
            sp=sp,
            signer=signer,
            method_args=[tws]
        )
    
        group_result =atc.execute(self.algod_client,2)
        return group_result.abi_results[0]


    #Try Close
    def tryClose(self,my_tx:MyTransaction):

        sp:transaction.SuggestedParams = self.algod_client.suggested_params()
        signer = AccountTransactionSigner(self.__private)

        my_tx_signed = my_tx.contract_payload()

        atc = AtomicTransactionComposer()
        atc.add_method_call(
            app_id=self.channel,
            method = self.contract.get_method_by_name("tryClose"),
            sender=self.address,
            sp=sp,
            method_args=[my_tx_signed],
            signer=signer,
        )

        #Reaching the budget of EdVerify using no-op transaction
        for x in range(0,6):
            txi = transaction.ApplicationNoOpTxn(self.address,sp,self.channel,note=str(x).encode('utf-8'))
            tws = TransactionWithSigner(txi,signer)
            atc.add_transaction(tws) 

        group_result = atc.execute(self.algod_client, 4)
        return group_result.abi_results[0]


        


    #Close channel
    def closeChannel(self,secret=0):
         sp:transaction.SuggestedParams = self.algod_client.suggested_params()
         
      
         signer = AccountTransactionSigner(self.__private)
         atc = AtomicTransactionComposer()
        
         atc.add_method_call(
             app_id=self.channel,
             method = self.contract.get_method_by_name("closeChannel"),
             sender=self.address,
             sp=sp,
             signer=signer,
             method_args=[secret],
             accounts=[self.address,self.counterpart]

         )

         result = atc.execute(self.algod_client,4)

         #Delete Transaction
         """ deletetx = transaction.ApplicationDeleteTxn(self.address,sp,self.channel)
         signed =deletetx.sign(self.__private)
         txid = self.algod_client.send_transaction(signed)
         result = transaction.wait_for_confirmation(self.algod_client, txid, 4) """