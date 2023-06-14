from django.urls import path
from rest_framework import routers

from subscription.views.analytics_on_subscribers import SubscribersAnalyticsViewset
from subscription.views.analytics_subs_payment_info import SubsPaymentAnalyticViewset
from subscription.views.pay_with_telebirr import PayWithTelebirrToSubscribeViewSet
from subscription.views.payment_info import PaymentViewset
from subscription.views.subs_notify_callback_url import notify
from subscription.views.subscribe import SubscriptionViewset
from subscription.views.subscribers_count import subscribers_count
from subscription.views.subscription_fee import SubscriptionFeeViewset

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"subscribe", SubscriptionViewset, basename="subscribe")
router.register(r"pay_to_subscribe", PaymentViewset, basename="pay_to_subscribe")
router.register(
    r"subs-payment-analytics",
    SubsPaymentAnalyticViewset,
    basename="subs-payment-analytics",
)
router.register(
    r"subscription-analytics",
    SubscribersAnalyticsViewset,
    basename="subscription-analytics",
)
router.register(
    r"subscribe_with_telebirr",
    PayWithTelebirrToSubscribeViewSet,
    basename="subscribe_with_telebirr",
)
router.register(
    r"subscription-fee", SubscriptionFeeViewset, basename="subscription-fee"
)


urlpatterns = [
    path("subscribe-notify-url", notify, name="subscribe-notify-url"),
    path("subscribed-users-count", subscribers_count, name="subscribed-users-count"),
]

urlpatterns += router.urls
