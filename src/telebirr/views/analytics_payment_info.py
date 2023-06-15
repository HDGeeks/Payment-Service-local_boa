from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utilities.subs_pagination import SubscriptionPagination
from telebirr.models import Payment_info
from telebirr.serializers import Payment_info_serializer
from utilities.identity import get_identity


class PurchaseAnalyticViewset(ModelViewSet):
    queryset = Payment_info.objects.all()
    serializer_class = Payment_info_serializer
    http_method_names = ["get", "head"]
    pagination_class = SubscriptionPagination

    def list(self, request, *args, **kwargs):
        # response dict
        response = {}

        # Get query parameters and set default values
        payment_method = self.request.query_params.get("payment_method", None)
        user = self.request.query_params.get("user", None)

         # Filter using user if it exists
        queryset = self.queryset

        if user:
            queryset = queryset.filter(userId=user)

         # Handle empty queryset
        if not queryset.exists():
            return self.get_paginated_response({"count": 0, "result": []})

        # The multiple queries using Q
        filter_query = Q()
        if payment_method:
            # Build filter query based on query parameters
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

       

        
       
        
        # for postgre
        # Get a list of unique user ids
        user_ids = queryset.distinct("userId").values_list("userId", flat=True)

        # get unique users
        user_id_set = set()
        for user in queryset:
            user_id_set.add(user.userId)

        distinct_user_count = len(user_id_set)

        # if filter query exists , filter
        # if filter_query:
        #     payment_analytics = payment_analytics.filter(filter_query)

        # apply pagination
        paginated_queryset = self.paginate_queryset(queryset)
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

        return self.get_paginated_response(response)






# class PurchaseAnalyticViewset(ModelViewSet):
#     queryset = Payment_info.objects.all()
#     serializer_class = Payment_info_serializer
#     http_method_names = ["get", "head"]
#     pagination_class = SubscriptionPagination

#     def list(self, request, *args, **kwargs):
#         # Get query parameters and set default values
#         payment_method = self.request.query_params.get("payment_method", None)
#         user = self.request.query_params.get("user", None)

#         # Build filter query based on query parameters
#         filter_query = Q()
#         if payment_method:
#             filter_query = Q(payment_method=payment_method)

#         # Filter using user if it exists
#         queryset = Payment_info.objects.all()

#         if user:
#             queryset = queryset.filter(userId=user)

#         # Handle empty queryset
#         if not queryset.exists():
#             return self.get_paginated_response({"count": 0, "result": []})

#         # Get unique users and total payment amount
#         user_summary = (
#             queryset.filter(filter_query)
#             .values("userId")
#             .annotate(total_per_user=Sum("payment_amount"), count=Count("userId"))
#             .order_by("userId")
#         )

#         # Apply pagination
#         paginator = Paginator(user_summary, self.pagination_class.page_size)
#         page = self.request.query_params.get("page", 1)
#         try:
#             paginated_user_summary = paginator.page(page)
#         except PageNotAnInteger:
#             paginated_user_summary = paginator.page(1)
#         except EmptyPage:
#             paginated_user_summary = paginator.page(paginator.num_pages)

#         # Prefetch per_user data
#         queryset = queryset.prefetch_related(
#             Prefetch(
#                 "payment_info",
#                 queryset=Payment_info.objects.filter(filter_query).order_by("created_at"),
#                 to_attr="filtered_per_user",
#             )
#         )

#         # Build response
#         response = {"count": len(user_summary), "result": []}

#         for user_data in paginated_user_summary:
#             user_id = user_data["userId"]
#             user_identity = get_identity(user_id)
#             per_user = list(
#                 queryset.filter(userId=user_id).values(
#                     "userId", "payment_amount", "payment_method", "created_at"
#                 )
#             )

#             # Build result dictionary
#             result_dict = {
#                 **user_identity,
#                 "per_user": per_user,
#                 "total_per_user": user_data["total_per_user"],
#             }

#             response["result"].append(result_dict)

#         return self.get_paginated_response(response)