from ast import Dict
from base64 import b64decode
import base64
import json
from typing import Any
from algosdk import account, transaction, abi
from algosdk.v2client import algod

#Deserialize the JSON string of the interface contract to produce an ogbject of type contract
def deserialize (js)->abi.Contract:
    contract_dict=json.loads(js)
    m:list = contract_dict['methods']
    methods = list()
    for el in m:
          name = el['name']
          args = list()
          for ele in el['args']:
               a = abi.Argument(ele['type'],ele['name'])
               args.append(a)
          p = el['returns']
          ret = abi.Returns(p['type'])

          m_el = abi.Method(name=name,args=args,returns=ret)
          methods.append(m_el)
               

    contract =abi.Contract(name=contract_dict['name'],methods=methods)
    return contract