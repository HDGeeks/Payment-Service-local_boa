import environ
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utilities.generate_nonce import generate_nonce
from utilities.send_to_telebirr import send_to_telebirr

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


from gift.models import Gift_Payment_info
from gift.serializers import Gift_payment_serializer


class TelebirrGiftPaymentViewset(ModelViewSet):

    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def create(self, request, *args, **kwargs):
        if request.data["payment_method"] == "telebirr":
            try:
                # if self.queryset.filter(userId=request.data['userId']).exists():
                #     return self.update(request)

                nonce = ""
                outtrade = ""
                outtrade = generate_nonce(16)
                nonce = generate_nonce(16)
                notify_type = "gift"

                amount = request.data["payment_amount"]
                pay = send_to_telebirr(amount, nonce, outtrade, notify_type)

                if pay["message"] == "Operation successful":
                    current_amount = 0

                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": current_amount,
                        "payment_method": request.data["payment_method"],
                        "outTradeNo": outtrade,  # "PZzTaKf4IW",
                        "msisdn": "",
                        "tradeNo": "",
                        "transactionNo": "",
                        "payment_state": request.data["payment_state"],
                    }

                    serializer = Gift_payment_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(
                            {"Telebirr_Response": pay, "Data": serializer.data}
                        )

                return Response(
                    {
                        "message": pay["message"],
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )

            except BaseException as e:
                return Response({"error message": str(e)})

        return Response({"msg": " payment method is not telebirr"})
