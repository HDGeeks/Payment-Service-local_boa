from django.urls import path
from rest_framework import routers
from .views import (
    TelebirrGiftPaymentViewset,
    GiveGiftArtistViewset,
    BuyGiftViewSet,
    notify,
    dummy_dec,
    CoinViewset,
    GiftRevenuViewset,
    GiftAnalyticViewset
)

router = routers.DefaultRouter(trailing_slash=False)


router.register(r"give-gift", GiveGiftArtistViewset, basename="give-gift")
router.register(
    r"buy-gift-telebirr", TelebirrGiftPaymentViewset, basename="buy-gift-telebirr"
)
router.register(
    r"save-gift-payment-info", BuyGiftViewSet, basename="gift-payment-info"
),
router.register(r"coin-info", CoinViewset, basename="coin-info")
router.register(r"gift-analytics" , GiftAnalyticViewset ,basename="gift-payment-analysis")
router.register(
    r"set-revenue-from-gift", GiftRevenuViewset, basename="set-revenue-from-gift"
)


urlpatterns = [
    path("dumy-notify-url", dummy_dec, name="dummy-notify-url"),
    path("notify-url", notify, name="notify-url"),
    # path("gift-artist/", GiftArtistViewset.as_view(), name="gift-artist"),
]
urlpatterns += router.urls
