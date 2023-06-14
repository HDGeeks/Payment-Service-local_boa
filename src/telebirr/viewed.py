# import json
# from django.shortcuts import redirect, render
# from django.db.models import Q


# import environ
# from django.db.models import Sum
# from django.views.decorators.csrf import csrf_exempt

# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.viewsets import ModelViewSet
# from rest_framework.exceptions import NotFound
# from gift.pagination import MyPagination


# from utilities.identity import get_identity
# from utilities.telebirrApi import Telebirr
# from utilities.send_to_telebirr import send_to_telebirr
# from utilities.generate_nonce import generate_nonce

# from .models import (
#     BoaWebhook,
#     Payment_info,
#     Purcahsed_album,
#     Purcahsed_track,
#     TrackRevenueRatePercentage,
# )
# from .serializers import (
#     Boa_Webhook_serializer,
#     Payment_info_serializer,
#     Purcahsed_album_serializer,
#     Purcahsed_track_serializer,
#     Track_revenue_rate_serializer,
# )


# # Initialise environment variables
# env = environ.Env()
# environ.Env.read_env(DEBUG=(bool, False))


# class SavePurchasePaymentViewSet(ModelViewSet):
#     """
#     This view make and external api call,
#     to telebirr platform ,
#     save the result and return
#     the data generated as json object
#     """

#     queryset = Payment_info.objects.all()
#     serializer_class = Payment_info_serializer

#     def create(self, request, *args, **kwargs):
#         if request.data["payment_method"] == "telebirr":
#             return Response("telebirr payment is not saved using this api .")
#         return super().create(request, *args, **kwargs)

#     def list(self, request, *args, **kwargs):
#         # this is haile code

#         user = self.request.query_params.get("user")
#         if user:
#             try:
#                 user_obj = Payment_info.objects.filter(userId=user).values(
#                     "id", "userId", "payment_amount"
#                 )
#             except Payment_info.DoesNotExist:
#                 raise NotFound("Record does not exist for this user .")

#             return Response(user_obj, status=status.HTTP_200_OK)

#         return Response(self.queryset.values(), status=status.HTTP_200_OK)

#         return Response(user_obj,status=status.HTTP_200_OK)
# except BaseException as e:
#     info = Payment_info.objects.all()
#     serializer = Payment_info_serializer(info, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# class PurchaseWithTelebirrViewSet(ModelViewSet):
#     queryset = Payment_info.objects.all()
#     serializer_class = Payment_info_serializer

#     def create(self, request, *args, **kwargs):
#         if request.data["payment_method"] == "telebirr":
#             try:
#                 nonce = ""
#                 outtrade = ""
#                 outtrade = generate_nonce(16)
#                 nonce = generate_nonce(16)
#                 notify_type = "purchase"

#                 amount = request.data["payment_amount"]
#                 pay = send_to_telebirr(amount, nonce, outtrade, notify_type)
#                 if pay["message"] == "Operation successful":
#                     content = {
#                         "userId": request.data["userId"],
#                         "payment_amount": request.data["payment_amount"],
#                         "payment_method": request.data["payment_method"],
#                         "outTradeNo": outtrade,
#                         "msisdn": "",
#                         "tradeNo": "",
#                         "transactionNo": "",
#                         "payment_state": request.data["payment_state"],
#                     }
#                     serializer = Payment_info_serializer(data=content)
#                     if serializer.is_valid(raise_exception=True):
#                         serializer.save()
#                         return Response({"pay": pay, "data": serializer.data})

#                 return Response(
#                     {
#                         "message": pay["message"],
#                         "status": status.HTTP_400_BAD_REQUEST,
#                     }
#                 )

#             except BaseException as e:
#                 return Response({"error message": str(e)})

#         else:
#             return Response(
#                 {
#                     "msg": " payment method is not telebirr",
#                     "status": "status.HTTP_400_BAD_REQUEST",
#                 }
#             )


# class PurchasedAlbumsViewset(ModelViewSet):
#     """
#     check the request data ,
#     check the notify url and its results ,
#     update the subscription model is subscribed field true

#     """

#     serializer_class = Purcahsed_album_serializer
#     queryset = Purcahsed_album.objects.all()

