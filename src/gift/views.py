import json

import environ
from django.db.models import Sum,Count
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from gift.pagination import MyPagination

from utilities.generate_nonce import generate_nonce
from utilities.identity import get_identity
from utilities.send_to_telebirr import send_to_telebirr

from utilities.telebirrApi import Telebirr

from .models import Coin, Gift_Info, Gift_Payment_info, Gift_Revenue_Rate
from .serializers import (
    Coin_info_serializer,
    Gift_info_serializer,
    Gift_payment_serializer,
    Gift_revenue_rate_serializer,
)

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


@api_view(["GET", "POST"])
@csrf_exempt
def notify(request):
    if request.method == "POST":
        payload = request.body
        try:
            decrypted_data = Telebirr.decrypt(
                public_key=env("Public_Key"), payload=payload
            )
        except Exception as e:
            return Response(str(e))
        else:
            # get current amount using outtade
            current = Gift_Payment_info.objects.filter(
                outTradeNo=decrypted_data["outTradeNo"]
            )
            # capture the existing amount
            if current.exists():
                # existing amount
                current_amount = current.values("payment_amount")[0]["payment_amount"]

                # user of the outtrade number
                current_user = current.values("userId")[0]["userId"]

                # perform addition of the current amount with total amount
                new_amount = current_amount + int(decrypted_data["totalAmount"])

                # update the row with new info in gift payment table
                update_data = Gift_Payment_info.objects.filter(
                    outTradeNo=decrypted_data["outTradeNo"]
                ).update(
                    msisdn=decrypted_data["msisdn"],
                    tradeNo=decrypted_data["tradeNo"],
                    transactionNo=decrypted_data["transactionNo"],
                    payment_amount=new_amount,
                    payment_state="completed",
                )

                # update the coin table

                # find the  existing coin per user
                current_coin = Coin.objects.filter(userId=current_user).values(
                    "total_coin"
                )[0]["total_coin"]
                # calculate the new coin
                new_coin = current_coin + int(decrypted_data["totalAmount"])
                # update the new amount
                Coin.objects.filter(userId=current_user).update(total_coin=new_coin)

                # return Response({"Decrypted_Data": decrypted_data, "Updated_Data": updated_data})
                return Response({"code": 0, "msg": "success"})
            else:
                return Response("The outtrade number doesn't exist .")
    else:
        return Response(" only methods get and post allowed .")


@api_view(["GET", "POST"])
@csrf_exempt
def dummy_dec(request):
    if request.method == "POST" or request.method == "GET":
        payload = request.body

        if payload != "":
            try:
                decrypted_data = Telebirr.decrypt(
                    public_key=env("Public_Key"), payload=payload
                )
            except Exception as e:
                return Response(str(e))
            else:
                return Response(
                    {
                        "Decrypted_Data": decrypted_data,
                    }
                )

    return Response("post method only")


class GiftRevenuViewset(ModelViewSet):
    serializer_class = Gift_revenue_rate_serializer
    queryset = Gift_Revenue_Rate.objects.all()


