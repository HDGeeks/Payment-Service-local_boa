from django.urls import path, re_path
from rest_framework import routers
from .views import SuperappPayViewSet, CheckPaymentViewSet, notify


router = routers.DefaultRouter(trailing_slash=False)

router.register(r'SubscribeWithTelebirr', SuperappPayViewSet,
                basename='SubscribeWithTelebirr')
router.register(r'CheckPayment', CheckPaymentViewSet, basename='CheckPayment')


urlpatterns = [

    #path("find-user/", findUser, name="find-user"),
    # path("subscription/", include("router.urls"))
    path("super-app-notify-url", notify, name="super-app-notify-url")
]

urlpatterns += router.urls
#
