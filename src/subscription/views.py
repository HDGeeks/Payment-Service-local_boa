import json
import environ

from datetime import date, datetime, timedelta
from dateutil.relativedelta import *

from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from super_app.models import *

from utilities.identity import get_identity
from utilities.telebirrApi import Telebirr
from utilities.send_to_telebirr import send_to_telebirr
from utilities.generate_nonce import generate_nonce

from .models import Subscription, Subscription_Payment_info, SubscriptionFee
from .serializers import (Subscription_fee_serializer,
                          Subscription_payment_serializer,
                          subscriptionSerializer)

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
        return Response(self.queryset.values().order_by('-created_at')[0])
        
 
      
        #return super().get_queryset()
class SubscriptionViewset(ModelViewSet):
    serializer_class = subscriptionSerializer
    queryset = Subscription.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.query_params.get("user")
        if user is not None:
            queryset = Subscription.objects.filter(user_id=user)
            return Response(queryset)

        else:
            return Response(Subscription.objects.all().values())

    def create(self, request, *args, **kwargs):
        query_params = request.GET
        q = query_params.get("payment_method")
        if q == "superApp":
            verify_payment_id = Superapp_Payment_info.objects.filter(
                payment_id=request.data["payment_id"]
            ).values("payment_id")
            verify_payment_state = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]
            verify_userId = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]
            verify_payment_title = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_title")[0]["payment_title"]
            if verify_payment_id:
                return Response(
                    {
                        "message": f"This payment id {verify_payment_id} is already used for other subscription."
                    }
                )
            if verify_userId != request.data["user_id"]:
                return Response(
                    {"message": "This subscription is not purchased by this user ."}
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

            elif request.data["sub_type"] == "MONTHLY":
                date = datetime.now()
                new_paid_until_monthly = date + relativedelta(months=+1)
                # new_paid_until = date + timedelta(months=+1)
                # request.data._mutable = True
                # request.data['paid_until']=new_paid_until
                # request.data._mutable = False
                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "sub_type": "MONTHLY",
                    "paid_until": new_paid_until_monthly,
                    "is_Subscriebed": True,
                }
            elif request.data["sub_type"] == "YEARLY":
                date = datetime.now()
                new_paid_until_yearly = date + relativedelta(months=+12)

                # # remember old state
                # request.data._mutable = True
                # request.data['paid_until']=new_paid_until
                # request.data._mutable = False
                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "sub_type": "MONTHLY",
                    "paid_until": new_paid_until_yearly,
                    "is_Subscriebed": True,
                }

            serializer = subscriptionSerializer(data=pay_load)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            verify_payment_id = Subscription.objects.filter(
                payment_id=request.data["payment_id"]
            ).values("payment_id")
            verify_payment_state = Subscription_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]
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
                    {"message": "This subscription is not purchased by this user ."}
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned as subscription."
                    }
                )

            elif request.data["sub_type"] == "MONTHLY":
                date = datetime.now()
                new_paid_until_monthly = date + relativedelta(months=+1)

                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "sub_type": "MONTHLY",
                    "paid_until": new_paid_until_monthly,
                    "is_Subscriebed": True,
                }
            elif request.data["sub_type"] == "YEARLY":
                date = datetime.now()
                new_paid_until_yearly = date + relativedelta(months=+12)

                # # remember old state
                # request.data._mutable = True
                # request.data['paid_until']=new_paid_until
                # request.data._mutable = False
                pay_load = {}
                pay_load = {
                    "user_id": request.data["user_id"],
                    "payment_id": request.data["payment_id"],
                    "sub_type": "YEARLY",
                    "paid_until": new_paid_until_yearly,
                    "is_Subscriebed": True,
                }

            serializer = subscriptionSerializer(data=pay_load)
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
    http_method_names = ['get', 'head']

    def list(self, request, *args, **kwargs):
        response = {}
        data = json.loads(json.dumps(
            super().list(request, *args, **kwargs).data["results"]))
        # list of user_ids
        list_of_users = []
        for item in data:
            list_of_users.append(item['userId'])

        unique_user_ids = list(set(list_of_users))

        response["count"] = unique_user_ids.__len__()
        response["result"] = []
        for user in unique_user_ids:
           # get data from haile
           user_identity = get_identity(user)
           # Per user
           per_user = Subscription_Payment_info.objects.filter(
               userId=user).values("userId", "payment_amount")
           # total per user
           total_per_user = per_user.aggregate(
               total_per_user=Sum("payment_amount"))
           # final result dictionary
           final_result_dictionary = {}
           final_result_dictionary['user_identity'] = user_identity
           final_result_dictionary['per_user'] = per_user
           final_result_dictionary['total_per_user'] = total_per_user
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
                notify_type="subs"
                pay = send_to_telebirr(amount, nonce, outtrade,notify_type)
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





