# import json

# import environ
# from django.db.models import Sum
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.viewsets import ModelViewSet
# from gift.pagination import MyPagination
# from django.db.models import Q
# from utilities.identity import get_identity

# from utilities.generate_nonce import generate_nonce
# from utilities.identity import get_identity
# from utilities.send_to_telebirr import send_to_telebirr
# from utilities.telebirrApi import Telebirr

# from .models import Coin, Gift_Info, Gift_Payment_info, Gift_Revenue_Rate
# from .serializers import (
#     Coin_info_serializer,
#     Gift_info_serializer,
#     Gift_payment_serializer,
#     Gift_revenue_rate_serializer,
# )

# # Initialise environment variables
# env = environ.Env()
# environ.Env.read_env()


# class BuyGiftViewSet(ModelViewSet):
#     queryset = Gift_Payment_info.objects.all()
#     serializer_class = Gift_payment_serializer

#     def list(self, request, *args, **kwargs):
#         user_id = self.request.query_params.get("user")
#         if user_id:
#             if user_id == "all":
#                 return Response(
#                     Gift_Payment_info.objects.aggregate(
#                         total_gift_payment_all_users=Sum("payment_amount")
#                     )
#                 )

#             else:
#                 per_user = Gift_Payment_info.objects.filter(userId=user_id).values(
#                     "id", "userId", "payment_amount", "payment_method"
#                 )
#                 total_per_user = per_user.aggregate(
#                     total_per_user=Sum("payment_amount")
#                 )
#             return Response(
#                 {"per_user": per_user, "total_per_this_user": total_per_user},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(
#             Gift_Payment_info.objects.all().values(), status=status.HTTP_200_OK
#         )


# class TelebirrGiftPaymentViewset(ModelViewSet):

#     """
#     This view make and external api call,
#     to telebirr platform ,
#     save the result and return
#     the data generated as json object
#     """

#     queryset = Gift_Payment_info.objects.all()
#     serializer_class = Gift_payment_serializer

#     def create(self, request, *args, **kwargs):
#         if request.data["payment_method"] == "telebirr":
#             try:
#                 # if self.queryset.filter(userId=request.data['userId']).exists():
#                 #     return self.update(request)

#                 nonce = ""
#                 outtrade = ""
#                 outtrade = generate_nonce(16)
#                 nonce = generate_nonce(16)
#                 notify_type = "gift"

#                 amount = request.data["payment_amount"]
#                 pay = send_to_telebirr(amount, nonce, outtrade, notify_type)

#                 if pay["message"] == "Operation successful":
#                     current_amount = 0

#                     content = {
#                         "userId": request.data["userId"],
#                         "payment_amount": current_amount,
#                         "payment_method": request.data["payment_method"],
#                         "outTradeNo": outtrade,  # "PZzTaKf4IW",
#                         "msisdn": "",
#                         "tradeNo": "",
#                         "transactionNo": "",
#                         "payment_state": request.data["payment_state"],
#                     }

#                     serializer = Gift_payment_serializer(data=content)
#                     if serializer.is_valid(raise_exception=True):
#                         serializer.save()
#                         return Response(
#                             {"Telebirr_Response": pay, "Data": serializer.data}
#                         )

#                 return Response(
#                     {
#                         "message": pay["message"],
#                         "status": status.HTTP_400_BAD_REQUEST,
#                     }
#                 )

#             except BaseException as e:
#                 return Response({"error message": str(e)})

#         return Response({"msg": " payment method is not telebirr"})


# class CoinViewset(ModelViewSet):
#     queryset = Coin.objects.all()
#     serializer_class = Coin_info_serializer
#     http_method_names = ["get", "head"]

#     def list(self, request, *args, **kwargs):
#         user_id = self.request.query_params.get("user")
#         if user_id:
#             return Response(Coin.objects.filter(userId=user_id).values())
#         return Response(Coin.objects.all().values(), status=status.HTTP_200_OK)


# class GiveGiftArtistViewset(ModelViewSet):
#     serializer_class = Gift_info_serializer
#     queryset = Gift_Info.objects.all()

#     def list(self, request, *args, **kwargs):
#         artist = self.request.query_params.get("artist")
#         if artist:
#             if artist == "all":
#                 return Response(
#                     Gift_Info.objects.values("ArtistId")
#                     .annotate(total_gift_collected=Sum("gift_amount"))
#                     .order_by("-total_gift_collected")[:10]
#                 )
#             queryset = Gift_Info.objects.filter(ArtistId=artist)
#             queryset = queryset.values("userId", "gift_amount")
#             res = []
#             for gift in queryset:
#                 temp = {}
#                 temp["userId"] = get_identity(gift["userId"])
#                 temp["amount"] = gift["gift_amount"]
#                 res.append(temp)

#             total_gift = sum(queryset.values_list("gift_amount", flat=True))
#             result = {"ArtistId": artist, "total": total_gift, "tippers": res}
#             return Response(result)
#         else:
#             return Response(
#                 Gift_Info.objects.all().values(
#                     "id", "userId", "ArtistId", "gift_amount"
#                 )
#             )

#     def create(self, request, *args, **kwargs):
#         # find the coin available per user
#         current_coin_amount = Coin.objects.filter(userId=request.data["userId"]).values(
#             "total_coin"
#         )[0]["total_coin"]

#         # validate if the user have enough balance
#         if int(request.data["gift_amount"]) > current_coin_amount:
#             return Response({"message": " You dont have enough gift coin balance ."})

#         # subtract the amount to gift from the existing coin amount
#         new_deducted_coin_amount = current_coin_amount - int(
#             request.data["gift_amount"]
#         )

