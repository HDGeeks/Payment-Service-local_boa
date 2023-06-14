from telebirr.models import BoaWebhook
from telebirr.serializers import Boa_Webhook_serializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from django.shortcuts import redirect


class BoaWebhookViewset(ModelViewSet):
    serializer_class = Boa_Webhook_serializer
    queryset = BoaWebhook.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.query_params.get("user")
        if user:
            try:
                result = (
                    BoaWebhook.objects.filter(data__req_reference_number=user)
                    .values("id", "data__req_amount", "data__req_reference_number")
                    .latest("created_at")
                )
            except BoaWebhook.DoesNotExist:
                raise NotFound("Record does not exist for this user .")

            return Response(result, status=status.HTTP_200_OK)

        return Response(self.queryset.values(), status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        payload = {"data": request.data}
        serializer = Boa_Webhook_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if request.data["decision"] == "DECLINE" or request.data["decision"] == "ERROR":
            return redirect(
                "https://zemastroragev100.blob.core.windows.net/boa/failedpage.html"
            )

        elif request.data["reason_code"] == "481":
            return redirect(
                "https://zemastroragev100.blob.core.windows.net/boa/success_but_flagged.html"
            )

        elif (
            request.data["reason_code"] == "100"
            and request.data["decision"] == "ACCEPT"
        ):
            return redirect(
                "https://zemastroragev100.blob.core.windows.net/boa/successpage.html"
            )
        else:
            return Response(
                "Transaction failed . Contact support .",
                status=status.HTTP_400_BAD_REQUEST,
            )
