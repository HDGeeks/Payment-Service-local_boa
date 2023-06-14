from telebirr.models import TrackRevenueRatePercentage
from telebirr.serializers import Track_revenue_rate_serializer
from rest_framework.viewsets import ModelViewSet


class TrackRevenueViewset(ModelViewSet):
    serializer_class = Track_revenue_rate_serializer
    queryset = TrackRevenueRatePercentage.objects.all()
