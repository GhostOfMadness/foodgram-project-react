from rest_framework import pagination


class PageLimitPagination(pagination.PageNumberPagination):
    """Пагинатор для отображения пользователей."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
