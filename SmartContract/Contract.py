from pyteal import *
import logging 

BALANCE_CONTRACT = Int(998000)


'''Ausiliarity function used for sending the ammount of money amm to the address addr
using the Inner Transaction'''
def sendMoney(addr,amm):
    return Seq(
        InnerTxnBuilder().Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.sender: Global.current_application_address(),
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: amm,
            TxnField.receiver: addr}),
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
        App.globalPut(Bytes("addA"),Txn.accounts[1]),
        App.globalPut(Bytes("ammA"),Int(0)),
        App.globalPut(Bytes("addB"),Txn.accounts[2]),
        App.globalPut(Bytes("ammB"),Int(0)),
        App.globalPut(Bytes("flag"),Int(0)),
        App.globalPut(Bytes("deleting"),Int(0)),
    
        #Payment of 1 algo minimum balance
        Assert(pay.get().receiver()==Global.current_application_address()),
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
def tryClose(msg:abi.DynamicBytes):
    
    app = ScratchVar(TealType.uint64)

    #Parsing Payload and extract attributes
    enc = msg.get()
    index = Btoi(Extract(enc,Int(0),Int(8)))
    amnt1 = Btoi(Extract(enc,Int(8),Int(8)))
    amnt2 = Btoi(Extract(enc,Int(16),Int(8)))
    secret = Btoi(Extract(enc,Int(24),Int(8)))
    secret_proposer = Extract(enc,Int(32),Int(32))
    signature1 = Extract(enc,Int(64),Int(64))
    signature2 = Extract(enc,Int(128),Int(64))
    body = Extract(enc,Int(0),Len(enc)-Int(128))

    #Signature verify
    ver_signature1 = Ed25519Verify_Bare(body,signature1,App.globalGet(Bytes("addA")))
    ver_signature2 = Ed25519Verify_Bare(body,signature2,App.globalGet(Bytes("addB")))


    #Verification of amount, the balance proposed with the transaction must fit with the balance of the smart contract
    verification_amount = Seq(app.store(amnt1+amnt2),
                              Assert((app.load())==App.globalGet(Bytes("ammA"))+App.globalGet(Bytes("AmmB"))),)
  

      
    #Update Secret Proposer and Revocation submitter
    handle_secret = Seq(App.globalPut(Bytes("secretProposer"),secret_proposer),
                        App.globalPut(Bytes("secret"),secret),
                        If(App.globalGet(Bytes("secretProposer"))==App.globalGet(Bytes("addA")),
                                App.globalPut(Bytes("revocationSubmitter"),App.globalGet(Bytes("addB"))),
                        #Else
                                App.globalPut(Bytes("revocationSubmitter"),App.globalGet(Bytes("addA"))),
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
                App.globalPut(Bytes("futureAccept"),Global.round()+Int(1)),
                #Update the flag to 1
                App.globalPut(Bytes("flag"),Int(1)),
                Approve()
                )


@router.method
def closeChannel(secret:abi.Uint64):
  
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
                #Assert(Gt(Global.round(),App.globalGet(Bytes("futureAccept")))),
                sendMoney(addA,ammA+BALANCE_CONTRACT),
                sendMoney(addB,ammB)
                )),

        If(Txn.sender()==revocationsub, Seq(
                #Chek revocation secret if it is given
                If(secret.get()==App.globalGet(Bytes("secret")),
                        sendMoney(revocationsub,ammA+ammB+BALANCE_CONTRACT),
                   #Else
                    Seq(
                        sendMoney(addA,ammA+BALANCE_CONTRACT),
                        sendMoney(addB,ammB),
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
    
    
 
   
#This is a comment


