import django_filters

from recipes.models import Recipe


class RecipeFilterSet(django_filters.FilterSet):
    """Фильтры для рецептов."""

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

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_in_list(queryset, value, 'favoriteslist_related')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_in_list(queryset, value, 'shoppingcart_related')

    def _filter_in_list(self, queryset, value, related_name):
        user = self.request.user
        if user.is_authenticated and value == 1:
            pks = getattr(user, related_name).values('recipe')
            return queryset.filter(pk__in=pks)
        return queryset
