from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin config for the User model."""

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
    )
    search_fields = ('username',)
    list_filter = ('email', 'username')
