import environ
from dateutil.relativedelta import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from rest_framework.viewsets import ModelViewSet

from gift.pagination import MyPagination
from subscription.models import Subscription_Payment_info
from subscription.serializers import Subscription_payment_serializer
from utilities.identity import get_identity

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class SubsPaymentAnalyticViewset(ModelViewSet):
    queryset = Subscription_Payment_info.objects.all()
    serializer_class = Subscription_payment_serializer
    http_method_names = ["get", "head"]
    pagination_class = MyPagination

    def list(self, request, *args, **kwargs):
        # The response object
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
        if not user:
            subscriptions = Subscription_Payment_info.objects.all().order_by(
                "-created_at"
            )
        else:
            subscriptions = Subscription_Payment_info.objects.filter(
                userId=user
            ).order_by("-created_at")

        # get unique users
        user_id_set = set()
        for subscription in subscriptions:
            user_id_set.add(subscription.user_id)

        distinct_user_count = len(user_id_set)

        # if filter query exists , filter
        if filter_query:
            subscriptions = subscriptions.filter(filter_query)

        # apply pagination
        subscriptions = self.paginate_queryset(subscriptions)
        paginated_user_ids = self.paginate_queryset(list(user_id_set))

        # Build response
        # response["count"] = subscriptions.values("user_id").distinct().count()
        response["count"] = distinct_user_count
        response["result"] = []

        for user in paginated_user_ids:
            # get data from haile
            user_identity = get_identity(user)
            # Per user
            per_user = (
                Subscription_Payment_info.objects.filter(userId=user)
                .order_by("created_at")
                .values("userId", "payment_amount", "payment_method", "created_at")
            )
            # total per user
            total_per_user = per_user.aggregate(total_per_user=Sum("payment_amount"))
            # final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key] = value

            final_result_dictionary["per_user"] = per_user
            for key, value in total_per_user.items():
                final_result_dictionary[key] = value

            # append results to result
            response["result"].append(final_result_dictionary)
        # the final response
        return self.get_paginated_response(response)
