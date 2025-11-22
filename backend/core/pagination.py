from rest_framework.pagination import PageNumberPagination


class CustomPagePagination(PageNumberPagination):
    """Пагинация с выбором размера страницы через параметр 'limit'."""

    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 200