#     def create(self, request, *args, **kwargs):
#         verify_amount = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("payment_amount")[0]["payment_amount"]
#         verify_payment_state = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("payment_state")[0]["payment_state"]
#         verify_userId = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("userId")[0]["userId"]
#         if verify_amount < int(request.data["album_price_amount"]):
#             return Response(
#                 {
#                     "message": "The price for this album cannot exceed the actual payment made ."
#                 }
#             )
#         elif verify_userId != request.data["userId"]:
#             return Response({"message": "This content is not purcahsed by this user ."})
#         elif verify_payment_state.upper() != "COMPLETED":
#             return Response(
#                 {
#                     "message": "The payment status is still pending , cannot be assigned ."
#                 }
#             )
#         else:
#             serializer = Purcahsed_album_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)


# class PurchasedTracksViewset(ModelViewSet):
#     """
#     check the request data ,
#     check the notify url and its results ,
#     update the subscription model is subscribed field true

#     """

#     serializer_class = Purcahsed_track_serializer
#     queryset = Purcahsed_track.objects.all()

#     def list(self, request, *args, **kwargs):
#         user_id = self.request.query_params.get("user")
#         if user_id:
#             if user_id == "all_users":
#                 return Response(
#                     Purcahsed_track.objects.values("userId").annotate(
#                         total_amount_per_user=Sum("track_price_amount")
#                     )
#                 )
#             elif user_id == "total":
#                 return Response(
#                     Purcahsed_track.objects.aggregate(
#                         total_money_from_purchased_tracks=Sum("track_price_amount")
#                     )
#                 )
#             else:
#                 per_user = Purcahsed_track.objects.filter(userId=user_id).values(
#                     "userId", "trackId", "track_price_amount", "created_at"
#                 )

#                 total_per_user = per_user.aggregate(
#                     total_per_user=Sum("track_price_amount")
#                 )
#                 return Response(
#                     {"per_user": per_user, "total_per_this_user": total_per_user},
#                     status=status.HTTP_200_OK,
#                 )

#         else:
#             return Response(Purcahsed_track.objects.all().values())

#     def create(self, request, *args, **kwargs):
#         verify_amount = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("payment_amount")[0]["payment_amount"]
#         verify_userId = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("userId")[0]["userId"]
#         verify_payment_state = Payment_info.objects.filter(
#             id=request.data["payment_id"]
#         ).values("payment_state")[0]["payment_state"]

#         if verify_amount < int(request.data["track_price_amount"]):
#             return Response(
#                 {
#                     "message": "The price for this track cannot exceed the actual payment made ."
#                 }
#             )
#         elif verify_userId != request.data["userId"]:
#             return Response({"message": "This content is not purcahsed by this user ."})
#         elif verify_payment_state.upper() != "COMPLETED":
#             return Response(
#                 {
#                     "message": "The payment status is still pending , cannot be assigned ."
#                 }
#             )
#         else:
#             serializer = Purcahsed_track_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)


# class TrackRevenueViewset(ModelViewSet):
#     serializer_class = Track_revenue_rate_serializer
#     queryset = TrackRevenueRatePercentage.objects.all()


# class PurchaseAnalyticViewset(ModelViewSet):
#     queryset = Payment_info.objects.all()
#     serializer_class = Payment_info_serializer
#     http_method_names = ["get", "head"]
#     pagination_class = MyPagination

#     def list(self, request, *args, **kwargs):
#         # The response object
#         response = {}
#         data = json.loads(
#             json.dumps(super().list(request, *args, **kwargs).data["results"])
#         )
#         # list of user_ids
#         list_of_users = []
#         for item in data:
#             list_of_users.append(item["userId"])

#         unique_user_ids = list(set(list_of_users))

#         # response["count"] = unique_user_ids.__len__()
#         response["count"] = Payment_info.objects.values("userId").distinct().count()

#         response["result"] = []
#         for user in unique_user_ids:
#             # get data from haile
#             user_identity = get_identity(user)

#             # Per user
#             per_user = (
#                 Payment_info.objects.filter(userId=user)
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

#         return Response(response)


# @api_view(
#     [
#         "GET",
#         "POST",
#     ]
# )
# @csrf_exempt
# def notify(request):
#     if request.method == "POST" or request.method == "GET":
#         if not request.body:
#             return Response("The request object (request.body) is empty .")
#         else:
#             payload = request.body
#             decrypted_data = Telebirr.decrypt(
#                 public_key=env("Public_Key"), payload=payload
#             )

