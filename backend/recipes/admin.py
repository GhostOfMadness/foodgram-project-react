import os
from typing import Any

from dotenv import load_dotenv

from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .admin_filters import (
    ListRecipeFilter,
    ListUserFilter,
    RecipeAuthorFilter,
    RecipeTagFilter,
)
from .models import (
    FavoritesList,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)


load_dotenv()

ADMIN_INLINE_EXTRA = int(os.getenv('ADMIN_INLINE_LEN', default=1))


class RecipeIngredientInline(admin.TabularInline):
    """Конфиг для отображения ингредиентов на странице рецепта."""

    model = RecipeIngredient
    extra = ADMIN_INLINE_EXTRA


class RecipeTagInline(admin.TabularInline):
    """Конфиг для отображения тегов на странице рецепта."""

    model = RecipeTag
    extra = ADMIN_INLINE_EXTRA


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели тега."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели ингредиента."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели рецепта."""

    list_display = (
        'name',
        'author',
    )
    list_filter = (RecipeAuthorFilter, RecipeTagFilter)
    search_fields = ('name',)
    fieldsets = [
        (
            None,
            {
                'fields': [
                    'author',
                    'image',
                    'name',
                    'text',
                    'cooking_time',
                    'additions_to_favorites_count',
                ],
            },
        ),
    ]
    readonly_fields = ['additions_to_favorites_count']
    inlines = [RecipeIngredientInline, RecipeTagInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """Для каждого рецепта подсчет числа раз добавления в избранное."""
        return super().get_queryset(request).select_related(
            'author',
        ).prefetch_related(
            'tags',
            'ingredients',
        ).annotate(
            count_favorite=Count('favoriteslist_related'),
        )

    @admin.display(description='В избранном (раз)')
    def additions_to_favorites_count(self, obj: Recipe) -> int:
        """Сколько раз рецепт был добавлен в избранное."""
        return obj.count_favorite


class ListConfig(admin.ModelAdmin):
    """Конфиг админ-зоны для моделей списков."""

    list_display = ('user', 'recipe')
    list_filter = (ListUserFilter, ListRecipeFilter)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related(
            'user',
            'recipe',
        )


@admin.register(FavoritesList)
class FavoritesListConfig(ListConfig):
    """Конфиг админ-зоны для списка избранного."""


@admin.register(ShoppingCart)
class ShoppingCartConfig(ListConfig):
    """Конфиг админ-зоны для списка покупок."""
