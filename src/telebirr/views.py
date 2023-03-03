from unittest import result
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from rest_framework.decorators import api_view
import environ
from datetime import datetime
from django.db.models import Sum
from super_app.models import *

from .telebirrApi import Telebirr
from .serializers import (
    Payment_info_serializer,
    Purcahsed_album_serializer,
    Purcahsed_track_serializer,
    Track_revenue_rate_serializer,
)
from .models import (
    Payment_info,
    Purcahsed_album,
    Purcahsed_track,
    TrackRevenueRatePercentage,
)
from telebirr.decrypt import Decrypt
import logging
import random
import string
from .abyssinia import Abyssinia


logger = logging.getLogger(__name__)
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
    if request.method == "POST":
        # if not request.body:
        #     return Response("The request object (request.body) is empty .")
        # else:

        decrypted_data = Telebirr.decrypt(
            public_key=env("Public_Key"), payload=request.body
        )

        outt = decrypted_data["outTradeNo"]

        fetch_data = Payment_info.objects.filter(outTradeNo=outt).values()

        if not fetch_data.exists():
            return Response("The outtrade number doesn't exist .")

        update_data = Payment_info.objects.filter(
            outTradeNo=decrypted_data["outTradeNo"]
        ).update(
            msisdn=decrypted_data["msisdn"],
            tradeNo=decrypted_data["tradeNo"],
            transactionNo=decrypted_data["transactionNo"],
            payment_state="completed",
        )

        updated_data = Payment_info.objects.filter(outTradeNo=outt).values()

        # return Response({"decrypted_data": decrypted_data, "updated_data": updated_data})
        return Response({"code": 0, "msg": "success"})
    else:
        return Response(" only method post allowed .")


# cred = credentials.Certificate(
#     "/Users/hd/Desktop/kin-pay/pay-telebirr/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)


# @api_view(['GET', 'POST', ])
# def findUser(request):
#     if not request.body:
#         return Response("empty request body")

#     #uid = request.body
#     uid = "rZ44TdX7fBQ8hUZZDy2bRkTIcns1"
#     user = user_info(uid)
#     result = json.load(user)
#     user.ge

#     return Response(user)


