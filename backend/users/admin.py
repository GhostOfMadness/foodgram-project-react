from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Конфиг админ-зоны для модели пользователя."""

    add_form_template = 'users/add_form.html'

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
    )
    search_fields = ('username',)
    list_filter = ('email', 'username')
    fieldsets = [
        (
            None,
            {'fields': ('email', 'password')},
        ),
        (
            'Personal info',
            {'fields': ('first_name', 'last_name', 'username')},
        ),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser')},
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    ]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели подписки."""

    list_display = ('follower', 'following')
    list_filter = ('follower', 'following')