class BuyGiftViewSet(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            count = Gift_Payment_info.objects.all().count()
            if user_id == "all":
                return Response(
                    Gift_Payment_info.objects.aggregate(
                        total_gift_payment_all_users=Sum("payment_amount")
                    )
                )
            elif user_id == "all_users":
                return Response(
                    Gift_Payment_info.objects.values("userId").annotate(
                        total_amount_per_user=Sum("payment_amount")
                    )
                )
            else:
                per_user = Gift_Payment_info.objects.filter(userId=user_id).values(
                    "userId", "payment_amount"
                )

                total_per_user = per_user.aggregate(
                    total_per_user=Sum("payment_amount")
                )
                identity = get_identity(user=user_id)
                if not identity:
                    identity = " No info on this user ."

            return Response(
                {
                    "count": "count",
                    "result": {
                        "per_user": per_user,
                        "total_per_user": total_per_user,
                        "identity": identity,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(Gift_Payment_info.objects.all().order_by("userId").values())


class GiftAnalyticViewset(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer
    http_method_names = ["get", "head"]
    pagination_class = MyPagination
    

    def list(self, request, *args, **kwargs):
        response = {}
        data = json.loads(
            json.dumps(super().list(request, *args, **kwargs).data["results"])
        )
        # list of user_ids
        list_of_users = []
        for item in data:
            list_of_users.append(item["userId"])

        unique_user_ids = list(set(list_of_users))

        #response["count"] = unique_user_ids.__len__()
        response["count"] = Gift_Payment_info.objects.values('userId').distinct().count()
        print(response["count"])
        
        response["result"] = []
        for user in unique_user_ids:
            # get data from haile
            user_identity = get_identity(user)
            
            # Per user
            per_user = (
                Gift_Payment_info.objects.filter(userId=user)
                .order_by("created_at")
                .values("userId", "payment_amount", "payment_method", "created_at")
            )
            # total per user
            total_per_user = per_user.aggregate(total_per_user=Sum("payment_amount"))
           
            # final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key]=value

            #final_result_dictionary["user_identity"] = user_identity
            final_result_dictionary["per_user"] = per_user
            # new change
            for key,value in total_per_user.items():
                final_result_dictionary[key]= value
            # append results to result
            response["result"].append(final_result_dictionary)
           
           
            
        return Response(response)


class CoinViewset(ModelViewSet):
    queryset = Coin.objects.all()
    serializer_class = Coin_info_serializer
    http_method_names = ["get", "head"]

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            return Response(Coin.objects.filter(userId=user_id).values())
        return Response(Coin.objects.all().values(), status=status.HTTP_200_OK)


class TelebirrGiftPaymentViewset(ModelViewSet):

    """
    This view make and external api call,
    to telebirr platform ,
    save the result and return
    the data generated as json object
    """

    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            try:
                # if self.queryset.filter(userId=request.data['userId']).exists():
                #     return self.update(request)

                nonce = ""
                outtrade = ""
                outtrade = generate_nonce(16)
                nonce = generate_nonce(16)
                notify_type = "gift"

                amount = request.data["payment_amount"]
                pay = send_to_telebirr(amount, nonce, outtrade, notify_type)

                if pay["message"] == "Operation successful":
                    current_amount = 0

                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": current_amount,
                        "payment_method": request.data["payment_method"],
                        "outTradeNo": outtrade,  # "PZzTaKf4IW",
                        "msisdn": "",
                        "tradeNo": "",
                        "transactionNo": "",
                        "payment_state": request.data["payment_state"],
                    }

                    serializer = Gift_payment_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(
                            {"Telebirr_Response": pay, "Data": serializer.data}
                        )

                return Response(
                    {
                        "message": pay["message"],
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )

            except BaseException as e:
                return Response({"error message": str(e)})

        return Response({"msg": " payment method is not telebirr"})


class GiveGiftArtistViewset(ModelViewSet):
    serializer_class = Gift_info_serializer
    queryset = Gift_Info.objects.all()

    def list(self, request, *args, **kwargs):
        artist = self.request.query_params.get("artist")
        if artist:
            if artist == "all":
                return Response(
                    Gift_Info.objects.values("ArtistId")
                    .annotate(total_gift_collected=Sum("gift_amount"))
                    .order_by("-total_gift_collected")[:10]
                )
            queryset = Gift_Info.objects.filter(ArtistId=artist)
            queryset = queryset.values("ArtistId", "gift_amount")
            total_gift = sum(queryset.values_list("gift_amount", flat=True))
            result = {"ArtistId": artist, "total": total_gift}
            return Response(result)
        else:
            return Response(
                Gift_Info.objects.all().values("id", "ArtistId", "gift_amount")
            )

    def create(self, request, *args, **kwargs):
        # find the coin available per user
        current_coin_amount = Coin.objects.filter(userId=request.data["userId"]).values(
            "total_coin"
        )[0]["total_coin"]

        # validate if the user have enough balance
        if int(request.data["gift_amount"]) > current_coin_amount:
            return Response({"message": " You dont have enough gift coin balance ."})

        # subtract the amount to gift from the existing coin amount
        new_deducted_coin_amount = current_coin_amount - int(
            request.data["gift_amount"]
        )

        # update the coin model with new deducted amount
        Coin.objects.filter(userId=request.data["userId"]).update(
            total_coin=new_deducted_coin_amount
        )
        # return response to front end
        serializer = Gift_info_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def send_to_telebirr(amount, nonce, outtrade):
#     # Initialise environment variables
#     env = environ.Env()
#     environ.Env.read_env()

#     telebirr = Telebirr(
#         app_id=env("App_ID"),
#         app_key=env("App_Key"),
#         public_key=env("Public_Key"),
#         notify_url="https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/gift/notify-url",
#         receive_name="Zema Multimedia PLC ",
#         return_url="https://zemamultimedia.com",
#         short_code=env("Short_Code"),
#         subject="Media content",
#         timeout_express="30",
#         total_amount=amount,
#         nonce=nonce,
#         out_trade_no=outtrade,
#     )

#     return telebirr.send_request()

