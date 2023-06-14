from gift.models import Gift_Payment_info
from gift.serializers import Gift_payment_serializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from rest_framework import status


class BuyGiftViewSet(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

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
        return Response(
            Gift_Payment_info.objects.all().values(), status=status.HTTP_200_OK
        )
