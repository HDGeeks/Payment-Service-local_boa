import requests
from . import applyFabricToken
import json
from . import tools
from . import tools


class VerifyResponseService:
    req = None

    def __init__(self, req):
        self.req = req

    def verifyResponse(self):
        data = self.req
        payload = self.createRequestObject(data)
        # print(rawRequest)
        return payload

    def createRequestObject(self, data):
        sign = data.pop([sign])
        result = tools.verify(data)

        # print(json.dumps(req))
        return (result)
