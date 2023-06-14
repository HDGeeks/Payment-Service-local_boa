import environ
from dateutil.relativedelta import *
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from subscription.models import Subscription_Payment_info
from subscription.serializers import Subscription_payment_serializer

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


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
                        total_money_from_all_subscription=Sum("payment_amount")
                    )
                )
            else:
                sub_per_user = Subscription_Payment_info.objects.filter(
                    userId=user_id
                ).values("userId", "payment_amount", "created_at")

                total_sub_per_user = sub_per_user.aggregate(
                    total_per_user=Sum("payment_amount")
                )
                return Response(
                    {
                        "sub_per_user": sub_per_user,
                        "total_sub_per_user": total_sub_per_user,
                    },
                    status=status.HTTP_200_OK,
                )

        else:
            return Response(Subscription_Payment_info.objects.all().values())

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] != "telebirr":
            return super().create(request, *args, **kwargs)
        return Response("telebirr payment is not saved using this api .")
