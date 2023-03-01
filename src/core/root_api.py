from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib import admin


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "payment-purchase-with-telebirr-list": reverse(
                "purchase-with-telebirr-list", request=request, format=format
            ),
            "payment-with-boa": reverse(
                "purchase-with-boa-list", request=request, format=format
            ),
            "payment-info-list": reverse(
                "payment-info-list", request=request, format=format
            ),
            "payment-purchased-tracks-list": reverse(
                "purchased-tracks-list", request=request, format=format
            ),
            "payment-purchased-albums-list": reverse(
                "purchased-albums-list", request=request, format=format
            ),
            "payment-notify-url": reverse(
                "payment-notify-url", request=request, format=format
            ),
            # gift
            "gift-buy-telebirr-list": reverse(
                "buy-gift-telebirr-list", request=request, format=format
            ),
            "gift-payment-info-list": reverse(
                "gift-payment-info-list", request=request, format=format
            ),
            "gift-give-gift-list": reverse(
                "give-gift-list", request=request, format=format
            ),
            "coin-info-list": reverse("coin-info-list", request=request, format=format),
            "gift-notify": reverse("notify-url", request=request, format=format),
            "gift-dummy-notify-test": reverse(
                "dummy-notify-url", request=request, format=format
            ),
            # subscribe
            "subscribe-list": reverse("subscribe-list", request=request, format=format),
            "subscribe-payment-list": reverse(
                "pay_to_subscribe-list", request=request, format=format
            ),
            "subscribe-with-telebirr": reverse(
                "subscribe_with_telebirr-list", request=request, format=format
            ),
            "subscribe-notify-url": reverse(
                "subscribe-notify-url", request=request, format=format
            ),
            "subscribed-users-count": reverse(
                "subscribed-users-count", request=request, format=format
            ),
            "schema-json": reverse("schema-json", request=request, format=format),
            # superapp
            "pay-with-super-app": reverse(
                "pay-with-super-app-list", request=request, format=format
            ),
            "check-superapp-payment": reverse(
                "check-superapp-payment-list", request=request, format=format
            ),
        }
    )
