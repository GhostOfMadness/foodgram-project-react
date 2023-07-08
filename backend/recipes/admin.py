import os

from dotenv import load_dotenv

from django.contrib import admin

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
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели ингредиента."""

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели рецепта."""

    list_display = (
        'name',
        'author',
    )
    list_filter = ('name', 'author', 'tags')
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

    @admin.display(description='В избранном (раз)')
    def additions_to_favorites_count(self, obj: Recipe) -> int:
        """Сколько раз рецепт был добавлен в избранное."""
        return obj.favoriteslist_related.count()


class ListConfig(admin.ModelAdmin):
    """Конфиг админ-зоны для моделей списков."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(FavoritesList)
class FavoritesListConfig(ListConfig):
    """Конфиг админ-зоны для списка избранного."""


@admin.register(ShoppingCart)
class ShoppingCartConfig(ListConfig):
    """Конфиг админ-зоны для списка покупок."""
