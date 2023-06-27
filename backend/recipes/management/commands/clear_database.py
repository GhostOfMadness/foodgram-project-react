from typing import Any, Optional

from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from recipes.models import Ingredient, Recipe, Tag, User


class Command(BaseCommand):
    """Delete all database entries."""

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        Ingredient.objects.all().delete()
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(_('Все данные успешно удалены.')),
        )
