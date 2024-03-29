import json
import environ

from dateutil.relativedelta import *

from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import tools
from .createOrder import CreateOrderService
from .models import Superapp_Payment_info
from .queryOrder import QueryOrderService
from .serializers import Superapp_payment_serializer
from .verifyResponse import VerifyResponseService


# CREAT-ORDER


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

    return fianl_result


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
                return Response({"error message": str(e)})

        else:
            return Response(
                {
                    "msg": " payment method is not telebirr super app",
                    "status": "status.HTTP_400_BAD_REQUEST",
                }
            )


def verify(req):
    module = VerifyResponseService(req)
    response = module.verifyResponse()

    return response


@api_view(
    [
        "GET",
        "POST",
    ]
)
@csrf_exempt
def notify(request):
    if request.method == "POST" or request.method == "GET":
        if not request.data:
            return Response("The request object (request.body) is empty .")
        else:
            payload = request.data
            verified_data = verify(payload)
            verified_data = True
            if verified_data:
                merch_order_id = payload["merch_order_id"]

                order_status = payload["trade_status"]
                amount = payload["total_amount"]

                if order_status == "Completed":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    )

                    if not fetch_data.exists():
                        return Response(
                            f"The merch_order_id  {merch_order_id} does not exist!"
                        )

                    update_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    ).update(payment_state="completed")

                if order_status == "Paying":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    )

                    if not fetch_data.exists():
                        return Response(
                            f"The merch_order id {merch_order_id} does not exist!"
                        )

                    update_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    ).update(payment_state="Paying")

                if order_status == "Pending":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    )

                    if not fetch_data.exists():
                        return Response(
                            f"The merch_order_id {merch_order_id} does not exist!"
                        )

                    update_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    ).update(payment_state="Pending")

                if order_status == "PAY_FAILED":
                    fetch_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    )

                    if not fetch_data.exists():
                        return Response(
                            f"The merch_order_id  {merch_order_id} does not exist!"
                        )

                    update_data = Superapp_Payment_info.objects.filter(
                        merch_order_id=merch_order_id
                    ).update(payment_state="Failure")

                return Response({"code": 0, "msg": "success"})
            else:
                return Response("signature verification failed")

    else:
        return Response(" only methods get and post allowed .")


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

    return dict_result


class CheckPaymentViewSet(ModelViewSet):
    serializer_class = Superapp_payment_serializer
    queryset = Superapp_Payment_info.objects.all()

    def list(self, request, *args, **kwargs):
        merch_order_id = self.request.query_params.get("orderId")

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
                return Response({"payment_state": payment_status})

        else:
            return Response(
                {
                    "msg": " enter valid query parameter (orderId)",
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )
