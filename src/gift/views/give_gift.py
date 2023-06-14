from gift.models import Coin, Gift_Info
from gift.serializers import Gift_info_serializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum
from utilities.identity import get_identity
from rest_framework import status


class GiveGiftArtistViewset(ModelViewSet):
    serializer_class = Gift_info_serializer
    queryset = Gift_Info.objects.all()

    def list(self, request, *args, **kwargs):
        artist = self.request.query_params.get("artist")
        if artist:
            if artist == "all":
                return Response(
                    Gift_Info.objects.values("ArtistId")
                    .annotate(total_gift_collected=Sum("gift_amount"))
                    .order_by("-total_gift_collected")[:10]
                )
            queryset = Gift_Info.objects.filter(ArtistId=artist)
            queryset = queryset.values("userId", "gift_amount")
            res = []
            for gift in queryset:
                temp = {}
                temp["userId"] = get_identity(gift["userId"])
                temp["amount"] = gift["gift_amount"]
                res.append(temp)

            total_gift = sum(queryset.values_list("gift_amount", flat=True))
            result = {"ArtistId": artist, "total": total_gift, "tippers": res}
            return Response(result)
        else:
            return Response(
                Gift_Info.objects.all().values(
                    "id", "userId", "ArtistId", "gift_amount"
                )
            )

    def create(self, request, *args, **kwargs):
        # find the coin available per user
        current_coin_amount = Coin.objects.filter(userId=request.data["userId"]).values(
            "total_coin"
        )[0]["total_coin"]

        # validate if the user have enough balance
        if int(request.data["gift_amount"]) > current_coin_amount:
            return Response({"message": " You dont have enough gift coin balance ."})

        # subtract the amount to gift from the existing coin amount
        new_deducted_coin_amount = current_coin_amount - int(
            request.data["gift_amount"]
        )

        # update the coin model with new deducted amount
        Coin.objects.filter(userId=request.data["userId"]).update(
            total_coin=new_deducted_coin_amount
        )
        # return response to front end
        serializer = Gift_info_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
