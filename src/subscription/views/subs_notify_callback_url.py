import json
import environ

from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import *
from django.core.exceptions import ObjectDoesNotExist


from django.views.decorators.csrf import csrf_exempt


from rest_framework.decorators import api_view
from rest_framework.response import Response


from utilities.telebirrApi import Telebirr


from subscription.models import Subscription_Payment_info


# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


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
            decrypted_data = Telebirr.decrypt(
                public_key=env("Public_Key"), payload=payload
            )

            outt = decrypted_data["outTradeNo"]

            fetch_data = Subscription_Payment_info.objects.filter(
                outTradeNo=outt
            ).values()

            if not fetch_data.exists():
                return Response("The outtrade number doesn't exist .")

            update_data = Subscription_Payment_info.objects.filter(
                outTradeNo=decrypted_data["outTradeNo"]
            ).update(
                msisdn=decrypted_data["msisdn"],
                tradeNo=decrypted_data["tradeNo"],
                transactionNo=decrypted_data["transactionNo"],
                payment_state="completed",
            )

            updated_data = Subscription_Payment_info.objects.filter(
                outTradeNo=outt
            ).values()

            # return Response({"decrypted_data": decrypted_data, "updated_data": updated_data})
            return Response({"code": 0, "msg": "success"})
    else:
        return Response(" only methods get and post allowed .")
