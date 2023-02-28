import json
import requests
from . import applyFabricToken, tools


class CreateOrderService:
    req = None
    BASE_URL = None
    fabricAppId = None
    appSecret = None
    merchantAppId = None
    merchantCode = None
    notify_path = None

    def __init__(self, req, BASE_URL, fabricAppId, appSecret, merchantAppId, merchantCode):
        self.req = req
        self.BASE_URL = BASE_URL
        self.fabricAppId = fabricAppId
        self.appSecret = appSecret
        self.merchantAppId = merchantAppId
        self.merchantCode = merchantCode
        self.notify_path = "https://superapp.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/subscription/super-app-notify-url"

   
    def createOrder(self):
        merch_order_id = self.req["merch_order_id"]
        title = self.req["title"]
        amount = self.req["amount"]
        currency = self.req["trans_currency"]


        # get token from telebirr super app server 
        applyFabricTokenResult = applyFabricToken.ApplyFabricTokenService(
            self.BASE_URL, self.fabricAppId, self.appSecret, self.merchantAppId)
        
        result = applyFabricTokenResult.applyFabricToken()
        fabricToken = result["token"]

        createOrderResult = self.requestCreateOrder(
            fabricToken, title, amount, currency, merch_order_id)
        
        prepayId = createOrderResult["biz_content"]["prepay_id"]
        rawRequest = self.createRawRequest(prepayId)

        return createOrderResult
       
  

    def requestCreateOrder(self, fabricToken, title, amount, currency, merch_order_id):
        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": self.fabricAppId,
            "Authorization": fabricToken
        }
        # Body parameters
        payload = self.createRequestObject(
            title, amount, currency, merch_order_id)
        server_output = requests.post(
            url=self.BASE_URL+"/payment/v1/merchant/preOrder", headers=headers, data=payload, verify=False)
        return server_output.json()
   

    def createRequestObject(self, title, amount, currency, merch_order_id):
        req = {
            "nonce_str": tools.createNonceStr(),
            "method": "payment.preorder",
            "timestamp": tools.createTimeStamp(),
            "version": "1.0",
            "biz_content": {},
        }

    
        biz = {
            "notify_url": self.notify_path,
            "business_type": "BuyGoods",
            "trade_type": "InApp",
            "appid": self.merchantAppId,
            "merch_code": self.merchantCode,
            "merch_order_id": merch_order_id,
            "title": title,
            "total_amount": amount,
            "trans_currency": currency,
            "timeout_express": "3m",

        }
        req["biz_content"] = biz
        sign = tools.sign(req)
        req["sign"] = sign
        req["sign_type"] = "SHA256withRSA"

      
        return json.dumps(req)
  

    def createRawRequest(self, prepayId):
        maps = {
            "appid": self.merchantAppId,
            "merch_code": self.merchantCode,
            "nonce_str": tools.createNonceStr(),
            "prepay_id": prepayId,
            "timestamp": tools.createTimeStamp(),
            "sign_type": "SHA256WithRSA"
        }
        rawRequest = ""
        for key in maps:
            value = maps[key]
            rawRequest = rawRequest + key + "=" + value + "&"
        sign = tools.sign(maps)
        rawRequest = rawRequest+"sign="+sign
        return rawRequest
