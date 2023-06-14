from django.urls import path
from rest_framework import routers


from telebirr.views.save_payment import SavePurchasePaymentViewSet
from telebirr.views.pay_with_telebirr import PurchaseWithTelebirrViewSet
from telebirr.views.purchased_album import PurchasedAlbumsViewset
from telebirr.views.purchased_track import PurchasedTracksViewset
from telebirr.views.analytics_payment_info import PurchaseAnalyticViewset
from telebirr.views.analytics_purchased_track import PurchsedTrackAnalytics
from telebirr.views.notify_callback_url import notify
from telebirr.views.set_track_price import TrackRevenueViewset
from telebirr.views.boa_webhook import BoaWebhookViewset
from telebirr.views.boa_webhook_dm import BoaWebhookForDMViewset

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
    r"purchase-analytics", PurchaseAnalyticViewset, basename="purchase-analytics"
)
router.register(
    r"purchased-tracks-analytics",
    PurchsedTrackAnalytics,
    basename="purchased-tracks-analytics",
)
router.register(
    r"purchase-with-telebirr",
    PurchaseWithTelebirrViewSet,
    basename="purchase-with-telebirr",
)
router.register(
    r"set-track-revenue-rate", TrackRevenueViewset, basename="set-track-revenue-rate"
)
router.register(r"boa-webhook", BoaWebhookViewset, basename="boa-webhook")
router.register(
    r"boa-webhook-for-dm", BoaWebhookForDMViewset, basename="boa-webhook-for-dm"
)


urlpatterns = [
    # path("find-user/", findUser, name="find-user"),
    path("payment-notify-url", notify, name="payment-notify-url")
]

urlpatterns += router.urls
