import environ
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from telebirr.models import Payment_info, Purcahsed_track
from telebirr.serializers import Purcahsed_track_serializer
from utilities.custom_pagination import CustomPagination



class PurchasedTracksViewset(ModelViewSet):
    

    serializer_class = Purcahsed_track_serializer
    queryset = Purcahsed_track.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            if user_id == "all_users":
                return Response(
                    Purcahsed_track.objects.values("userId").annotate(
                        total_amount_per_user=Sum("track_price_amount")
                    )
                )
            elif user_id == "total":
                return Response(
                    Purcahsed_track.objects.aggregate(
                        total_money_from_purchased_tracks=Sum("track_price_amount")
                    )
                )
            else:
                per_user = Purcahsed_track.objects.filter(userId=user_id).values(
                    "userId", "trackId", "track_price_amount", "created_at"
                )

                total_per_user = per_user.aggregate(
                    total_per_user=Sum("track_price_amount")
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
    

    def create(self, request, *args, **kwargs):
        verify_amount = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("payment_amount")[0]["payment_amount"]
        verify_userId = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("userId")[0]["userId"]
        verify_payment_state = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("payment_state")[0]["payment_state"]

        if verify_amount < int(request.data["track_price_amount"]):
            return Response(
                {
                    "message": "The price for this track cannot exceed the actual payment made ."
                }
            )
        elif verify_userId != request.data["userId"]:
            return Response({"message": "This content is not purcahsed by this user ."})
        elif verify_payment_state.upper() != "COMPLETED":
            return Response(
                {
                    "message": "The payment status is still pending , cannot be assigned ."
                }
            )
        else:
            serializer = Purcahsed_track_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
