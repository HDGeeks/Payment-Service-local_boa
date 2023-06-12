import json
import environ

from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from django.db.models import Q

from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utilities.pagination import MyPagination

from super_app.models import *

from utilities.identity import get_identity
from utilities.telebirrApi import Telebirr
from utilities.send_to_telebirr import send_to_telebirr
from utilities.generate_nonce import generate_nonce

from super_app.models import Superapp_Payment_info
from utilities.validate import subs_data

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

from .models import Subscription, Subscription_Payment_info, SubscriptionFee
from .serializers import (
    Subscription_fee_serializer,
    Subscription_payment_serializer,
    subscriptionSerializer,
    SearchsubscriptionSerializer,
)

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    "/Users/hd/Desktop/Zema/zema_new_local_boa/Payment-Service-local_boa/serviceAccountKey.json"
)
firebase_admin.initialize_app(cred)


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


@api_view(["GET"])
def subscribers_count(request):
    subsecribed_users_count = Subscription.objects.all().count()
    monthly_subsecribed_users_count = Subscription.objects.filter(
        sub_type="MONTHLY"
    ).count()
    yearly_subsecribed_users_count = Subscription.objects.filter(
        sub_type="YEARLY"
    ).count()

    # Today
    today = date.today()
    # This year subscribed users
    this_year_subscribed_users = Subscription.objects.filter(
        created_at__year=today.year
    ).count()
    # This month subscribed users
    this_month_subscribed_users = Subscription.objects.filter(
        created_at__month=today.month
    ).count()
    # Past week
    one_week_ago = datetime.today() - timedelta(days=7)

    this_week_subscribed_users = Subscription.objects.filter(
        created_at__gte=one_week_ago
    ).count()

    return Response(
        {
            "subsecribed_users_count": subsecribed_users_count,
            "monthly_subsecribed_users_count": monthly_subsecribed_users_count,
            "yearly_subsecribed_users_count": yearly_subsecribed_users_count,
            "this_year_subscribed_users": this_year_subscribed_users,
            "this_month_subscribed_users": this_month_subscribed_users,
            "this_week_subscribed_users": this_week_subscribed_users,
        }
    )


class SubscriptionFeeViewset(ModelViewSet):
    serializer_class = Subscription_fee_serializer
    queryset = SubscriptionFee.objects.all()

    def list(self, request, *args, **kwargs):
        sub_fee = self.request.query_params.get("subFee")
        if sub_fee:
            if sub_fee == "all":
                return Response(self.queryset.values())
        return Response(self.queryset.values().order_by("-created_at")[0])

        # return super().get_queryset()


