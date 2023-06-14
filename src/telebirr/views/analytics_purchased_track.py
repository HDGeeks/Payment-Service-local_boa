import environ
from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from gift.pagination import MyPagination
from telebirr.models import Purcahsed_track
from telebirr.serializers import Purcahsed_track_serializer
from utilities.identity import get_identity

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class PurchsedTrackAnalytics(ModelViewSet):
    serializer_class = Purcahsed_track_serializer
    queryset = Purcahsed_track.objects.all()
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
        if not user:
            track_analytics = Purcahsed_track.objects.all()
        else:
            track_analytics = Purcahsed_track.objects.filter(userId=user)

        # get unique users
        user_id_set = set()
        for user in track_analytics:
            user_id_set.add(user.userId)

        distinct_user_count = len(user_id_set)

        # if filter query exists , filter
        if filter_query:
            track_analytics = track_analytics.filter(filter_query)

        # apply pagination
        track_analytics = self.paginate_queryset(track_analytics)
        paginated_user_ids = self.paginate_queryset(list(user_id_set))

        # Build response
        response["count"] = distinct_user_count
        response["result"] = []

        for user in paginated_user_ids:
            # get data from haile
            user_identity = get_identity(user)

            # Per user
            per_user = (
                Purcahsed_track.objects.filter(userId=user)
                .order_by("created_at")
                .values(
                    "id",
                    "userId",
                    "trackId",
                    "track_price_amount",
                    "payment_id",
                    "created_at",
                )
            )

            # total per user
            total_per_user = per_user.aggregate(
                total_per_user=Sum("track_price_amount")
            )

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

        # the final response
        return self.get_paginated_response(response)
