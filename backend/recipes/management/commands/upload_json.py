from typing import Any, Optional

from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from users.models import Follow, User

from ._utils import upload_json_file


FILES_ATTRS: dict[str, dict[str, Any]] = {
    'tags.json': {
        'model': Tag,
        'exclude_fields': (),
    },
    'ingredients.json': {
        'model': Ingredient,
        'exclude_fields': (),
    },
    'users.json': {
        'model': User,
        'exclude_fields': ('password',),
    },
    'recipes.json': {
        'model': Recipe,
        'exclude_fields': (),
    },
    'recipe_ingredient.json': {
        'model': RecipeIngredient,
        'exclude_fields': (),
    },
    'recipe_tag.json': {
        'model': RecipeTag,
        'exclude_fields': (),
    },
    'follow.json': {
        'model': Follow,
        'exclude_fields': (),
    },
    'favorites.json': {
        'model': FavoritesList,
        'exclude_fields': (),
    },
    'shopping_cart.json': {
        'model': ShoppingCart,
        'exclude_fields': (),
    },
}


class Command(BaseCommand):
    """Command to upload data from json files."""

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        for file_name, attrs in FILES_ATTRS.items():
            try:
                errors, total, valid = upload_json_file(
                    file_name=file_name,
                    model=attrs['model'],
                    exclude_fields=attrs['exclude_fields'],
                )
                self.stdout.write(
                    _(f'{file_name} - загружено {valid} из {total} объектов'),
                    ending=' ',
                )
                if total == valid:
                    self.stdout.write(self.style.SUCCESS('OK'))
                else:
                    self.stdout.write(self.style.ERROR('FAILED'))
                    for error in errors:
                        self.stderr.write(
                            _(f'Строка {error["id"]}:'),
                            ending=' ',
                        )
                        for key, value in error.items():
                            if key != 'id':
                                self.stderr.write(
                                    _(f'поле {key} - {value[0]}'),
                                    ending=' ',
                                )
                        self.stderr.write()
            except ValueError as e:
                self.stderr.write(
                    _(
                        f'{file_name} - ошибка при загрузке данных: '
                        f'{e}',
                    ),
                )
