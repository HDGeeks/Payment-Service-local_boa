import random
import string
import environ

from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rsa import PublicKey
import json

from telebirr.decrypt import Decrypt
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .models import Gift_Info, Gift_Payment_info
from .serializers import Gift_info_serializer, Gift_payment_serializer
from .telebirrApi import Telebirr
from .models import Gift_Payment_info
from django.shortcuts import get_object_or_404

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


@api_view(['GET', 'POST'])
@csrf_exempt
def notify(request):

    if request.method == 'POST':
        payload = request.body
        try:
            decrypted_data = Telebirr.decrypt(
                public_key=env("Public_Key"), payload=payload)
        except Exception as e:
            return Response(str(e))
        else:
            # get current amount using outtade
            current = Gift_Payment_info.objects.filter(
                outTradeNo=decrypted_data["outTradeNo"])
            # capture the existing amount
            if current.exists():
                current_amount = current.values("payment_amount")[
                    0]["payment_amount"]

                # perform addition of the current amount with total amount
                new_amount = current_amount + \
                    int(decrypted_data['totalAmount'])

                # update the row with new info
                update_data = Gift_Payment_info.objects.filter(
                    outTradeNo=decrypted_data["outTradeNo"]).update(msisdn=decrypted_data["msisdn"], tradeNo=decrypted_data["tradeNo"], transactionNo=decrypted_data["transactionNo"], payment_amount=new_amount, payment_state="completed")

                # fetch the row for display
                updated_data = Gift_Payment_info.objects.filter(
                    outTradeNo=decrypted_data["outTradeNo"]).values()

                # return Response({"Decrypted_Data": decrypted_data, "Updated_Data": updated_data})
                return Response({"code": 0, "msg": "success"})
            else:
                return Response("The outtrade number doesn't exist .")
    else:
        return Response(" only methods get and post allowed .")


@api_view(['GET', 'POST'])
@csrf_exempt
def dummy_dec(request):

    if request.method == 'POST' or request.method == 'GET':

        payload = request.body

        if payload != "":
            try:
                decrypted_data = Telebirr.decrypt(
                    public_key=env("Public_Key"), payload=payload)
            except Exception as e:
                return Response(str(e))
            else:
                return Response({"Decrypted_Data": decrypted_data, })

    return Response("post method only")


class BuyGiftViewSet(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def create(self, request, *args, **kwargs):
        if (request.data['payment_method'] != "telebirr"):
            if self.queryset.filter(userId=request.data['userId']).exists():
                return self.update(request)
            else:
                return super().create(request, *args, **kwargs)
        else:
            return Response("Telebirr payment method not allowed!")

    def update(self, request, *args, **kwargs):
        if (request.data['payment_method'] != "telebirr"):
            current_amount = Gift_Payment_info.objects.filter(
                userId=request.data['userId']).values("payment_amount")[0]["payment_amount"]

            new_amount = current_amount + int(request.data['payment_amount'])

            Gift_Payment_info.objects.filter(userId=request.data['userId']).update(
                payment_amount=new_amount)

            queryset = Gift_Payment_info.objects.filter(userId=request.data['userId']).values(
                "userId", "payment_amount", "payment_method")
            return Response(queryset, status=status.HTTP_200_OK)
        else:
            return Response("Telebirr payment method not allowed!")


class TelebirrGiftPaymentViewset(ModelViewSet):

    """
    This view make and external api call,
    to telebirr platform ,
    save the result and return
    the data generated as json object
    """
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def create(self, request, *args, **kwargs):
        if request.data['payment_method'] == "telebirr":
            try:
                if self.queryset.filter(userId=request.data['userId']).exists():
                    return self.update(request)

                nonce = ''
                outtrade = ''
                outtrade = generate_nonce(16)
                nonce = generate_nonce(16)

                amount = request.data['payment_amount']
                pay = send_to_telebirr(amount, nonce, outtrade)

                if pay['message'] == 'Operation successful':
                    current_amount = 0

                    content = {
                        "userId": request.data["userId"],
                        "payment_amount": current_amount,
                        "payment_method": request.data["payment_method"],
                        "outTradeNo": outtrade,  # "PZzTaKf4IW",
                        "msisdn": "",
                        "tradeNo": "",
                        "transactionNo": "",
                        "payment_state": request.data["payment_state"]
                    }

                    serializer = Gift_payment_serializer(data=content)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({"Telebirr_Response": pay, "Data": serializer.data})

                return Response({"message": pay['message'], 'status': status.HTTP_400_BAD_REQUEST, })

            except BaseException as e:
                return Response({'error message': str(e)})

        return Response({'msg': ' payment method is not telebirr'})

    def update(self, request, *args, **kwargs):
        if request.data['payment_method'] == "telebirr":
            try:
                nonce = ''
                outtrade = ''
                outtrade = generate_nonce(16)
                nonce = generate_nonce(16)
                amount = request.data['payment_amount']
                pay = send_to_telebirr(amount, nonce, outtrade)
                if pay['message'] == 'Operation successful':

                    update = Gift_Payment_info.objects.filter(
                        userId=request.data['userId']).update(outTradeNo=outtrade)
                    updated = Gift_Payment_info.objects.filter(
                        userId=request.data['userId']).values()
                    return Response({"Telebirr_Response": pay, "Data": updated})

                return Response({"message": pay['message'], 'status': status.HTTP_400_BAD_REQUEST, })

            except BaseException as e:
                return Response({'error message': str(e)})
        return Response({'msg': ' payment method is not telebirr'})


class GiveGiftArtistViewset(ModelViewSet):
    serializer_class = Gift_info_serializer
    queryset = Gift_Info.objects.all()

    def list(self, request, *args, **kwargs):
        artist = self.request.query_params.get('artist')
        if artist:
            queryset = Gift_Info.objects.filter(
                ArtistId=artist)
            queryset = queryset.values("ArtistId", "gift_amount")
            total_gift = sum(queryset.values_list('gift_amount', flat=True))
            result = {"ArtistId": artist, "total": total_gift}
            return Response(result)
        else:
            return Response(Gift_Info.objects.all().values("id", "ArtistId", "gift_amount"))

    def create(self, request, *args, **kwargs):

        current_amount = Gift_Payment_info.objects.filter(
            userId=request.data['userId']).values("payment_amount")[0]["payment_amount"]

        if int(request.data['gift_amount']) > current_amount:
            return Response({"message": " You dont xhave enough balance ."})

        new_amount = current_amount - int(request.data['gift_amount'])

        Gift_Payment_info.objects.filter(userId=request.data['userId']).update(
            payment_amount=new_amount)

        serializer = Gift_info_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_to_telebirr(amount, nonce, outtrade):
    # Initialise environment variables
    env = environ.Env()
    environ.Env.read_env()

    telebirr = Telebirr(

        app_id=env("App_ID"),
        app_key=env("App_Key"),
        public_key=env("Public_Key"),
        notify_url="https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/gift/notify-url",
        receive_name="Zema Multimedia PLC ",
        return_url="https://zemamultimedia.com",
        short_code=env("Short_Code"),
        subject="Media content",
        timeout_express="30",
        total_amount=amount,
        nonce=nonce,
        out_trade_no=outtrade,
    )

    return telebirr.send_request()


def decrypt_response_from_telebirr(message):
    responded_data = Decrypt(
        message=message)
    return responded_data


def generate_nonce(length):
    result_str = ''.join(random.choices(
        string.ascii_uppercase + string.digits + string.digits, k=length))
    return result_str
