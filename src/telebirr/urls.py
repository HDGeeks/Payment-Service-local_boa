from django.urls import path, re_path
from rest_framework import routers
from .views import (
    PurchaseWithTelebirrViewSet,
    PurchasedTracksViewset,
    PurchasedAlbumsViewset,
    PurchsedTrackAnalytics,
    SavePurchasePaymentViewSet,
    TrackRevenueViewset,
    PurchaseAnalyticViewset,
    notify,
)


router = routers.DefaultRouter(trailing_slash=False)
router.register(
    r"purchased-tracks", PurchasedTracksViewset, basename="purchased-tracks"
)
router.register(
    r"purchased-albums", PurchasedAlbumsViewset, basename="purchased-albums"
)
router.register(
    r"save-payment-info", SavePurchasePaymentViewSet, basename="payment-info"
)
router.register(
    r"purchase-with-telebirr",
    PurchaseWithTelebirrViewSet,
    basename="purchase-with-telebirr",
)
router.register(
    r"purchase-analytics", PurchaseAnalyticViewset, basename="purchase-analytics"
)
router.register(
    r"purchased-tracks-analytics",
    PurchsedTrackAnalytics,
    basename="purchased-tracks-analytics",
)
router.register(
    r"set-track-revenue-rate", TrackRevenueViewset, basename="set-track-revenue-rate"
)


urlpatterns = [
    # path("find-user/", findUser, name="find-user"),
    path("payment-notify-url", notify, name="payment-notify-url")
]

urlpatterns += router.urls
