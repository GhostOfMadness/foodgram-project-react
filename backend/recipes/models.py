import os

from dotenv import load_dotenv

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import HexColorValidator


load_dotenv()

STR_MAX_LENGTH = int(os.getenv('MODEL_STR_MAX_LENGTH', default=30))

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(_('Название'), max_length=200, unique=True)
    color = models.CharField(
        _('HEX-цвет'),
        max_length=7,
        unique=True,
        validators=[HexColorValidator()],
    )
    slug = models.SlugField(_('Слаг'), max_length=200, unique=True)

    class Meta:
        ordering = ['slug']
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self) -> str:
        return self.slug[:STR_MAX_LENGTH]


class IngredientQuerySet(models.QuerySet):
    """Дополнительный метод для модели ингредиентов."""

    def order_by_is_startswith_value(self, value):
        """
        Сортировка на основе вхождения строки в начало.

        В запросе создается временный булевый столбец (is_startswith),
        принимающий значение True, если название ингредиента начинается с
        заданного значения и False в противном случае. Все объекты
        сортируются по полученному значению (от True к False).
        """
        is_startswith_value = models.Case(
            models.When(name__istartswith=value, then=models.Value(True)),
            default=models.Value(False),
        )
        return self.alias(
            is_startswith=is_startswith_value,
        ).order_by(
            '-is_startswith',
            models.functions.Lower('name'),
        )


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(_('Название'), max_length=200)
    measurement_unit = models.CharField(
        _('Единицы измерения'),
        max_length=200,
    )

    objects = IngredientQuerySet.as_manager()

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        indexes = [
            models.Index(fields=['name'], name='ingredient_name_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        ]

    def __str__(self) -> str:
        return self.name[:STR_MAX_LENGTH]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name=_('Изображение'),
    )
    name = models.CharField(_('Название'), max_length=200)
    text = models.TextField(_('Описание'))
    cooking_time = models.PositiveSmallIntegerField(
        _('Время приготовления (в минутах)'),
        validators=[
            MinValueValidator(
                1,
                _('Время приготовления не может быть меньше 1 минуты.'),
            ),
        ],
    )
    pub_date = models.DateTimeField(_('publication date'), auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        indexes = [
            models.Index(fields=['name'], name='recipe_name_idx'),
        ]

    def __str__(self) -> str:
        return self.name[:STR_MAX_LENGTH]


class RecipeIngredient(models.Model):
    """Промежуточная таблица для пары рецепт-ингредиент."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        _('Количество'),
        validators=[
            MinValueValidator(
                1,
                _('Количество не может быть меньше 1 единицы измерения.'),
            ),
        ],
    )

    class Meta:
        ordering = ['recipe', 'ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient}'


class RecipeTag(models.Model):
    """Промежуточная таблица для пары рецепт-тег."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name=_('Тег'),
    )

    class Meta:
        ordering = ['recipe', 'tag']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.tag}'


class ListModel(models.Model):
    """Абстрактная модель для пар пользователь-рецепт."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name=_('Пользователь'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name=_('Рецепт'),
    )

    class Meta:
        abstract = True
        ordering = ['user', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_user_recipe',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class ShoppingCart(ListModel):
    """Модель списка покупок."""

    class Meta(ListModel.Meta):
        verbose_name = _('Shopping cart')
        verbose_name_plural = _('Shopping carts')


class FavoritesList(ListModel):
    """Модель списка избранного."""

    class Meta(ListModel.Meta):
        verbose_name = _('Favorites list')
        verbose_name_plural = _('Favorites lists')