#         # update the coin model with new deducted amount
#         Coin.objects.filter(userId=request.data["userId"]).update(
#             total_coin=new_deducted_coin_amount
#         )
#         # return response to front end
#         serializer = Gift_info_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GiftRevenuViewset(ModelViewSet):
#     queryset = Gift_Revenue_Rate.objects.all()
#     serializer_class = Gift_revenue_rate_serializer


# @api_view(["GET", "POST"])
# @csrf_exempt
# def notify(request):
#     if request.method == "POST" or request.method == "GET":
#         if not request.body:
#             return Response("The request object (request.body) is empty .")
#         else:
#             payload = request.body
#             # decrypt data
#             decrypted_data = Telebirr.decrypt(
#                 public_key=env("Public_Key"), payload=payload
#             )

#             # get current amount using outtade
#             current = Gift_Payment_info.objects.filter(
#                 outTradeNo=decrypted_data["outTradeNo"]
#             )
#             current_user = current.values("userId")[0]["userId"]
#             # capture the existing amount
#             if current.exists():
#                 current_amount = current.values("payment_amount")[0]["payment_amount"]

#                 # perform addition of the current amount with total amount
#                 new_amount = current_amount + int(decrypted_data["totalAmount"])

#                 # update the row with new info
#                 update_data = Gift_Payment_info.objects.filter(
#                     outTradeNo=decrypted_data["outTradeNo"]
#                 ).update(
#                     msisdn=decrypted_data["msisdn"],
#                     tradeNo=decrypted_data["tradeNo"],
#                     transactionNo=decrypted_data["transactionNo"],
#                     payment_amount=new_amount,
#                     payment_state="completed",
#                 )

#                 # fetch the row for display
#                 updated_data = Gift_Payment_info.objects.filter(
#                     outTradeNo=decrypted_data["outTradeNo"]
#                 ).values()

#                 # find the  existing coin per user
#                 current_coin = Coin.objects.filter(userId=current_user).values(
#                     "total_coin"
#                 )[0]["total_coin"]
#                 # calculate the new coin
#                 new_coin = current_coin + int(decrypted_data["totalAmount"])
#                 # update the new amount
#                 Coin.objects.filter(userId=current_user).update(total_coin=new_coin)

#                 # return Response({"Decrypted_Data": decrypted_data, "Updated_Data": updated_data})
#                 return Response({"code": 0, "msg": "success"})
#             else:
#                 return Response("The outtrade number doesn't exist .")
#     else:
#         return Response(" only methods get and post allowed .")


# @api_view(["GET", "POST"])
# @csrf_exempt
# def dummy_dec(request):
#     # Initialise environment variables
#     env = environ.Env()
#     environ.Env.read_env()
#     if request.method == "POST" or request.method == "GET":
#         payload = request.body
#         # payload = json.loads(request.data)
#         try:
#             decrypted_data = Telebirr.decrypt(
#                 public_key=env("Public_Key"), payload=payload
#             )
#         except Exception as e:
#             return Response(str(e))
#         else:
#             return Response(
#                 {
#                     "Decrypted_Data": decrypted_data,
#                 }
#             )
# return Response({"code": 0, "msg": "success"})


# class GiftAnalyticViewset(ModelViewSet):
#     queryset = Gift_Payment_info.objects.all()
#     serializer_class = Gift_payment_serializer
#     http_method_names = ["get", "head"]
#     pagination_class = MyPagination

#     def list(self, request, *args, **kwargs):
#         # response dict
#         response = {}

#         # Get query parameters and set default values
#         payment_method = self.request.query_params.get("payment_method", None)
#         user = self.request.query_params.get("user", None)

#         # The multiple queries using Q
#         filter_query = Q()
#         if payment_method:
#             # Build filter query based on query parameters
#             # filter_query = Q()
#             if payment_method == "telebirr":
#                 filter_query |= Q(payment_id__payment_method="telebirr")
#             elif payment_method == "Abysinia":
#                 filter_query |= Q(payment_id__payment_method="Abysinia")
#             elif payment_method == "telebirr_superApp":
#                 filter_query |= Q(
#                     payment_id_from_superapp__payment_method="telebirr_superApp"
#                 )
#             else:
#                 pass

#         # Filter using user if it exists
#         if not user:
#             gift_analytics = Gift_Payment_info.objects.all()
#         else:
#             gift_analytics = Gift_Payment_info.objects.filter(userId=user)

#         # get unique users
#         user_id_set = set()
#         for user in gift_analytics:
#             user_id_set.add(user.userId)

#         distinct_user_count = len(user_id_set)

#         # if filter query exists , filter
#         if filter_query:
#             subscriptions = subscriptions.filter(filter_query)

#         # apply pagination
#         gift_analytics = self.paginate_queryset(gift_analytics)
#         paginated_user_ids = self.paginate_queryset(list(user_id_set))

#         # Build response
#         response["count"] = distinct_user_count
#         response["result"] = []

#         # loop through users
#         for user in paginated_user_ids:
#             # get data from haile
#             user_identity = get_identity(user)

#             # Per user
#             per_user = (
#                 Gift_Payment_info.objects.filter(userId=user)
#                 .order_by("created_at")
#                 .values("userId", "payment_amount", "payment_method", "created_at")
#             )
#             # total per user
#             total_per_user = per_user.aggregate(total_per_user=Sum("payment_amount"))

#             # final result dictionary
#             final_result_dictionary = {}
#             for key, value in user_identity.items():
#                 final_result_dictionary[key] = value

#             # final_result_dictionary["user_identity"] = user_identity
#             final_result_dictionary["per_user"] = per_user
#             # new change
#             for key, value in total_per_user.items():
#                 final_result_dictionary[key] = value
#             # append results to result
#             response["result"].append(final_result_dictionary)

#         # the final response
#         return self.get_paginated_response(response)
