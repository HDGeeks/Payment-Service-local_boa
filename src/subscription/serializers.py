from .models import Subscription, Subscription_Payment_info, SubscriptionFee
from rest_framework.serializers import ModelSerializer
from dateutil.relativedelta import *


class Subscription_payment_serializer(ModelSerializer):
    class Meta:
        model = Subscription_Payment_info
        fields = [
            "id",
            "userId",
            "payment_amount",
            "payment_method",
            "boa_webhook_id",
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
            "payment_id_from_superapp",
            "sub_type",
            "subscription_date",
            "paid_until",
            "is_Subscriebed",
        ]


class Subscription_fee_serializer(ModelSerializer):
    class Meta:
        model = SubscriptionFee
        fields = "__all__"
