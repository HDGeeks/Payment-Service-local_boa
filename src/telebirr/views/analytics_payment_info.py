import json

import environ
from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from gift.pagination import MyPagination
from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer
from utilities.identity import get_identity


class PurchaseAnalyticViewset(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer
    http_method_names = ["get", "head"]
    pagination_class = MyPagination

    def list(self, request, *args, **kwargs):
        # response dict
        response = {}

        # Get query parameters and set default values
        payment_method = self.request.query_params.get("payment_method", None)
        user = self.request.query_params.get("user", None)

        # The multiple queries using Q
        filter_query = Q()
        if payment_method:
            # Build filter query based on query parameters
            # filter_query = Q()
            if payment_method == "telebirr":
                filter_query |= Q(payment_id__payment_method="telebirr")
            elif payment_method == "Abysinia":
                filter_query |= Q(payment_id__payment_method="Abysinia")
            elif payment_method == "telebirr_superApp":
                filter_query |= Q(
                    payment_id_from_superapp__payment_method="telebirr_superApp"
                )
            else:
                pass

        # Filter using user if it exists
        payment_analytics = Payment_info.objects.all()

        if user:
            payment_analytics = Payment_info.objects.filter(userId=user)

        # get unique users
        user_id_set = set()
        for user in payment_analytics:
            user_id_set.add(user.userId)

        distinct_user_count = len(user_id_set)

        # if filter query exists , filter
        if filter_query:
            payment_analytics = payment_analytics.filter(filter_query)

        # apply pagination
        payment_analytics = self.paginate_queryset(payment_analytics)
        paginated_user_ids = self.paginate_queryset(list(user_id_set))

        # Build response
        response["count"] = distinct_user_count
        response["result"] = []

        for user in paginated_user_ids:
            # get data from haile
            user_identity = get_identity(user)

            # Per user
            per_user = (
                Payment_info.objects.filter(userId=user)
                .order_by("created_at")
                .values("userId", "payment_amount", "payment_method", "created_at")
            )

            # total per user
            total_per_user = per_user.aggregate(total_per_user=Sum("payment_amount"))

            # final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key] = value

            # final_result_dictionary["user_identity"] = user_identity
            final_result_dictionary["per_user"] = per_user
            # new change
            for key, value in total_per_user.items():
                final_result_dictionary[key] = value
            # append results to result
            response["result"].append(final_result_dictionary)

        return Response(response)
