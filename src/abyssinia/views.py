from django.shortcuts import render
from .abyssinia import Abyssinia
import environ
from telebirr.views import generate_nonce
from datetime import datetime
from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view

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

                outtrade = generate_nonce(16)

                amount = request.data['payment_amount']
                pay = send_to_boa(amount)
            except Exception as e:
                return Response(str(e))
        return render(request, template_name="abyssinia/index.html")


def send_to_boa(amount):
    """
    {
    "transaction_type":"sale",
    "amount":"50",
    "currency":"USD"
    }
    """
    SIGNED_FIELD_NAMES = ["access_key",
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
        signed_field_names=str(SIGNED_FIELD_NAMES),
        unsigned_field_names=str(UNSIGNED_FIELD_NAMES),
        locale='en',
        signed_date_time=str(datetime.now()),
        transaction_type="transaction_type",
        amount=amount,
        currency="currency",


    )
    return boa.result()


@api_view(['GET', 'POST'])
def index(request):
    if request.method == "POST":
        nonce = generate_nonce(16)

        amount = request.POST['amount']
        pay = send_to_boa(amount)
        print(pay)

        # return render(request, template_name="abyssinia/confirm.html", context={'access_key': 'd3d82db024323d10992bef56d52c1f0b', 'profile_id': 'B97DA933-11BA-4758-945B-B012AAC266DF', 'transaction_uuid': 'Dc3pIWfhiB2VnozH', 'reference_number': 'b8P5VzvaijGq9JGa', 'signed_field_names': "['access_key', 'profile_id', 'transaction_uuid', 'signed_field_names', 'unsigned_field_names', 'signed_date_time', 'locale', 'transaction_type', 'reference_number', 'amount', 'currency']", 'unsigned_field_names': '[]', 'signed_date_time': '2023-02-06 08:02:41.609311', 'locale': 'en', 'transaction_type': 'transaction_type', 'amount': '1', 'currency': 'currency', 'signature': 'EAAB41826728BD456A70080D130501E7827331471737166E04C12CD553891AD9'})
        return render(request, template_name="abyssinia/confirm.html", context=pay)

    return render(request, template_name="abyssinia/index.html")


@api_view(['GET'])
def confirm(request):
    return render(request, template_name="abyssinia/confirm.html")
