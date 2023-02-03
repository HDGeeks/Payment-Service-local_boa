from django.urls import path
from rest_framework import routers
from .views import TelebirrGiftPaymentViewset, GiveGiftArtistViewset, BuyGiftViewSet, notify, dummy_dec

router = routers.DefaultRouter(trailing_slash=False)


router.register(r'give-gift', GiveGiftArtistViewset, basename='give-gift')
router.register(r'buy-gift-telebirr', TelebirrGiftPaymentViewset,
                basename='buy-gift-telebirr')
router.register(r'save-gift-payment-info', BuyGiftViewSet,
                basename='gift-payment-info'),


urlpatterns = [
    path("dumy-notify-url", dummy_dec, name="dummy-notify-url"),
    path("notify-url", notify, name="notify-url"),
    #path("gift-artist/", GiftArtistViewset.as_view(), name="gift-artist"),

]
urlpatterns += router.urls
