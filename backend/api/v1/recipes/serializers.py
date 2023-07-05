from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient, RecipeTag
from api.v1.users.serializers import UserSerializer
from api.v1.utils import is_something_true


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецептах."""

    id = serializers.IntegerField(
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_id(self, value):
        """Проверка, что объект с переданным id существует."""
        try:
            Ingredient.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                _(
                    f'Недопустимый первичный ключ "{value}" '
                    '- объект не существует.',
                ),
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
    )
    tags = DictPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects,
        source='tag',
    )
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')

        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        self._create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance_required_fields = (
            'image',
            'name',
            'text',
            'cooking_time',
        )
        for field in instance_required_fields:
            setattr(
                instance,
                field,
                validated_data.get(field, getattr(instance, field)),
            )

        tags = validated_data.get('tag')
        if tags:
            instance.tags.all().delete()
            RecipeTag.objects.bulk_create(
                [RecipeTag(recipe=instance, tag=tag) for tag in tags],
            )
        ingredients = validated_data.get('ingredients')
        if ingredients:
            instance.ingredients.all().delete()
            self._create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def get_is_favorited(self, obj: Recipe) -> bool:
        """Возвращает True, если рецепт в избранном."""
        return is_something_true(
            serializer=self,
            obj=obj,
            related_name='favoriteslist_related',
            field_name='recipe',
        )

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """Возвращает True, если рецепт в списке покупок."""
        return is_something_true(
            serializer=self,
            obj=obj,
            related_name='shoppingcart_related',
            field_name='recipe',
        )

    def _create_ingredients(self, ingredients, recipe):
        """Записывает пары рецепт - ингредиент в RecipeIngredient."""
        ingredient_list: list[RecipeIngredient] = []
        for ingredient in ingredients:
            ingredient_pk = ingredient['ingredient']['id']
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient_pk)
            ingredient_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount,
                ),
            )
        RecipeIngredient.objects.bulk_create(ingredient_list)
