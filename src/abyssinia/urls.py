from rest_framework import routers
from .views import PurchaseWithBOAViewset , index,confirm
from django.urls import path


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'purchase-with-boa',
                PurchaseWithBOAViewset, basename='purchase-with-boa')

urlpatterns = [
    path("index",index, name="index"),
    path("confirm", confirm, name="confirm"),
    
]

urlpatterns += router.urls
