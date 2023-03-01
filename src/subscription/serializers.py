from .models import Subscription, Subscription_Payment_info
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import datetime
from dateutil.relativedelta import *


class Subscription_payment_serializer(ModelSerializer):
    class Meta:
        model = Subscription_Payment_info
        fields = [
            "id",
            "userId",
            "payment_amount",
            "payment_method",
            "outTradeNo",
            "msisdn",
            "tradeNo",
            "transactionNo",
            "payment_state",
        ]


class subscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "user_id",
            "payment_id",
            "sub_type",
            "subscription_date",
            "paid_until",
            "is_Subscriebed",
        ]
