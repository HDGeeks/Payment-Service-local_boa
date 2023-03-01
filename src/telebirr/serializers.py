from dataclasses import fields
from rest_framework import serializers
from .models import Purcahsed_album, Purcahsed_track, Payment_info


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
    class Meta:
        model = Payment_info
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
