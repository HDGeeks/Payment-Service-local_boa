from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "payment-purchase-with-telebirr-list": reverse(
                "purchase-with-telebirr-list", request=request, format=format
            ),
            "payment-info-list": reverse(
                "payment-info-list", request=request, format=format
            ),
            "purchase-analytics": reverse(
                "purchase-analytics-list", request=request, format=format
            ),
            "purchased-tracks-analytics": reverse(
                "purchased-tracks-analytics-list", request=request, format=format
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
            "set-track-revenue-rate": reverse(
                "set-track-revenue-rate-list", request=request, format=format
            ),
            "boa-webhook": reverse("boa-webhook-list", request=request, format=format),
            "boa-webhook-for-dm": reverse(
                "boa-webhook-for-dm-list", request=request, format=format
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
            "gift-payment-analysis": reverse(
                "gift-payment-analysis-list", request=request, format=format
            ),
            "gift-notify": reverse("notify-url", request=request, format=format),
            "gift-dummy-notify-test": reverse(
                "dummy-notify-url", request=request, format=format
            ),
            "coin-info-list": reverse("coin-info-list", request=request, format=format),
            "set-revenue-from-gift-list": reverse(
                "set-revenue-from-gift-list", request=request, format=format
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
            "subs-payment-analytics": reverse(
                "subs-payment-analytics-list", request=request, format=format
            ),
            "subscription-analytics": reverse(
                "subscription-analytics-list", request=request, format=format
            ),
            "subscription-fee-list": reverse(
                "subscription-fee-list", request=request, format=format
            ),
            "schema-json": reverse("schema-json", request=request, format=format),
            # superapp
            "pay-with-super-app": reverse(
                "pay-with-super-app-list", request=request, format=format
            ),
            "check-superapp-payment": reverse(
                "check-superapp-payment-list", request=request, format=format
            ),
            "superapp_notify-url": reverse(
                "super-app-notify-url", request=request, format=format
            ),
            # docs
            "admin-site": reverse("admin:login", request=request, format=format),
            # doc
            "swagger-api-doc": reverse(
                "schema-swagger-ui", request=request, format=format
            ),
            "redoc-api-doc": reverse("schema-redoc", request=request, format=format),
        }
    )
