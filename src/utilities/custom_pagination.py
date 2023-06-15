from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        next_page = self.get_next_link()
        prev_page = self.get_previous_link()
        return Response({
            'next': next_page,
            'previous': prev_page,
            'count': self.page.paginator.count,
            'results': data
        })