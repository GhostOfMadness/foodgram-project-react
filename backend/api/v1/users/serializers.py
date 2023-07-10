from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from rest_framework import serializers

from django.contrib.auth import get_user_model

from api.v1.utils import is_in_user_list
from recipes.models import Recipe


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    password = serializers.CharField(
        max_length=150,
        style={'input_type': 'password'},
        write_only=True,
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя с аннотацией."""

    is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class MethodFieldUserSerializer(UserSerializer):
    """Сериализатор для отображения пользователя с methodfield."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
    )

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Проверка статуса подписки.

        Возвращает True, если текущий пользователь подписан на автора,
        данные которого представлены в obj.
        """
        return is_in_user_list(
            serializer=self,
            obj=obj,
            related_name='follower',
            field_name='following',
        )


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сокращенное отображение рецепта."""

    image = serializers.URLField(source='image.url')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(UserSerializer):
    """Отображение пользователя в подписке."""

    recipes = RecipeMinifiedSerializer(
        many=True,
        read_only=True,
    )
    recipes_count = serializers.IntegerField()
    is_subscribed = serializers.BooleanField(read_only=True, default=True)

    class Meta(UserSerializer.Meta):
        fields = (
            UserSerializer.Meta.fields
            + (
                'recipes',
                'recipes_count',
            )
        )
