import environ

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer

from utilities.generate_nonce import generate_nonce
from utilities.send_to_telebirr import send_to_telebirr

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class PurchaseWithTelebirrViewSet(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            try:
                nonce = ""
                outtrade = ""
                outtrade = generate_nonce(16)
                nonce = generate_nonce(16)
                notify_type = "purchase"

                amount = request.data["payment_amount"]
                pay = send_to_telebirr(amount, nonce, outtrade, notify_type)
                if pay["message"] == "Operation successful":
                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": request.data["payment_amount"],
                        "payment_method": request.data["payment_method"],
                        "outTradeNo": outtrade,
                        "msisdn": "",
                        "tradeNo": "",
                        "transactionNo": "",
                        "payment_state": request.data["payment_state"],
                    }
                    serializer = Payment_info_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({"pay": pay, "data": serializer.data})

                return Response(
                    {
                        "message": pay["message"],
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )

            except BaseException as e:
                return Response({"error message": str(e)})

        else:
            return Response(
                {
                    "msg": " payment method is not telebirr",
                    "status": "status.HTTP_400_BAD_REQUEST",
                }
            )
