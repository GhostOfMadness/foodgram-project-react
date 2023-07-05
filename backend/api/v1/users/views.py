from djoser.serializers import (
    SetPasswordSerializer as DjoserSetPasswordSerializer,
)
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model

from api.v1.pagination import PageLimitPagination
from .serializers import UserCreateSerializer, UserSerializer


User = get_user_model()


class CreateRetrieveListViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """Вьюсет для создания объекта, получения объекта или списка объектов."""


class UserViewSet(CreateRetrieveListViewSet):
    """
    Вьюсет для работы с пользователями.

    Действия:
    - создать пользователя;
    - получить список пользователей;
    - получить одного любого пользователя по его id;
    - отобразить профиль текущего пользователя;
    - изменить пароль текущего пользователя.
    """

    queryset = User.objects.all()
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action in ['retrieve', 'me', 'set_password']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return DjoserSetPasswordSerializer
        return UserSerializer

    def get_instance(self) -> User:
        return self.request.user

    @action(
        methods=['get'],
        detail=False,
    )
    def me(self, request, *args, **kwargs):
        return DjoserUserViewSet.me(self, request, *args, **kwargs)

    @action(
        methods=['post'],
        detail=False,
    )
    def set_password(self, request, *args, **kwargs):
        return DjoserUserViewSet.set_password(self, request, *args, *kwargs)
