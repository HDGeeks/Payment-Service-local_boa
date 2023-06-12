from .views import (
    SubscribersAnalytics,
    SubscriptionViewset,
    PaymentViewset,
    notify,
    SubscribeWithTelebirrViewSet,
    SubscriptionFeeViewset,
    SubsAnalyticViewset,
    subscribers_count,
    SearchSubsrcriptionViewset
)
from rest_framework import routers
from django.urls import path


router = routers.DefaultRouter(trailing_slash=False)
router.register(r"subscribe", SubscriptionViewset, basename="subscribe")
router.register(
    r"subscription-fee", SubscriptionFeeViewset, basename="subscription-fee"
)
router.register(r"pay_to_subscribe", PaymentViewset, basename="pay_to_subscribe")

router.register(
    r"subs-payment-analytics", SubsAnalyticViewset, basename="subs-payment-analytics"
)
router.register(
    r"subscription-analytics", SubscribersAnalytics, basename="subscription-analytics"
)
router.register(
    r"search",SearchSubsrcriptionViewset
, basename="search"
)
router.register(
    r"subscribe_with_telebirr",
    SubscribeWithTelebirrViewSet,
    basename="subscribe_with_telebirr",
)


urlpatterns = [
    path("subscribe-notify-url", notify, name="subscribe-notify-url"),
    path("subscribed-users-count", subscribers_count, name="subscribed-users-count"),
]

urlpatterns += router.urls
