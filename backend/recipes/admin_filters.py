from admin_auto_filters.filters import AutocompleteFilter

from django.utils.translation import gettext_lazy as _


class RecipeAuthorFilter(AutocompleteFilter):
    """Фильтр рецепта по автору."""

    title = _('Автор')
    field_name = 'author'


class RecipeTagFilter(AutocompleteFilter):
    """Фильтр рецепта по тегу."""

    title = _('Тег')
    field_name = 'tags'


class ListUserFilter(AutocompleteFilter):
    """Фильтр избранного/ списка покупок по пользователю."""

    title = _('Пользователь')
    field_name = 'user'


class ListRecipeFilter(AutocompleteFilter):
    """Фильтр избранного/ списка покупок по рецепту."""

    title = _('Рецепт')
    field_name = 'recipe'
