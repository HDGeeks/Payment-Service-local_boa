from gift.models import Gift_Payment_info
from gift.serializers import Gift_payment_serializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from rest_framework import status
from utilities.custom_pagination import CustomPagination

class BuyGiftViewSet(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer
    pagination_class=CustomPagination

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            if user_id == "all":
                return Response(
                    Gift_Payment_info.objects.aggregate(
                        total_gift_payment_all_users=Sum("payment_amount")
                    )
                )

            else:
                per_user = Gift_Payment_info.objects.filter(userId=user_id).values(
                    "id", "userId", "payment_amount", "payment_method"
                )
                total_per_user = per_user.aggregate(
                    total_per_user=Sum("payment_amount")
                )
            return Response(
                {"per_user": per_user, "total_per_this_user": total_per_user},
                status=status.HTTP_200_OK,
            )
        else:
              # use queryset directly without calling values()
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(self.queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

       

       
