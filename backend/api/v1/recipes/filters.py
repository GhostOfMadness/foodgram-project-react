import django_filters

from django.db.models import Subquery

from recipes.models import Recipe, Tag


class RecipeFilterSet(django_filters.FilterSet):
    """
    Фильтры для рецептов.

    - author - рецепты автора с переданным id;
    - is_favorited - рецепты в избранном текущего пользователя;
    - is_in_shopping_cart - рецепты в списке покупок текущего пользователя;
    - tags - рецепты с одним из указанных тегов.
    """

    author = django_filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact',
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_in_list(queryset, value, 'favorites_recipes')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_in_list(queryset, value, 'shopping_cart_recipes')

    def _filter_in_list(self, queryset, value, related_name):
        user = self.request.user
        if user.is_authenticated and value == 1:
            return queryset.filter(
                id__in=Subquery(
                    getattr(user, related_name).values_list('id', flat=True),
                ),
            )
        return queryset
