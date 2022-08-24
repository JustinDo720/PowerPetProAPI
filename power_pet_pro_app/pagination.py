from rest_framework.pagination import PageNumberPagination


class ProductResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class MessageBarViewPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 5


class FeedbackResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


class SubmitBugPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'