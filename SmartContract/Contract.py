from pyteal import *
import logging 



'''Ausiliarity function used for sending the ammount of money amm to the address addr
using the Inner Transaction'''
def sendMoney(addr,amm,b=False,addr2=None):
    if b:
        return Seq(
            InnerTxnBuilder().Begin(),
            InnerTxnBuilder.SetFields({
            TxnField.sender: Global.current_application_address(),
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: amm,
            TxnField.receiver: addr,
            TxnField.close_remainder_to: addr2
            }),
        InnerTxnBuilder.Submit())
    else:
        return Seq(
            InnerTxnBuilder().Begin(),
            InnerTxnBuilder.SetFields({
            TxnField.sender: Global.current_application_address(),
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: amm,
            TxnField.receiver: addr,
            }),
        InnerTxnBuilder.Submit())



noop = Approve()

handle_delete = Seq(
    Assert(App.globalGet(Bytes("deleting"))==Int(1)),
    Assert(Or(App.globalGet(Bytes("addA"))==Txn.sender(),App.globalGet(Bytes("addB"))==Txn.sender()) )

)


router = Router("Draft-Channell", BareCallActions(

    no_op=OnCompleteAction.always(Approve()),
    update_application=OnCompleteAction.never(),
    delete_application=OnCompleteAction.always(handle_delete)  
    ))




@router.method
def open_channel(pay:abi.PaymentTransaction):
    
    handle_creation= Seq(
        #Initialize all the variables

        Assert(App.globalGet(Bytes("open"))==Int(0)),
        App.globalPut(Bytes("addA"),Txn.accounts[1]),
        App.globalPut(Bytes("ammA"),Int(0)),
        App.globalPut(Bytes("addB"),Txn.accounts[2]),
        App.globalPut(Bytes("ammB"),Int(0)),
        App.globalPut(Bytes("flag"),Int(0)),
        App.globalPut(Bytes("deleting"),Int(0)),
    
        #Payment of 1 algo minimum balance
        Assert(pay.get().receiver()==Global.current_application_address()),
        App.globalPut(Bytes("open"),Int(1)),
        Approve(),
    )

    return handle_creation


#Deposit ammount of money inside the contract
@router.method
def deposit(pay:abi.PaymentTransaction):
    sender =pay.get().sender()
    addA = App.globalGet(Bytes("addA"))
    addB = App.globalGet(Bytes("addB"))

    return Seq( 
            Assert(pay.get().receiver()==Global.current_application_address())
               ,Assert(Or(sender==addA,sender==addB)),
               If(sender==addA,
                    Seq(App.globalPut(Bytes("ammA"),App.globalGet(Bytes("ammA"))+pay.get().amount())
                        ,Approve()),
                #Else
                    Seq(App.globalPut(Bytes("ammB"),App.globalGet(Bytes("ammB"))+pay.get().amount())
                        ,Approve())),
                )



