from gift.models import Gift_Revenue_Rate
from gift.serializers import Gift_revenue_rate_serializer
from rest_framework.viewsets import ModelViewSet


class GiftRevenuViewset(ModelViewSet):
    queryset = Gift_Revenue_Rate.objects.all()
    serializer_class = Gift_revenue_rate_serializer
