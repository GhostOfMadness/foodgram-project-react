from admin_auto_filters.filters import AutocompleteFilter

from django.utils.translation import gettext_lazy as _


class FollowFollowerFilter(AutocompleteFilter):
    """Фильтр подписок по подписчику."""

    title = _('Подписчик')
    field_name = 'follower'


class FollowFollowingFilter(AutocompleteFilter):
    """Фильтр подписок по автору."""

    title = _('Автор')
    field_name = 'following'
