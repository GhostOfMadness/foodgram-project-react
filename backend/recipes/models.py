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
    """The Tag model."""

    name = models.CharField(_('name'), max_length=200, unique=True)
    color = models.CharField(
        _('color'),
        max_length=7,
        unique=True,
        validators=[HexColorValidator()],
    )
    slug = models.SlugField(_('slug'), max_length=200, unique=True)

    class Meta:
        ordering = ['slug']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self) -> str:
        return self.slug[:STR_MAX_LENGTH]


class Ingredient(models.Model):
    """The Ingredient model."""

    name = models.CharField(_('name'), max_length=200)
    measurement_unit = models.CharField(_('measurement unit'), max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        indexes = [
            models.Index(fields=['name'], name='ingredient_name_idx'),
        ]

    def __str__(self) -> str:
        return self.name[:STR_MAX_LENGTH]


class Recipe(models.Model):
    """The Recipe model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('author'),
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name=_('image'),
    )
    name = models.CharField(_('name'), max_length=200)
    text = models.TextField(_('description'))
    cooking_time = models.PositiveSmallIntegerField(
        _('cooking time (minutes)'),
        validators=[
            MinValueValidator(
                1,
                _('Cooking time cannot be less than 1 minute.'),
            ),
        ],
    )
    pub_date = models.DateTimeField(_('publication date'), auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
        indexes = [
            models.Index(fields=['name'], name='recipe_name_idx'),
        ]

    def __str__(self) -> str:
        return self.name[:STR_MAX_LENGTH]


class RecipeIngredient(models.Model):
    """Intermediary join table to pair recipe-ingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('ingredient'),
    )
    amount = models.PositiveSmallIntegerField(
        _('amount'),
        validators=[
            MinValueValidator(
                1,
                _('Amount cannot be less than 1 measurement unit.'),
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
    """Intermediary join table to pair recipe-tag."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name=_('tag'),
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
    """The abstract model to store user-recipe pairs."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name=_('user'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name=_('recipe'),
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
    """The Shopping cart model."""

    class Meta(ListModel.Meta):
        verbose_name = _('Shopping cart')
        verbose_name_plural = _('Shopping carts')


class FavoritesList(ListModel):
    """The Favourites model."""

    class Meta(ListModel.Meta):
        verbose_name = _('Favorites list')
        verbose_name_plural = _('Favorites lists')
