from django.urls import path
from rest_framework import routers

from gift.views.gift_payment_info import BuyGiftViewSet
from gift.views.buy_gift_with_telebirr import TelebirrGiftPaymentViewset
from gift.views.give_gift import GiveGiftArtistViewset
from gift.views.coin import CoinViewset
from gift.views.set_gift_revenue import GiftRevenuViewset
from gift.views.gift_notify_callback_url import notify
from gift.views.analytics_gift_payment import GiftAnalyticViewset
from gift.views.dummy_dec import dummy_dec

router = routers.DefaultRouter(trailing_slash=False)


router.register(r"give-gift", GiveGiftArtistViewset, basename="give-gift")
router.register(
    r"buy-gift-telebirr", TelebirrGiftPaymentViewset, basename="buy-gift-telebirr"
)
router.register(
    r"save-gift-payment-info", BuyGiftViewSet, basename="gift-payment-info"
),
router.register(
    r"gift-analytics", GiftAnalyticViewset, basename="gift-payment-analysis"
)
router.register(r"coin-info", CoinViewset, basename="coin-info")
router.register(
    r"set-revenue-from-gift", GiftRevenuViewset, basename="set-revenue-from-gift"
)


urlpatterns = [
    path("dumy-notify-url", dummy_dec, name="dummy-notify-url"),
    path("notify-url", notify, name="notify-url"),
    # path("gift-artist/", GiftArtistViewset.as_view(), name="gift-artist"),
]
urlpatterns += router.urls
