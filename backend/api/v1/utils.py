from rest_framework import serializers

from django.db.models import Model


def is_in_user_list(
    serializer: serializers.Serializer,
    obj: Model,
    related_name: str,
    field_name: str,
) -> bool:
    """Проверяет, что объект obj находится в списке пользователя."""
    params = {field_name: obj}
    return (
        serializer.context.get('request')
        and hasattr(serializer.context['request'], 'user')
        and serializer.context['request'].user.is_authenticated
        and getattr(
            serializer.context['request'].user,
            related_name,
        ).filter(
            **params,
        ).exists()
    )
