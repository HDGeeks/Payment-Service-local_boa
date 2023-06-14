from rest_framework.viewsets import ModelViewSet
from subscription.models import SubscriptionFee
from rest_framework.response import Response

from subscription.serializers import Subscription_fee_serializer


class SubscriptionFeeViewset(ModelViewSet):
    serializer_class = Subscription_fee_serializer
    queryset = SubscriptionFee.objects.all()

    def list(self, request, *args, **kwargs):
        sub_fee = self.request.query_params.get("subFee")
        if sub_fee:
            if sub_fee == "all":
                return Response(self.queryset.values())
        return Response(self.queryset.values().order_by("-created_at")[0])
