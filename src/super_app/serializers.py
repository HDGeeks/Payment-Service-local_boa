from .models import Superapp_Payment_info
from rest_framework.serializers import ModelSerializer
from dateutil.relativedelta import *


class Superapp_payment_serializer(ModelSerializer):
    class Meta:
        model = Superapp_Payment_info
        fields = [
            "id",
            "userId",
            "payment_amount",
            "payment_method",
            "payment_state",
            "payment_currency",
            "payment_title",
            "prepay_id",
            "merch_order_id",
            "created_at",
            "updated_at",
        ]
