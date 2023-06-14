import environ
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from stripe import Subscription

from subscription.serializers import subscriptionSerializer
from utilities.identity import get_identity
from utilities.subs_pagination import SubscriptionPagination
from subscription.models import Subscription

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class SubscribersAnalyticsViewset(ModelViewSet):
    serializer_class = subscriptionSerializer
    queryset = Subscription.objects.all()
    http_method_names = ["get", "head"]
    pagination_class = SubscriptionPagination

    def list(self, request, *args, **kwargs):
        # The response object
        response = {}

        # Get query parameters and set default values
        payment_method = self.request.query_params.get("payment_method", None)
        user = self.request.query_params.get("user", None)

        # Get all subscriptions
        subscriptions = Subscription.objects.all().order_by("-created_at")
        if user:
            subscriptions = subscriptions.filter(user_id=user).order_by("-created_at")

        # Get unique user IDs
        user_id_set = set(subscriptions.values_list("user_id", flat=True))
        distinct_user_count = len(user_id_set)

        # Build response
        response["count"] = distinct_user_count
        response["result"] = []

        for user_id in self.paginate_queryset(list(user_id_set)):
            # Get user identity
            user_identity = get_identity(user_id)

            # Get subscriptions for the user
            per_user = Subscription.objects.filter(user_id=user_id).order_by(
                "-created_at"
            )

            # Apply filter query if it exists
            filter_query = Q()
            if payment_method:
                if payment_method == "telebirr":
                    filter_query |= Q(payment_id__payment_method="telebirr")
                elif payment_method == "Abysinia":
                    filter_query |= Q(payment_id__payment_method="Abysinia")
                elif payment_method == "telebirr_superApp":
                    filter_query |= Q(
                        payment_id_from_superapp__payment_method="telebirr_superApp"
                    )
            per_user = per_user.filter(filter_query)

            # Get total subscriptions for the user
            total_per_user = per_user.count()

            # Build final result dictionary
            final_result_dictionary = {}
            for key, value in user_identity.items():
                final_result_dictionary[key] = value
            final_result_dictionary["per_user"] = per_user.values(
                "id",
                "user_id",
                "sub_type",
                "subscription_date",
                "paid_until",
                "payment_id__payment_method",
                "payment_id_from_superapp__payment_method",
                "created_at",
            ).order_by("-created_at")
            final_result_dictionary["total_per_user"] = total_per_user

            # Append result to response
            response["result"].append(final_result_dictionary)

        # Return paginated response
        return self.get_paginated_response(response)
