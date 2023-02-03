from django.shortcuts import render
from .abyssinia import Abyssinia
import environ
from telebirr.views import generate_nonce
from datetime import datetime
from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

# Create your views here.
# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))

class PurchaseWithBOAViewset(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer

    def create(self, request, *args, **kwargs):

        if request.data['payment_method'] == "BOA":
            try:

                nonce = ''
                outtrade = ''
                outtrade = generate_nonce(16)
                print(outtrade)
                nonce = generate_nonce(16)

                amount = request.data['payment_amount']
                pay = send_to_boa(amount)
            except Exception as e:
                return Response(str(e))
        return Response(pay)


def send_to_boa(amount):
    """
    {
    "transaction_type":"sale",
    "amount":"50",
    "currency":"USD"
    }
    """
    SIGNED_FIELD_NAMES = [
        "access_key",
        "profile_id",
        "transaction_uuid",
        "signed_field_names",
        "unsigned_field_names",
        "signed_date_time",
        "locale",
        "transaction_type",
        "reference_number",
        "amount",
        "currency"
    ]
    UNSIGNED_FIELD_NAMES = []
    boa = Abyssinia(
        access_key=env("Aby_Access_Key"),
        profile_id=env("Aby_Profile_Id"),
        transaction_uuid=generate_nonce(16),
        reference_number=generate_nonce(16),
        # const reference_number='E-5AFEF65238874EA0936EB3F3C2673A59'
        signed_field_names=str(SIGNED_FIELD_NAMES),
        unsigned_field_names=str(UNSIGNED_FIELD_NAMES),
        locale='en',
        signed_date_time=str(datetime.now()),
        transaction_type="transaction_type",
        amount=amount,
        currency="currency",


    )
    return boa.send_request()
