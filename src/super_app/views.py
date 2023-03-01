from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import base64
import hashlib
import sys
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import json
from django.http import JsonResponse
import requests
from django.shortcuts import render
from rest_framework.decorators import api_view
from urllib3.exceptions import InsecureRequestWarning
from .createOrder import CreateOrderService
from .queryOrder import QueryOrderService
from .verifyResponse import VerifyResponseService
from . import tools

####################################################################
import dataclasses
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from rest_framework.viewsets import ModelViewSet
from .serializers import Superapp_payment_serializer
from .models import Superapp_Payment_info
from rest_framework.response import Response
import string
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import environ


###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

# CREAT-ORDER#

###################################################################################################################################
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


def creatOrder(amount, title, currency, merch_order_id):
    req = {
        "timestamp": "",
        "method": "",
        "nonce_str": "",
        "sign_type": "",
        "sign": "",
        "version": "",
        "notify_url": "",
        "business_type": "",
        "trade_type": "",
        "appid": "",
        "merch_code": "",
        "merch_order_id": merch_order_id,
        "title": title,
        "amount": amount,
        "trans_currency": currency,
        "timeout_express": "",
        "payee_identifier": "",
        "payee_identifier_type": "",
        "payee_type": "",
    }

    module = CreateOrderService(
        req,
        env("baseUrl"),
        env("fabricAppId"),
        env("appSecret"),
        env("merchantAppId"),
        env("merchantCode"),
    )
    response = module.createOrder()

    result = json.dumps(response)
    dict_result = json.loads(result)
    prepayId = dict_result["biz_content"]["prepay_id"]
    rawRequest = module.createRawRequest(prepayId)
    fianl_result = {}
    fianl_result["result"] = dict_result
    fianl_result["raw_result"] = rawRequest
    # return JsonResponse(dict_result)
    # return dict_result
    return fianl_result


###################################################################################################################################


class SuperappPayViewSet(ModelViewSet):
    serializer_class = Superapp_payment_serializer
    queryset = Superapp_Payment_info.objects.all()

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr_superApp":
            try:
                amount = request.data["payment_amount"]
                title = request.data["payment_title"]
                currency = request.data["payment_currency"]
                merch_order_id = tools.createMerchantOrderId()

                order = creatOrder(amount, title, currency, merch_order_id)
                print(order)
                if order["result"]["result"] == "SUCCESS":
                    rawRequest = order["raw_result"]

                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": request.data["payment_amount"],
                        "payment_method": request.data["payment_method"],
                        "payment_title": request.data["payment_title"],
                        "payment_currency": request.data["payment_currency"],
                        "payment_state": request.data["payment_state"],
                        "merch_order_id": merch_order_id,
                        "prepay_id": order["result"]["biz_content"]["prepay_id"],
                    }

                    serializer = Superapp_payment_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(
                            {"rawRequest": rawRequest, "data": serializer.data}
                        )

                return Response(
                    {
                        "message": order["result"],
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )

            except BaseException as e:
                print(e)

                return Response({"error message": str(e)})

        else:
            print(request.data["payment_method"])
            return Response(
                {
                    "msg": " payment method is not telebirr super app",
                    "status": "status.HTTP_400_BAD_REQUEST",
                }
            )


###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

# NOTIFY#
###################################################################################################################################


def verify(req):
    module = VerifyResponseService(req)
    response = module.verifyResponse()
    # result = json.dumps(response)
    # dict_result = json.loads(result)
    # # return JsonResponse(dict_result)
    return response


###################################################################################################################################


@api_view(
    [
        "GET",
        "POST",
    ]
)
@csrf_exempt
def notify(request):
    if request.method == "POST" or request.method == "GET":
        if not request.body:
            return Response("The request object (request.body) is empty .")
        else:
            payload = request.body
            verified_data = verify(payload)
            if verified_data:
                prepay_id = payload["payment_order_id"]
                order_status = payload["trade_status"]
                amount = payload["total_amount"]

                if order_status == "Completed":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                    if not fetch_data.exists():
                        return Response(f"The Prepay id {prepay_id} does not exist!")

                    update_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).update(payment_state="completed")

                    updated_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()
                if order_status == "Paying":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                    if not fetch_data.exists():
                        return Response(f"The Prepay id {prepay_id} does not exist!")

                    update_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).update(payment_state="Paying")

                    updated_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                if order_status == "Pending":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                    if not fetch_data.exists():
                        return Response(f"The Prepay id {prepay_id} does not exist!")

                    update_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).update(payment_state="Pending")

                    updated_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                if order_status == "Failure":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                    if not fetch_data.exists():
                        return Response(f"The Prepay id {prepay_id} does not exist!")

                    update_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).update(payment_state="Failure")

                    updated_data = Superapp_Payment_info.objects.filter(
                        prepay_id=prepay_id
                    ).values()

                return Response({"code": 0, "msg": "success"})
            else:
                return Response("signature verification failed")

    else:
        return Response(" only methods get and post allowed .")


###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

# QUERY-ORDER#

###################################################################################################################################


def queryOrder(merch_order_id):
    req = {
        "timestamp": "",
        "method": "",
        "nonce_str": "",
        "sign_type": "",
        "sign": "",
        "version": "",
        "appid": "",
        "merch_code": "",
        "merch_order_id": merch_order_id,
    }

    module = QueryOrderService(
        req,
        env("baseUrl"),
        env("fabricAppId"),
        env("appSecret"),
        env("merchantAppId"),
        env("merchantCode"),
    )
    response = module.queryOrder()
    result = json.dumps(response)
    dict_result = json.loads(result)
    # return JsonResponse(dict_result)
    return dict_result


###################################################################################################################################


class CheckPaymentViewSet(ModelViewSet):
    serializer_class = Superapp_payment_serializer
    queryset = Superapp_Payment_info.objects.all()

    def list(self, request, *args, **kwargs):
        merch_order_id = self.request.query_params.get("orderId")
        print(merch_order_id)
        if merch_order_id:
            payment_obj = Superapp_Payment_info.objects.filter(
                merch_order_id=merch_order_id
            )
            # payment_obj = Subscription_Payment_info.objects.all()
            if not payment_obj:
                return Response({"message": "no payment order found"})
            merch_order_id = payment_obj.values("merch_order_id")[0]["merch_order_id"]
            payment_status = payment_obj.values("payment_state")[0]["payment_state"]
            # return Response(merch_order_id)
            if not payment_status == "completed":
                try:
                    merch_order_id = merch_order_id

                    query = queryOrder(merch_order_id)
                    if query["result"] == "SUCCESS":
                        if query["biz_content"]["order_status"] == "PAY_FAILED":
                            payment_obj.update(payment_state="FAILURE")
                        return Response(
                            {
                                "STATUS": query["biz_content"]["order_status"],
                                "response": query,
                            }
                        )

                    return Response(
                        {
                            "message": query["result"],
                            "status": status.HTTP_400_BAD_REQUEST,
                        }
                    )

                except BaseException as e:
                    return Response({"error message": str(e)})
            else:
                return Response({"payment_state": status})

        else:
            return Response(
                {
                    "msg": " enter valid query parameter (orderId)",
                    "status": "status.HTTP_400_BAD_REQUEST",
                }
            )
