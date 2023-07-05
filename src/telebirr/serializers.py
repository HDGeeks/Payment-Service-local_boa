from dataclasses import fields
from rest_framework import serializers
from utilities.identity import get_identity
from .models import (
    Purcahsed_album,
    Purcahsed_track,
    Payment_info,
    TrackRevenueRatePercentage,
    BoaWebhook,
)


class Purcahsed_track_serializer(serializers.ModelSerializer):
    class Meta:
        model = Purcahsed_track
        fields = [
            "id",
            "userId",
            "payment_id",
            "trackId",
            "track_price_amount",
            "isPurcahsed",
        ]


class Track_revenue_rate_serializer(serializers.ModelSerializer):
    class Meta:
        model = TrackRevenueRatePercentage
        fields = "__all__"


class Purcahsed_album_serializer(serializers.ModelSerializer):
    class Meta:
        model = Purcahsed_album

        fields = [
            "id",
            "userId",
            "payment_id",
            "albumId",
            "album_price_amount",
            "isPurcahsed",
        ]


class Payment_info_serializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = Payment_info
        fields = [
            "id",
            "userId",
            "payment_amount",
            "payment_method",
            "outTradeNo",
            "boa_webhook_id",
            "msisdn",
            "tradeNo",
            "transactionNo",
            "payment_state",
            "user_detail",
        ]

    def get_user_detail(self, obj):
        userId = obj.userId
        user_detail = {}
        try:
            user = get_identity(userId)
            user_detail["name"] = user["display_name"]
            user_detail["identifier"] = user["identifier"]
        except:
            user_detail = "Detail Not found."
        return user_detail


class Boa_Webhook_serializer(serializers.ModelSerializer):
    class Meta:
        model = BoaWebhook
        fields = "__all__"


# class Boa_Webhook_for_dm_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = BoaWebhookForDM
#         fields='__all__'
