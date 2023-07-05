from rest_framework.permissions import IsAuthenticated


class IsAuthor(IsAuthenticated):
    """Доступ к объекту имеет только автор."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
