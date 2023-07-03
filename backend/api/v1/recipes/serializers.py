from rest_framework import serializers

from recipes.models import Ingredient, Tag


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
