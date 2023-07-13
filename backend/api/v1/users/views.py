from typing import ClassVar

from djoser.serializers import (
    SetPasswordSerializer as DjoserSetPasswordSerializer,
)
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Prefetch, Subquery
from django.utils.translation import gettext_lazy as _

from api.v1.views import MultiSeralizerViewSetMixin
from recipes.models import Recipe
from users.models import Follow

from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserSubscribeSerializer,
)


User = get_user_model()


class CreateRetrieveListViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    """Вьюсет для создания объекта, получения объекта или списка объектов."""


class UserViewSet(MultiSeralizerViewSetMixin, CreateRetrieveListViewSet):
    """
    Вьюсет для работы с пользователями.

    Действия:
    - создать пользователя;
    - получить список пользователей;
    - получить одного любого пользователя по его id;
    - отобразить профиль текущего пользователя;
    - изменить пароль текущего пользователя;
    - отобразить подписки текущего пользователя;
    - подписаться на автора;
    - отписаться от автора.
    """

    ACTIONS_AUTHENTICATED: ClassVar[tuple[str]] = (
        'retrieve',
        'me',
        'set_password',
        'subscriptions'
        'subscribe',
    )

    serializer_class = UserSerializer
    serializer_classes = {
        'create': UserCreateSerializer,
        'set_password': DjoserSetPasswordSerializer,
        'subscriptions': UserSubscribeSerializer,
        'subscribe': UserSubscribeSerializer,
    }

    def _prefetch_recipes(self) -> Subquery:
        """Подзапрос для извлечения только указанного числа рецептов."""
        recipes_limit = self.request.query_params.get('recipes_limit')
        recipes_limit = int(recipes_limit) if recipes_limit else recipes_limit
        subquery = Subquery(
            Recipe.objects.filter(
                author__id=OuterRef('author__id'),
            ).values_list(
                'id',
                flat=True,
            )[:recipes_limit],
        )
        return Prefetch(
            'recipes',
            queryset=Recipe.objects.filter(id__in=subquery),
        )

    def _is_subscription_exists(self) -> Exists:
        """Подзапрос для проверки статуса подписки."""
        return Exists(
            Follow.objects.filter(
                follower__id=self.request.user.id,
                following=OuterRef('pk'),
            ),
        )

    def get_queryset(self):
        qs = User.objects.prefetch_related(
            'following',
            self._prefetch_recipes(),
        ).annotate(
            is_subscribed=self._is_subscription_exists(),
            recipes_count=Count('recipes'),
        ).order_by(
            'pk',
        )
        if self.action == 'subscriptions':
            return qs.filter(following__follower=self.request.user)
        return qs

    def get_permissions(self):
        if self.action in self.ACTIONS_AUTHENTICATED:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_instance(self) -> User:
        return self.get_queryset().get(pk=self.request.user.pk)

    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        return DjoserUserViewSet.me(self, request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        return DjoserUserViewSet.set_password(self, request, *args, *kwargs)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def _add_to_subscribes(
        self,
        user: User,
        author: User,
        exists: bool,
    ) -> Response:
        """Добавить автора в подписки."""
        if author == user:
            raise serializers.ValidationError(
                {
                    'errors': _('Вы не можете подписаться на себя.'),
                },
            )
        if exists:
            raise serializers.ValidationError(
                {
                    'errors': _('Вы уже подписаны на этого автора.'),
                },
            )
        user.subscriptions.add(author)
        serializer_class = self.get_serializer_class()(
            self.get_object(),
            many=False,
        )
        data = serializer_class.data
        return Response(data, status=status.HTTP_201_CREATED)

    def _delete_from_subscriptions(
        self,
        user: User,
        author: User,
        exists: bool,
    ) -> Response:
        """Удалить автора из подписок."""
        if not exists:
            raise serializers.ValidationError(
                {
                    'errors': _('Этого автора нет в подписках.'),
                },
            )
        user.follower.filter(following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        user = request.user
        exists = user.follower.filter(following=author).exists()
        if request.method == 'POST':
            return self._add_to_subscribes(user, author, exists)
        if request.method == 'DELETE':
            return self._delete_from_subscriptions(user, author, exists)
