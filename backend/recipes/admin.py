import os

from dotenv import load_dotenv

from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


load_dotenv()

ADMIN_INLINE_EXTRA = int(os.getenv('ADMIN_INLINE_LEN', default=1))


class RecipeIngredientInline(admin.TabularInline):
    """Config to show ingredients on a recipe page."""

    model = RecipeIngredient
    extra = ADMIN_INLINE_EXTRA


class RecipeTagInline(admin.TabularInline):
    """Config to show tags on a recipe page."""

    model = RecipeTag
    extra = ADMIN_INLINE_EXTRA


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin config for the Tag model."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin config for the Ingredient model."""

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin config for the Recipe model."""

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

    @admin.display(description='favorites')
    def additions_to_favorites_count(self, obj):
        return obj.favoriteslist_related.count()
