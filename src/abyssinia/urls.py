from rest_framework import routers
from .views import PurchaseWithBOAViewset


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'purchase-with-boa',
                PurchaseWithBOAViewset, basename='purchase-with-boa')

urlpatterns = [

    
]

urlpatterns += router.urls
