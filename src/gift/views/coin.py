from gift.models import Coin
from gift.serializers import Coin_info_serializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class CoinViewset(ModelViewSet):
    queryset = Coin.objects.all()
    serializer_class = Coin_info_serializer
    http_method_names = ["get", "head"]

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            return Response(Coin.objects.filter(userId=user_id).values())
        return Response(Coin.objects.all().values(), status=status.HTTP_200_OK)