class SubscriptionViewset(ModelViewSet):
    serializer_class = subscriptionSerializer
    queryset = Subscription.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.query_params.get("user")
        if user is not None:
            queryset = Subscription.objects.filter(user_id=user).values()
            return Response(queryset, status=status.HTTP_200_OK)

        else:
            return Response(Subscription.objects.all().values())

    def create(self, request, *args, **kwargs):
        payment_id = request.data["payment_id"]
        payment_id_from_superapp = request.data["payment_id_from_superapp"]
        print("======================================", payment_id)
        print("========================================", payment_id_from_superapp)
        if payment_id and payment_id_from_superapp:
            return Response(
                "Only one type of payment is supported . Multiple payment provided .",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif payment_id is None and payment_id_from_superapp is None:
            return Response(
                "Provide one payment Id please .", status=status.HTTP_400_BAD_REQUEST
            )

        if payment_id_from_superapp:
            # check if the payment id already exists in subscription
            verify_payment_id = Subscription.objects.filter(
                payment_id_from_superapp=request.data["payment_id_from_superapp"]
            ).values("payment_id_from_superapp")

            # Verify payment state is complete
            verify_payment_state = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("payment_state")[0]["payment_state"]

            # Check if the current requesting user made the payment
            verify_userId = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("userId")[0]["userId"]

            # Verify if the payment was made for subscription
            verify_payment_title = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("payment_title")[0]["payment_title"]

            if verify_payment_id:
                return Response(
                    {
                        "message": f"This payment id {verify_payment_id} is already used for existing subscription."
                    }
                )
            if verify_userId != request.data["user_id"]:
                return Response(
                    {"message": "This payment provided was not made by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned as subscription."
                    }
                )
            elif verify_payment_title.upper() != "SUBSCRIPTION":
                return Response(
                    {
                        "message": "The payment reason is not for subscription, cannot be assigned."
                    }
                )

            try:
                subs_data_saved = subs_data(request.data)
            except Exception as e:
                return Response(str(e))

            if request.data["sub_type"] == "MONTHLY":
                date = datetime.now()
                new_paid_until_monthly = date + relativedelta(months=+1)

                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "payment_id_from_superapp": request.data[
                        "payment_id_from_superapp"
                    ],
                    "sub_type": "MONTHLY",
                    "paid_until": new_paid_until_monthly,
                    "is_Subscriebed": True,
                }
            else:
                # request.data["sub_type"] == "YEARLY"
                date = datetime.now()
                new_paid_until_yearly = date + relativedelta(months=+12)

                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "payment_id_from_superapp": request.data[
                        "payment_id_from_superapp"
                    ],
                    "sub_type": "YEARLY",
                    "paid_until": new_paid_until_yearly,
                    "is_Subscriebed": True,
                }

            serializer = subscriptionSerializer(data=subs_data_saved)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            # check if the payment id is already used for subscription ,
            verify_payment_id = Subscription.objects.filter(
                payment_id=request.data["payment_id"]
            ).values("payment_id")
            print("========================================.", verify_payment_id)
            # make sure payment state is complete in the payment table
            verify_payment_state = Subscription_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]

            # make sure the payment was done by the subscribing user
            verify_userId = Subscription_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]

            if verify_payment_id:
                return Response(
                    {
                        "message": f"This payment id {verify_payment_id} is already used for other subscription."
                    }
                )
            if verify_userId != request.data["user_id"]:
                return Response(
                    {
                        "message": "The user {verify_userId} made the payment , not the current user ."
                    }
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned as subscription."
                    }
                )

            try:
                subs_data_saved_normal = subs_data(request.data)
            except Exception as e:
                return Response(str(e))

            if request.data["sub_type"] == "MONTHLY":
                date = datetime.now()
                new_paid_until_monthly = date + relativedelta(months=+1)

                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "payment_id_from_superapp": request.data[
                        "payment_id_from_superapp"
                    ],
                    "sub_type": "MONTHLY",
                    "paid_until": new_paid_until_monthly,
                    "is_Subscriebed": True,
                }
            else:
                # request.data["sub_type"] == "YEARLY"
                date = datetime.now()
                new_paid_until_yearly = date + relativedelta(months=+12)

                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "payment_id_from_superapp": request.data[
                        "payment_id_from_superapp"
                    ],
                    "sub_type": "YEARLY",
                    "paid_until": new_paid_until_yearly,
                    "is_Subscriebed": True,
                }

            serializer = subscriptionSerializer(data=subs_data_saved_normal)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewset(ModelViewSet):
    serializer_class = Subscription_payment_serializer
    queryset = Subscription_Payment_info.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            if user_id == "all_users":
                return Response(
                    Subscription_Payment_info.objects.values("userId").annotate(
                        total_amount_per_user=Sum("payment_amount")
                    )
                )
            elif user_id == "total":
                return Response(
                    Subscription_Payment_info.objects.aggregate(
                        total_money_from_purchased_tracks=Sum("payment_amount")
                    )
                )
            else:
                per_user = Subscription_Payment_info.objects.filter(
                    userId=user_id
                ).values("userId", "payment_amount", "created_at")

                total_per_user = per_user.aggregate(
                    total_per_user=Sum("payment_amount")
                )
                return Response(
                    {"per_user": per_user, "total_per_this_user": total_per_user},
                    status=status.HTTP_200_OK,
                )

        else:
            return Response(Subscription_Payment_info.objects.all().values())

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] != "telebirr":
            return super().create(request, *args, **kwargs)
        return Response("telebirr payment is not saved using this api .")


class SubsAnalyticViewset(ModelViewSet):
    queryset = Subscription_Payment_info.objects.all()
    serializer_class = Subscription_payment_serializer
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

        response["count"] = (
            Subscription_Payment_info.objects.values("userId").distinct().count()
        )

        response["result"] = []

        for user in unique_user_ids:
            # get data from haile
            user_identity = get_identity(user)
            # Per user
            per_user = (
                Subscription_Payment_info.objects.filter(userId=user)
                .order_by("created_at")
                .values("userId", "payment_amount", "payment_method", "created_at")
            )
            # total per user
            total_per_user = per_user.aggregate(total_per_user=Sum("payment_amount"))
            # final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key] = value

            final_result_dictionary["per_user"] = per_user
            for key, value in total_per_user.items():
                final_result_dictionary[key] = value

            # append results to result
            response["result"].append(final_result_dictionary)
        return Response(response)


class SubscribeWithTelebirrViewSet(ModelViewSet):
    serializer_class = Subscription_payment_serializer
    queryset = Subscription_Payment_info.objects.all()

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            try:
                nonce = ""
                outtrade = ""
                outtrade = generate_nonce(16)

                nonce = generate_nonce(16)
                amount = request.data["payment_amount"]
                notify_type = "subs"
                pay = send_to_telebirr(amount, nonce, outtrade, notify_type)
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
                    serializer = Subscription_payment_serializer(data=content)
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


# class SubscribersAnalytics(ModelViewSet):
#     queryset = Subscription.objects.all()
#     serializer_class = subscriptionSerializer

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
#         print(data)
#         for item in data:
#             list_of_users.append(item["user_id"])
#         print(list_of_users)

