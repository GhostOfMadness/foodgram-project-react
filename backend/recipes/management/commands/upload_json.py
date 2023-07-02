from typing import Any, Optional

from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from recipes.models import (
    FavoritesList,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

from ._utils import JSONLoader


FILES_ATTRS: list[dict[str, Any]] = [
    {
        'file_name': 'tags.json',
        'model': Tag,
    },
    {
        'file_name': 'ingredients.json',
        'model': Ingredient,
    },
    {
        'file_name': 'users.json',
        'model': User,
        'exclude_fields': ('password',),
    },
    {
        'file_name': 'recipes.json',
        'model': Recipe,
        'related_field_model_map': {'author_username': User},
        'file_fields': ('image',),
    },
    {
        'file_name': 'recipe_ingredient.json',
        'model': RecipeIngredient,
        'related_field_model_map': {
            'recipe_name': Recipe,
            'ingredient_name': Ingredient,
        },
    },
    {
        'file_name': 'recipe_tag.json',
        'model': RecipeTag,
        'related_field_model_map': {
            'recipe_name': Recipe,
            'tag_slug': Tag,
        },
    },
    {
        'file_name': 'follow.json',
        'model': Follow,
        'related_field_model_map': {
            'follower_username': User,
            'following_username': User,
        },
    },
    {
        'file_name': 'favorites.json',
        'model': FavoritesList,
        'related_field_model_map': {
            'user_username': User,
            'recipe_name': Recipe,
        },
    },
    {
        'file_name': 'shopping_cart.json',
        'model': ShoppingCart,
        'related_field_model_map': {
            'user_username': User,
            'recipe_name': Recipe,
        },
    },
]


class Command(BaseCommand):
    """Команда для загрузи данных из json-файлов."""

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        for file_attrs in FILES_ATTRS:
            try:
                loader = JSONLoader(**file_attrs)
                errors, total, valid = loader.create_model_objects()
                self.stdout.write(
                    _(
                        f'{file_attrs["file_name"]} - загружено {valid} '
                        f'из {total} объектов',
                    ),
                    ending=' ',
                )
                if total == valid:
                    self.stdout.write(self.style.SUCCESS('OK'))
                else:
                    self.stdout.write(self.style.ERROR('FAILED'))
                    for error in errors:
                        self.stderr.write(
                            _(f'Объект {error["object"]}:'),
                            ending=' ',
                        )
                        for key, value in error.items():
                            if key != 'object':
                                self.stderr.write(
                                    _(f'{key} - {value}'),
                                    ending=', ',
                                )
                        self.stderr.write()
            except ValueError as e:
                self.stderr.write(
                    _(
                        f'{file_attrs["file_name"]} - ошибка при '
                        f'загрузке данных: {e}',
                    ),
                )
