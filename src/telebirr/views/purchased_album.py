import environ


from rest_framework import status

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from telebirr.models import Purcahsed_album, Payment_info
from telebirr.serializers import Purcahsed_album_serializer


# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class PurchasedAlbumsViewset(ModelViewSet):
    """
    check the request data ,
    check the notify url and its results ,
    update the subscription model is subscribed field true

    """

    serializer_class = Purcahsed_album_serializer
    queryset = Purcahsed_album.objects.all()

    def create(self, request, *args, **kwargs):
        verify_amount = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("payment_amount")[0]["payment_amount"]
        verify_payment_state = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("payment_state")[0]["payment_state"]
        verify_userId = Payment_info.objects.filter(
            id=request.data["payment_id"]
        ).values("userId")[0]["userId"]
        if verify_amount < int(request.data["album_price_amount"]):
            return Response(
                {
                    "message": "The price for this album cannot exceed the actual payment made ."
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
            serializer = Purcahsed_album_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