#         unique_user_ids = list(set(list_of_users))
#         print("===================================>", unique_user_ids)
#         # response["count"] = unique_user_ids.__len__()
#         response["count"] = Subscription.objects.values("user_id").distinct().count()

#         response["result"] = []
#         for user in unique_user_ids:
#             # get data from haile
#             user_identity = get_identity(user)

#             # Per user
#             per_user = (
#                 Subscription.objects.filter(user_id=user)
#                 .order_by("created_at")
#                 .values("id", "user_id", "sub_type", "subscription_date", "created_at")
#             )

#             # total per user
#             total_per_user = per_user.count()

#             # final result dictionary
#             final_result_dictionary = {}
#             # include user idntity in the dict
#             for key, value in user_identity.items():
#                 final_result_dictionary[key] = value
#             # include per user in to dict
#             final_result_dictionary["per_user"] = per_user
#             # include total per user in to dict
#             final_result_dictionary["total_per_user"] = total_per_user
#             # append results to result
#             response["result"].append(final_result_dictionary)

#         return Response(response)


class SubscribersAnalytics(ModelViewSet):
    serializer_class = subscriptionSerializer
    queryset = Subscription.objects.all()
    http_method_names = ["get", "head"]
    pagination_class = MyPagination

    def list(self, request, *args, **kwargs):
        # The response object
        response = {}

        # Get query parameters and set default values
        payment_method = self.request.query_params.get("payment_method", None)
        user = self.request.query_params.get("user", None)
        filter_query = Q()
        if payment_method:
            # Build filter query based on query parameters
            # filter_query = Q()
            if payment_method == "telebirr":
                filter_query |= Q(payment_id__payment_method="telebirr")
            elif payment_method == "Abysinia":
                filter_query |= Q(payment_id__payment_method="Abysinia")
            elif payment_method == "telebirr_superApp":
                filter_query |= Q(
                    payment_id_from_superapp__payment_method="telebirr_superApp"
                )
            else:
                pass

        if not user:
            # Get all subscriptions and apply filter query if it exists
            subscriptions = Subscription.objects.all()
        else:
            subscriptions = Subscription.objects.filter(user_id=user)

        user_id_set = set()
        for subscription in subscriptions:
            user_id_set.add(subscription.user_id)
        distinct_user_count = len(user_id_set)
        print("======================== >", sorted(user_id_set))
        # Paginate the user IDs
        # paginated_user_ids = self.paginate_queryset(user_id_set, request)
        subscriptions = self.paginate_queryset(subscriptions)
        paginated_user_ids = self.paginate_queryset(list(user_id_set))

        # # Filter subscriptions by user ID if user ID is specified
        # if user_id:
        #     subscriptions = subscriptions.filter(user_id=user_id)

        if filter_query:
            subscriptions = subscriptions.filter(filter_query)

        subscriptions = self.paginate_queryset(subscriptions)
        print("-------------------------------------", subscriptions)

        # Count the number of distinct user IDs by iterating through the Subscription objects

        # Build response
        response["count"] = distinct_user_count
        response["result"] = []

        for user_id in paginated_user_ids:
            # Get user identity
            user_identity = get_identity(user_id)

            # Get subscriptions for the user and apply filter query if it exists
            per_user = Subscription.objects.filter(user_id=user_id)
            if filter_query:
                per_user = per_user.filter(filter_query).order_by("user_id")

            # Get total subscriptions for the user
            total_per_user = per_user.count()

            # Build final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key] = value
            final_result_dictionary["per_user"] = per_user.values(
                "id",
                "user_id",
                "sub_type",
                "subscription_date",
                "paid_until",
                "payment_id__payment_method",
                "payment_id_from_superapp__payment_method",
                "created_at",
            )
            final_result_dictionary["total_per_user"] = total_per_user

            # Append result to response
            response["result"].append(final_result_dictionary)

      
        return self.get_paginated_response(response)
        # return Response(response)


class SearchSubsrcriptionViewset(ModelViewSet):
    serializer_class = SearchsubscriptionSerializer
    queryset = Subscription.objects.all()

    def list(self, request, *args, **kwargs):
        email_id = self.request.query_params.get("email")
        phone = self.request.query_params.get("phone")

        if not email_id and not phone:
            return Response("Provide email or phone number please .")

        if email_id:
            uid = get_user_id_by_email(email_id)
            return Response(uid)

        if phone:
            uid = get_user_id_by_phone_number(phone)
            return uid


# Obtain a user ID using their email or phone number
def get_user_id_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        print(f"User with email {email} has ID: {user.uid}")
        return user.uid
    except Exception as e:
        print(f"Error getting user with email {email}: {e}")


def get_user_id_by_phone_number(phone_number):
    try:
        user = auth.get_user_by_phone_number(phone_number)
        print(f"User with phone number {phone_number} has ID: {user.uid}")
        return user.uid
    except Exception as e:
        print(f"Error getting user with phone number {phone_number}: {e}")
