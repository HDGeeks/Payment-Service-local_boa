import environ
from rest_framework import status

from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer


# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class SavePurchasePaymentViewSet(ModelViewSet):
    """
    This view make and external api call,
    to telebirr platform ,
    save the result and return
    the data generated as json object
    """

    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            return Response("telebirr payment is not saved using this api .")
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # this is haile code

        user = self.request.query_params.get("user")
        if user:
            try:
                user_obj = Payment_info.objects.filter(userId=user).values(
                    "id", "userId", "payment_amount"
                )
            except Payment_info.DoesNotExist:
                raise NotFound("Record does not exist for this user .")

            return Response(user_obj, status=status.HTTP_200_OK)

        return Response(self.queryset.values(), status=status.HTTP_200_OK)
