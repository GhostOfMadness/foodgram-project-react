from typing import Any

from more_admin_filters import MultiSelectDropdownFilter

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .admin_filters import FollowFollowerFilter, FollowFollowingFilter
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
    list_display_links = ('username', 'email')
    search_fields = ('username', 'email')
    list_filter = (
        ('email', MultiSelectDropdownFilter),
        ('username', MultiSelectDropdownFilter),
    )
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
    list_filter = (FollowFollowerFilter, FollowFollowingFilter)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related(
            'follower',
            'following',
        )