@router.method
def presentation(msg:abi.DynamicBytes):
    
    app = ScratchVar(TealType.uint64)
    app2 = ScratchVar(TealType.uint64)
    #Parsing Payload and extract attributes
    enc = msg.get()
    index = Btoi(Extract(enc,Int(0),Int(8)))
    amnt1 = Btoi(Extract(enc,Int(8),Int(8)))
    amnt2 = Btoi(Extract(enc,Int(16),Int(8)))
    secret = Extract(enc,Int(24),Int(32))
    secret2 = Extract(enc,Int(56),Int(32))
    signature1 = Extract(enc,Int(88),Int(64))
    signature2 = Extract(enc,Int(152),Int(64))
    body = Extract(enc,Int(0),Len(enc)-Int(128))

    #Signature verify
    ver_signature1 = Ed25519Verify_Bare(body,signature1,App.globalGet(Bytes("addA")))
    ver_signature2 = Ed25519Verify_Bare(body,signature2,App.globalGet(Bytes("addB")))


    #Verification of amount, the balance proposed with the transaction must fit with the balance of the smart contract
    verification_amount = Seq(app.store(amnt1+amnt2),
                              app2.store(App.globalGet(Bytes("ammA"))+App.globalGet(Bytes("ammB"))),
                              Assert((app.load())==app2.load()),)
  

      
    #Update Secret Proposer and Revocation submitter
    handle_secret = Seq(App.globalPut(Bytes("secretProposer"),Txn.sender()),
                        
                        If(Txn.sender()==App.globalGet(Bytes("addA")),
                                Seq(
                                App.globalPut(Bytes("revocationSubmitter"),App.globalGet(Bytes("addB"))),
                                App.globalPut(Bytes("secret"),secret),
                                ),
                                
                        #Else
                                Seq(
                                App.globalPut(Bytes("revocationSubmitter"),App.globalGet(Bytes("addA"))),
                                App.globalPut(Bytes("secret"),secret2),
                                ),
                            )
                        )
    
     
    return Seq(
                #Verification on Signature (Verify that  Mytransaction was not tampered)
                Assert(And(ver_signature1,ver_signature2)==Int(1)),
                #Verification on amount (sum of proposed transfer must be equal to the sum of stored amount)
                verification_amount,
                #Update the global state
                App.globalPut(Bytes("ammA"),amnt1),
                App.globalPut(Bytes("ammB"),amnt2),
                App.globalPut(Bytes("index"),index),
                #Update secret mechanism
                handle_secret,
                #Set the lock on time accept (futureAccept) + delta
                App.globalPut(Bytes("futureAccept"),Global.round()+Int(2)),
                #Update the flag to 1
                App.globalPut(Bytes("flag"),Int(1)),
                Approve()
                )


@router.method
def close_channel(secret:abi.DynamicBytes):
  
    addA = App.globalGet(Bytes("addA"))
    addB = App.globalGet(Bytes("addB"))
    ammA = App.globalGet(Bytes("ammA"))
    ammB = App.globalGet(Bytes("ammB"))
    
    revocationsub= App.globalGet(Bytes("revocationSubmitter"))

    return Seq(
        #Check the flag status
        Assert(App.globalGet(Bytes("flag"))==Int(1)),
        App.globalPut(Bytes("deleting"),Int(1)),
        #Secret Proposer try to close the channel
        If(Txn.sender()==App.globalGet(Bytes("secretProposer")), Seq(
                Assert(Gt(Global.round(),App.globalGet(Bytes("futureAccept")))),
                sendMoney(addB,ammB),
                sendMoney(addA,ammA,True,addA),
                
                )),

        If(Txn.sender()==revocationsub, Seq(
                App.globalPut(Bytes("secret_proposed"),secret.get()),
                #Chek revocation secret if it is given
                If(secret.get()==App.globalGet(Bytes("secret")),
                        #Give all the money inside the contract + Balance_contract +1000 as there is only one transaction
                        sendMoney(revocationsub,ammA+ammB,True,revocationsub),
                   #Else
                    Seq(
                        sendMoney(addB,ammB),
                        sendMoney(addA,ammA,True,addA),
                         )))
        ),
       )
    
               


if __name__ == "__main__":
    import os
    import json


    #now we will Create and configure logger 
    logging.basicConfig( format='%(asctime)s %(message)s', filemode='w')
    logger=logging.getLogger() 
    #Now we are going to Set the threshold of logger to DEBUG 
    logger.setLevel(logging.DEBUG) 

    art_path=str(os.path.dirname(__file__))+"/artifacts"
    try:
        os.mkdir(art_path)
    except(FileExistsError):
        logger.info("artifacts directory already exist") 

 
    path = os.path.dirname(os.path.abspath(__file__))
    approval,clear, contract = router.compile_program(version=7)


    #Dump out the contract as json that can be read in by any SD K
    with open(os.path.join(path,"artifacts/contract.json"),"w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))
    #Write out the approval and clear programs
    with open(os.path.join(path,"artifacts/approval.teal"),"w") as f:
        f.write(approval)
    
    with open(os.path.join(path,"artifacts/clear.teal"), "w") as f:
        f.write(clear)
    
    logger.info("All file are compiled")
    


