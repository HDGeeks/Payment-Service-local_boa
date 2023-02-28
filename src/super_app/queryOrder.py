import requests
from . import applyFabricToken
import json
from . import tools
from . import tools


class QueryOrderService:
    req = None
    BASE_URL = None
    fabricAppId = None
    appSecret = None
    merchantAppId = None
    merchantCode = None

    def __init__(self, req, BASE_URL, fabricAppId, appSecret, merchantAppId, merchantCode):
        self.req = req
        self.BASE_URL = BASE_URL
        self.fabricAppId = fabricAppId
        self.appSecret = appSecret
        self.merchantAppId = merchantAppId
        self.merchantCode = merchantCode
        #self.notify_path = "https://superapp.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/subscription/super-app-notify-url"

        merch_order_id = self.req["merch_order_id"]
        applyFabricTokenResult = applyFabricToken.ApplyFabricTokenService(
            self.BASE_URL, self.fabricAppId, self.appSecret, self.merchantAppId)
        result = applyFabricTokenResult.applyFabricToken()
        fabricToken = result["token"]
        queryOrderResult = self.requestQueryOrder(fabricToken, merch_order_id)

        # rawRequest = self.createRawRequest(prepayId)
        # print(rawRequest)
        return queryOrderResult
    def requestQueryOrder(self, fabricToken, title):
        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": self.fabricAppId,
            "Authorization": fabricToken
        }

        payload = self.createRequestObject(title)
        server_output = requests.post(
            url=self.BASE_URL+"/payment/v1/merchant/queryOrder", headers=headers, data=payload, verify=False)
        return server_output.json()

    def createRequestObject(self, merch_order_id):
        req = {
            "nonce_str": tools.createNonceStr(),
            "method": "payment.queryorder",
            "timestamp": tools.createTimeStamp(),
            "version": "1.0",
            "biz_content": {},
        
        }
        biz = {

            "appid": self.merchantAppId,
            "merch_code": self.merchantCode,
            "merch_order_id": merch_order_id,


        }
        req["biz_content"] = biz
        sign = tools.sign(req)
        req["sign"] = sign
        req["sign_type"] = "SHA256withRSA"

        # print(json.dumps(req))
        return json.dumps(req)
    



    
