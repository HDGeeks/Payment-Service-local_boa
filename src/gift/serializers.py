from rest_framework import serializers
from .models import Gift_Payment_info, Gift_Info, Coin, Gift_Revenue_Rate


class Gift_payment_serializer(serializers.ModelSerializer):
    class Meta:
        model = Gift_Payment_info
        fields = [
            "userId",
            "payment_amount",
            "payment_method",
            "outTradeNo",
            "msisdn",
            "tradeNo",
            "transactionNo",
            "payment_state",
        ]


class Gift_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Gift_Info
        fields = [
            "id",
            "userId",
            "ArtistId",
            "gift_amount",
        ]


class Coin_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ["userId", "total_coin"]


class Gift_revenue_rate_serializer(serializers.ModelSerializer):
    class Meta:
        model = Gift_Revenue_Rate
        fields = "__all__"
