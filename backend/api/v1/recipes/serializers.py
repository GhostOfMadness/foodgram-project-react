from typing import Any, Union

from drf_extra_fields.fields import Base64ImageField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from api.v1.users.serializers import MethodFieldUserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class DictPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Возвращает словарь объекта по первичному ключу."""

    def to_representation(self, value):
        return model_to_dict(value)


class TagSeralizer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSeralizer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = ('name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects,
        many=False,
        source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        representation: dict[str, Any] = {}
        ingredient = model_to_dict(instance.ingredient)
        for key, value in ingredient.items():
            representation[key] = value
        representation['amount'] = instance.amount
        return representation


class RecipeSerializer(WritableNestedModelSerializer):
    """Сериализатор для отображения рецепта."""

    author = MethodFieldUserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False,
    )
    tags = DictPrimaryKeyRelatedField(many=True, queryset=Tag.objects)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def _many_to_many_field_validate(
        self,
        data: list[Union[Ingredient, Tag]],
        message: str,
    ):
        """Проверяет, что значение используется ровно 1 раз."""
        unique_values: set[Union[Ingredient, Tag]] = set()
        error_messages: list[str] = []
        for obj in data:
            if obj in unique_values:
                error_params = {'name': obj.name}
                error_messages.append(message % error_params)
            unique_values.add(obj)
        if error_messages:
            raise serializers.ValidationError(error_messages)

    def validate_ingredients(self, data):
        message = _(
            'Ингредиент "%(name)s" уже выбран. Пожалуйста, поменяйте его '
            'количество, а инструкцию с количеством для каждого шага '
            'оставьте в описании.',
        )
        ingredients = [ingredient['ingredient'] for ingredient in data]
        self._many_to_many_field_validate(
            data=ingredients,
            message=message,
        )
        return data

    def validate_tags(self, data):
        message = _('Тег "%(name)s" уже выбран. Пожалуйста, выберите другой.')
        self._many_to_many_field_validate(data=data, message=message)
        return data
