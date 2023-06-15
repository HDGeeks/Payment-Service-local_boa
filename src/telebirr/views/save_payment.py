from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer
from utilities.custom_pagination import CustomPagination


class SavePurchasePaymentViewSet(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            return Response("telebirr payment is not saved using this api .")
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        user = self.request.query_params.get("user")
        queryset = self.queryset.order_by("-created_at")  # apply ordering here

        if user:
            try:
                user_obj = queryset.filter(userId=user)
            except Payment_info.DoesNotExist:
                raise NotFound("Record does not exist for this user.")

            serializer = self.get_serializer(user_obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # use queryset directly without calling values()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
