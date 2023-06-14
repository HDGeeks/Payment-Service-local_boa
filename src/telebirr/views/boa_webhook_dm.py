from telebirr.models import BoaWebhook
from telebirr.serializers import Boa_Webhook_serializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class BoaWebhookForDMViewset(ModelViewSet):
    serializer_class = Boa_Webhook_serializer
    queryset = BoaWebhook.objects.all()

    def list(self, request, *args, **kwargs):
        return Response(
            self.queryset.filter(data__reason_code="481")
            .values()
            .order_by("-created_at"),
            status=status.HTTP_200_OK,
        )