class SavePurchasePaymentViewSet(ModelViewSet):
    """
    This view make and external api call,
    to telebirr platform ,
    save the result and return
    the data generated as json object
    """

    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] != "telebirr":
            return super().create(request, *args, **kwargs)
        return Response("telebirr payment is not saved using this api .")

    def list(self, request, *args, **kwargs):
        # this is haile code
        try:
            user = request.query_params["user"] or None
            user_obj = Payment_info.objects.filter(userId=user).values(
                "id", "userId", "amount"
            )
            return Response(user_obj)
        except BaseException as e:
            info = Payment_info.objects.all()
            serializer = Payment_info_serializer(info, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class PurchaseWithTelebirrViewSet(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            try:
                nonce = ""
                outtrade = ""
                outtrade = generate_nonce(16)
                print(outtrade)
                nonce = generate_nonce(16)

                amount = request.data["payment_amount"]
                pay = send_to_telebirr(amount, nonce, outtrade)
                if pay["message"] == "Operation successful":
                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": request.data["payment_amount"],
                        "payment_method": request.data["payment_method"],
                        "outTradeNo": outtrade,
                        "msisdn": "",
                        "tradeNo": "",
                        "transactionNo": "",
                        "payment_state": request.data["payment_state"],
                    }
                    serializer = Payment_info_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({"pay": pay, "data": serializer.data})

                return Response(
                    {
                        "message": pay["message"],
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )

            except BaseException as e:
                return Response({"error message": str(e)})

        else:
            return Response(
                {
                    "msg": " payment method is not telebirr",
                    "status": "status.HTTP_400_BAD_REQUEST",
                }
            )


class TrackRevenueViewset(ModelViewSet):
    serializer_class = Track_revenue_rate_serializer
    queryset = TrackRevenueRatePercentage.objects.all()


class PurchasedAlbumsViewset(ModelViewSet):
    """
    check the request data ,
    check the notify url and its results ,
    update the subscription model is subscribed field true

    """

    serializer_class = Purcahsed_album_serializer
    queryset = Purcahsed_album.objects.all()

    def create(self, request, *args, **kwargs):
        query_params = request.GET
        q = query_params.get("payment_method")

        if q == "superApp":
            verify_amount = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_amount")[0]["payment_amount"]
            verify_payment_state = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]
            verify_payment_title = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_title")[0]["payment_title"]
            verify_userId = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]
            if verify_amount < int(request.data["album_price_amount"]):
                return Response(
                    {
                        "message": "The price for this album cannot exceed the actual payment made ."
                    }
                )
            elif verify_userId != request.data["userId"]:
                return Response(
                    {"message": "This content is not purcahsed by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {"message": "The payment status is pending , cannot be assigned ."}
                )
            elif verify_payment_title.upper() != "PURCHASE_ALBUM":
                return Response(
                    {
                        "message": "The payment reason is not to purchase album , cannot be assigned ."
                    }
                )

            else:
                serializer = Purcahsed_album_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            verify_amount = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_amount")[0]["payment_amount"]
            verify_payment_state = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]
            verify_userId = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]
            if verify_amount < int(request.data["album_price_amount"]):
                return Response(
                    {
                        "message": "The price for this album cannot exceed the actual payment made ."
                    }
                )
            elif verify_userId != request.data["userId"]:
                return Response(
                    {"message": "This content is not purcahsed by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned ."
                    }
                )
            else:
                serializer = Purcahsed_album_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class PurchasedTracksViewset(ModelViewSet):
    """
    check the request data ,
    check the notify url and its results ,
    update the subscription model is subscribed field true

    """

    serializer_class = Purcahsed_track_serializer
    queryset = Purcahsed_track.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            if user_id == "all_users":
                return Response(
                    Purcahsed_track.objects.values("userId").annotate(
                        total_amount_per_user=Sum("track_price_amount")
                    )
                )
            elif user_id == "total":
                return Response(
                    Purcahsed_track.objects.aggregate(
                        total_money_from_purchased_tracks=Sum("track_price_amount")
                    )
                )
            else:
                per_user = Purcahsed_track.objects.filter(userId=user_id).values(
                    "userId", "trackId", "track_price_amount", "created_at"
                )
                # total_per_user = Purcahsed_track.objects.filter(
                #     userId=user_id).annotate(sum_per_user=Sum('track_price_amount'))
                total_per_user = per_user.aggregate(
                    total_per_user=Sum("track_price_amount")
                )
                return Response(
                    {"per_user": per_user, "total_per_this_user": total_per_user},
                    status=status.HTTP_200_OK,
                )

        else:
            return Response(Purcahsed_track.objects.all().values())

    def create(self, request, *args, **kwargs):
        query_params = request.GET
        q = query_params.get("payment_method")

        if q == "superApp":
            verify_amount = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_amount")[0]["payment_amount"]
            verify_userId = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]
            verify_payment_state = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]

            verify_payment_title = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_title")[0]["payment_title"]
            if verify_amount < int(request.data["track_price_amount"]):
                return Response(
                    {
                        "message": "The price for this track cannot exceed the actual payment made ."
                    }
                )
            elif verify_userId != request.data["userId"]:
                return Response(
                    {"message": "This content is not purcahsed by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned ."
                    }
                )
            elif verify_payment_title.upper() != "PURCHASE_TRACK":
                return Response(
                    {
                        "message": "The payment reason is not to purchase a track , cannot be assigned ."
                    }
                )

            else:
                serializer = Purcahsed_track_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            verify_amount = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_amount")[0]["payment_amount"]
            verify_userId = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]
            verify_payment_state = Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]

            if verify_amount < int(request.data["track_price_amount"]):
                return Response(
                    {
                        "message": "The price for this track cannot exceed the actual payment made ."
                    }
                )
            elif verify_userId != request.data["userId"]:
                return Response(
                    {"message": "This content is not purcahsed by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned ."
                    }
                )
            else:
                serializer = Purcahsed_track_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)


def send_to_telebirr(amount, nonce, outtrade):
    # Initialise environment variables
    env = environ.Env()
    environ.Env.read_env(DEBUG=(bool, False))

    telebirr = Telebirr(
        app_id=env("App_ID"),
        app_key=env("App_Key"),
        public_key=env("Public_Key"),
        notify_url="https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/payment/payment-notify-url",
        receive_name="Zema Multimedia PLC",
        return_url="https://zemamultimedia.com",
        short_code=env("Short_Code"),
        subject="Media content",
        timeout_express="30",
        total_amount=amount,
        nonce=nonce,
        out_trade_no=outtrade,
    )

    return telebirr.send_request()


def decrypt_response_from_telebirr(message):
    responded_data = Decrypt(message=message)
    return responded_data


def generate_nonce(length):
    result_str = "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length
        )
    )
    return result_str
