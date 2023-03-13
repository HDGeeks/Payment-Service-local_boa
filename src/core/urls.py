from xml.dom.minidom import Document
from django.contrib import admin
from django.urls import path, include, re_path
from django.urls import re_path as url


from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static


from .root_api import api_root

# api documentation
from drf_yasg.views import get_schema_view
from rest_framework import permissions


###############################################
###############################################
###############################################
# Test Code Start
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import DefaultRouter
from gift.models import *
from gift.serializers import *


class TestViewSet(ModelViewSet):
    queryset = Gift_Payment_info.objects.all()
    serializer_class = Gift_payment_serializer

    def create(self, request, *args, **kwargs):
        return Response("Working")

    def update(self, request, *args, **kwargs):
        return Response("Working")

    def retrieve(self, request, *args, **kwargs):
        return Response("Working")

    def destroy(self, request, *args, **kwargs):
        return Response("Working")

    def list(self, request, *args, **kwargs):
        return Response("Still Working")


router = DefaultRouter(trailing_slash=False)

router.register(r"", TestViewSet, basename="")

# Test Code END
###############################################
###############################################
###############################################


schema_view = get_schema_view(
    # API schema for our accounts
    openapi.Info(
        title="PAYMENT API",
        default_version="v1",
        description="payment API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="dannyhd88@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("root/", api_root, name="root"),
    path("payment/", include("telebirr.urls")),
    path("gift/", include("gift.urls")),
    path("super/", include("super_app.urls")),
    path("tests/", include(router.urls)),
    # path("paypal/", include("paypal.urls")),
    path("subscription/", include("subscription.urls")),
    #path("boa/", include("abyssinia.urls")),
    # API documentation urls
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("openapi.yml", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    # Report Builde
    re_path(r"^report_builder/", include("report_builder.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