#             outt = decrypted_data["outTradeNo"]

#             fetch_data = Payment_info.objects.filter(outTradeNo=outt).values()

#             if not fetch_data.exists():
#                 return Response("The outtrade number doesn't exist .")

#             update_data = Payment_info.objects.filter(
#                 outTradeNo=decrypted_data["outTradeNo"]
#             ).update(
#                 msisdn=decrypted_data["msisdn"],
#                 tradeNo=decrypted_data["tradeNo"],
#                 transactionNo=decrypted_data["transactionNo"],
#                 payment_state="completed",
#             )

#             updated_data = Payment_info.objects.filter(outTradeNo=outt).values()

#             # return Response({"decrypted_data": decrypted_data, "updated_data": updated_data})
#             return Response({"code": 0, "msg": "success"})
#     else:
#         return Response(" only methods get and post allowed .")


# class BoaWebhookViewset(ModelViewSet):
#     serializer_class = Boa_Webhook_serializer
#     queryset = BoaWebhook.objects.all()

#     def list(self, request, *args, **kwargs):
#         user = self.request.query_params.get("user")
#         if user:
#             try:
#                 result = (
#                     BoaWebhook.objects.filter(data__req_reference_number=user)
#                     .values("id", "data__req_amount", "data__req_reference_number")
#                     .latest("created_at")
#                 )
#             except BoaWebhook.DoesNotExist:
#                 raise NotFound("Record does not exist for this user .")

#             return Response(result, status=status.HTTP_200_OK)

#         return Response(self.queryset.values(), status=status.HTTP_200_OK)

#     def create(self, request, *args, **kwargs):
#         payload = {"data": request.data}
#         serializer = Boa_Webhook_serializer(data=payload)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         if request.data["decision"] == "DECLINE" or request.data["decision"] == "ERROR":
#             return redirect(
#                 "https://zemastroragev100.blob.core.windows.net/boa/failedpage.html"
#             )

#         elif request.data["reason_code"] == "481":
#             return redirect(
#                 "https://zemastroragev100.blob.core.windows.net/boa/success_but_flagged.html"
#             )

#         elif (
#             request.data["reason_code"] == "100"
#             and request.data["decision"] == "ACCEPT"
#         ):
#             return redirect(
#                 "https://zemastroragev100.blob.core.windows.net/boa/successpage.html"
#             )
#         else:
#             return Response(
#                 "Transaction failed . Contact support .",
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


# class BoaWebhookForDMViewset(ModelViewSet):
#     serializer_class = Boa_Webhook_serializer
#     queryset = BoaWebhook.objects.all()

#     def list(self, request, *args, **kwargs):
#         return Response(
#             self.queryset.filter(data__reason_code="481")
#             .values()
#             .order_by("-created_at"),
#             status=status.HTTP_200_OK,
#         )


# class PurchsedTrackAnalytics(ModelViewSet):
#     serializer_class = Purcahsed_track_serializer
#     queryset = Purcahsed_track.objects.all()
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
#             track_analytics = Purcahsed_track.objects.all()
#         else:
#             track_analytics = Purcahsed_track.objects.filter(userId=user)

#         # get unique users
#         user_id_set = set()
#         for user in track_analytics:
#             user_id_set.add(user.userId)

#         distinct_user_count = len(user_id_set)

#         # if filter query exists , filter
#         if filter_query:
#             track_analytics = track_analytics.filter(filter_query)

#         # apply pagination
#         track_analytics = self.paginate_queryset(track_analytics)
#         paginated_user_ids = self.paginate_queryset(list(user_id_set))

#         # Build response
#         response["count"] = distinct_user_count
#         response["result"] = []

#         for user in paginated_user_ids:
#             # get data from haile
#             user_identity = get_identity(user)

#             # Per user
#             per_user = (
#                 Purcahsed_track.objects.filter(userId=user)
#                 .order_by("created_at")
#                 .values(
#                     "id",
#                     "userId",
#                     "trackId",
#                     "track_price_amount",
#                     "payment_id",
#                     "created_at",
#                 )
#             )

#             # total per user
#             total_per_user = per_user.aggregate(
#                 total_per_user=Sum("track_price_amount")
#             )

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
