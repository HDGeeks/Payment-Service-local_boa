from jinja2 import Environment, PackageLoader
import requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# url = "http://10.180.79.13:10001/payment/services/APIRequestMgrService"
url = "http://196.188.120.3:10001/payment/services/APIRequestMgrService"
# headers = {'content-type': 'application/soap+xml'}
# env = Environment(loader=PackageLoader('myapp', 'templates'))
# template = env.get_template('soaprequests/WeatherSericeRequest.xml')
# body = template.render()
headers = {"content-type": "text/xml"}
body = """<?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:api="http://cps.huawei.com/synccpsinterface/api_requestmgr" xmlns:req="http://cps.huawei.com/synccpsinterface/request" xmlns:com="http://cps.huawei.com/synccpsinterface/common">
   <soapenv:Header/>
   <soapenv:Body>

      <api:Request>
         <req:Header>
            <req:Version>1.0</req:Version>
            <req:CommandID>InitTrans_Business Deposit</req:CommandID>
            <req:OriginatorConversationID>
               49ea5e94e5fc40a7a652f8b97db931e6</req:OriginatorConversationID>
            <req:Caller>
               <req:CallerType>2</req:CallerType>
               <req:ThirdPartyID>Test
                  Acc</req:ThirdPartyID>
               <req:Password>Gi5mLfbLsCiw7NM6JdbEbxjs2ioV+YqE4ueO9D2D/qc=</req:Password>
            </req:Caller>
            <req:KeyOwner>
               1</req:KeyOwner>
            <req:Timestamp>20220103114748</req:Timestamp>
         </req:Header>
         <req:Body>
            <req:Identity>
               <req:Initiator>
                  <req:IdentifierType>12</req:IdentifierType>
                  <req:Identifier>
                     44444</req:Identifier>
                  <req:SecurityCredential>d9YEi1KxV7HcOkeM0zUUJahWm8u/VDzTLU+/9R5OliI=</req:SecurityCredential>
                  <req:ShortCode>
                     44444</req:ShortCode>
               </req:Initiator>
               <req:ReceiverParty>
                  <req:IdentifierType>4</req:IdentifierType>
                  <req:Identifier>04044</req:Identifier>
               </req:ReceiverParty>
            </req:Identity>
            <req:TransactionRequest>
               <req:Parameters>
                  <req:Amount>
                     12</req:Amount>
                  <req:Currency>ETB</req:Currency>
               </req:Parameters>
            </req:TransactionRequest>
         </req:Body>
      </api:Request>
   </soapenv:Body>
</soapenv:Envelope>
			"""

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)
try:
    session.post(url, data=body, headers=headers)
except requests.exceptions.ConnectionError as e:
    print(e)
else:
    print(session)
