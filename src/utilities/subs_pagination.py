from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class SubscriptionPagination(BasePagination):
    page_size = 10
    page_query_param = "page"
    max_page_size = "100"

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.page_size
        page_query_param = self.page_query_param
        max_page_size = int(self.max_page_size)

        try:
            page = int(request.query_params.get(page_query_param, 1))
        except ValueError:
            page = 1

        if page <= 0:
            return None

        offset = (page - 1) * page_size
        limit = offset + page_size

        if limit > max_page_size:
            return None

        return queryset[offset:limit]

    def get_paginated_response(self, data):
        return Response(data)
