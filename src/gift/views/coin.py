from gift.models import Coin
from gift.serializers import Coin_info_serializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from utilities.custom_pagination import CustomPagination


class CoinViewset(ModelViewSet):
    queryset = Coin.objects.all()
    serializer_class = Coin_info_serializer
    http_method_names = ["get", "head"]
    pagination_class=CustomPagination

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            res= self.get_paginated_response(Coin.objects.filter(userId=user_id).values())
            return Response(res,status=status.HTTP_200_OK)


        # use queryset directly without calling values()
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

       