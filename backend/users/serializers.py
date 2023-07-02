from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from rest_framework import serializers

from django.contrib.auth import get_user_model


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
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_usbscribed',
    )

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

    def get_is_usbscribed(self, obj: User) -> bool:
        """
        Проверка статуса подписки.

        Возвращает True, если текущий пользователь подписан на автора,
        данные которого представлены в obj.
        """
        return (
            self.context.get('request')
            and hasattr(self.context['request'], 'user')
            and self.context.get('request').user.is_authenticated
            and (
                self.context.get(
                    'request',
                ).user.follower.filter(
                    following=obj,
                ).exists()
            )
        )
