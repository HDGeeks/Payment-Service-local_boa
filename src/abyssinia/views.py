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
        if request.data["payment_method"] == "BOA":
            try:
                outtrade = generate_nonce(16)

                amount = request.data["payment_amount"]
                pay = send_to_boa(amount)
            except Exception as e:
                return Response(str(e))
        return render(request, template_name="abyssinia/index.html")


def send_to_boa(amount):
    # SIGNED_FIELD_NAMES="access_key, profile_id, transaction_uuid, signed_field_names, unsigned_field_names, signed_date_time, locale, transaction_type, reference_number, amount, currency"
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
        "currency",
    ]

    UNSIGNED_FIELD_NAMES = []
    boa = Abyssinia(
        access_key=env("Aby_Access_Key"),
        profile_id=env("Aby_Profile_Id"),
        transaction_uuid=generate_nonce(16),
        reference_number=generate_nonce(16),
        signed_field_names=",".join(SIGNED_FIELD_NAMES),
        unsigned_field_names=" ",  #','.join(UNSIGNED_FIELD_NAMES),
        locale="en",
        signed_date_time=str(datetime.now()),
        transaction_type="sale",
        amount=amount,
        currency="ETB",
    )
    return boa.result()


@api_view(["GET", "POST"])
def index(request):
    if request.method == "POST":
        amount = request.POST["amount"]
        try:
            pay = send_to_boa(amount)
        except Exception as e:
            return Response(str(e))
        else:
            # return Response(pay)
            return render(request, template_name="abyssinia/confirm.html", context=pay)

    return render(request, template_name="abyssinia/index.html")


@api_view(["GET"])
def confirm(request):
    return render(request, template_name="abyssinia/confirm.html")
