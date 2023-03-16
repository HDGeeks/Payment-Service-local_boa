from . import tools


class VerifyResponseService:
    req = None

    def __init__(self, req):
        self.req = req

    def verifyResponse(self):
        payload = self.createRequestObject()

        return payload

    def createRequestObject(self):
        data = self.req
        clean_data = {
            "appid": data["appid"],
            "merchCode": data["merch_code"],
            "merchOrderId": data["merch_order_id"],
            "notifyTime": data["notify_time"],
            "notifyUrl": data["notify_url"],
            "paymentOrderId": data["payment_order_id"],
            "totalAmount": data["total_amount"],
            "tradeStatus": data["trade_status"],
            "transCurrency": data["trans_currency"],
            "transEndTime": data["trans_end_time"],
        }
        sign = data.pop("sign")
        result = tools.verify(clean_data, sign)

        return result
