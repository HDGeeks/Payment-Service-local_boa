from django.urls import path, re_path
from rest_framework import routers
from .views import SuperappPayViewSet, CheckPaymentViewSet, notify


router = routers.DefaultRouter(trailing_slash=False)

router.register(r'pay-with-super-app', SuperappPayViewSet,
                basename='pay-with-super-app')
router.register(r'check-superapp-payment', CheckPaymentViewSet,
                basename='check-superapp-payment')


urlpatterns = [
    path("super-app-notify-url", notify, name="super-app-notify-url")
]

urlpatterns += router.urls
#
