from pyteal import *

noop = Approve()

handle_delete = Seq(
    Assert(App.globalGet(Bytes("deleting"))==Int(1)),
    Assert(Or(App.globalGet(Bytes("addA"))==Txn.sender(),App.globalGet(Bytes("addB"))==Txn.sender()) )

)

handle_creation= Seq(
    
    App.globalPut(Bytes("addA"),Txn.accounts[1]),
    App.globalPut(Bytes("ammA"),Int(0)),
    App.globalPut(Bytes("addB"),Txn.accounts[2]),
    App.globalPut(Bytes("ammB"),Int(0)),
    App.globalPut(Bytes("flag"),Int(0)),
    App.globalPut(Bytes("deleting"),Int(0)),
    Approve(),
)



router = Router("Draft-Channel", BareCallActions(

    no_op=OnCompleteAction.always(Approve()),
    update_application=OnCompleteAction.never(),
    delete_application=OnCompleteAction.always(handle_delete)

    ))


@router.method
def open_channel():
    return handle_creation


 #Deposit on the application
@router.method
def deposit(pay:abi.PaymentTransaction):
    sender =pay.get().sender()
    addA = App.globalGet(Bytes("addA"))
    addB = App.globalGet(Bytes("addB"))

    return Seq( 
            Assert(pay.get().receiver()==Global.current_application_address())
               ,Assert(Or(sender==addA,sender==addB)),
               If(sender==addA,
                    Seq(App.globalPut(Bytes("ammA"),App.globalGet(Bytes("ammA"))+pay.get().amount()-Int(1000000))
                        ,Approve()),
                #Else
                    Seq(App.globalPut(Bytes("ammB"),App.globalGet(Bytes("ammB"))+pay.get().amount()-Int(1000000))
                        ,Approve())),
                )



@router.method
def tryClose(msg:abi.DynamicBytes):
    
    app1 = ScratchVar(TealType.uint64)

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

    #Verification of amount
    verification_amount = Seq(App.globalPut(Bytes("tmp"),amnt1+amnt2),
                              app1.store(App.globalGet(Bytes("tmp"))),
                              Assert((app1.load())==App.globalGet(Bytes("ammA"))+App.globalGet(Bytes("AmmB"))),
                              App.globalPut(Bytes("Extern"),app1.load()),
                              App.globalPut(Bytes("Intern"),App.globalGet(Bytes("ammA"))+App.globalGet(Bytes("AmmB"))),
                              App.globalDel(Bytes("tmp")))
  
    scr = ScratchVar(TealType.bytes)
      
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
                App.globalPut(Bytes("futureAccept"),Global.round()+Int(1000)),
                #Update the flag to 1
                App.globalPut(Bytes("flag"),Int(1)),
                Approve()
                )


#Private Function send Money through
def sendMoney(addr,amm):
    return Seq(
        InnerTxnBuilder().Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.sender: Global.current_application_address(),
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: amm,
            TxnField.receiver: addr}),
        InnerTxnBuilder.Submit())

                

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
                sendMoney(addA,ammA),
                sendMoney(addB,ammB)
                )),

        If(Txn.sender()==revocationsub, Seq(
                #Chek revocation secret if it is given
                If(secret.get()==App.globalGet(Bytes("secret")),
                        sendMoney(revocationsub,ammA+ammB),
                   #Else
                    Seq(
                        sendMoney(addA,ammA),
                        sendMoney(addB,ammB),
                         )))
        ),)
    
               


if __name__ == "__main__":
    import os
    import json

    art_path=str(os.path.dirname(__file__))+"/artifacts"
    try:
        os.mkdir(art_path)
    except(FileExistsError):
        print("File Exists")

 
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
    
 
    
