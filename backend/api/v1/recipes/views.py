import csv
import datetime
from typing import Any, ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models import QuerySet, Sum
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from recipes.models import Ingredient, Recipe, Tag

from .filters import RecipeFilterSet
from .permissions import IsAuthor
from .serializers import IngredientSeralizer, RecipeSerializer, TagSeralizer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSeralizer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSeralizer
    pagination_class = None
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Возвращает набор объектов в зависимости от параметра запроса.

        Если в запросе есть параметр name, то выводит только те записи,
        которые содержат искомый параметр в произвольном месте. Сначала
        идут записи, содержащие значение в начале, затем - все остальные.
        """
        if self.request.query_params and 'name' in self.request.query_params:
            search_value = self.request.query_params['name']
            return Ingredient.objects.filter(
                name__icontains=search_value,
            ).order_by_is_startswith_value(
                search_value,
            )
        return super().get_queryset()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения рецептов."""

    ACTIONS_AUTHENTICATED: ClassVar[tuple[str]] = (
        'create',
        'favorite',
        'shopping_cart',
        'download_shopping_cart',
    )
    ACTIONS_AUTHOR: ClassVar[tuple[str]] = (
        'partial_update',
        'destroy',
    )

    queryset = Recipe.objects.select_related(
        'author',
    ).prefetch_related(
        'tags',
        'ingredients',
    ).all()
    serializer_class = RecipeSerializer
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
        'trace',
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        if self.action == 'download_shopping_cart':
            return self.request.user.shopping_cart_recipes.prefetch_related(
                'recipe_ingredients',
            ).values(
                'recipe_ingredients__ingredient',
            ).annotate(
                amount=Sum('recipe_ingredients__amount'),
            ).values(
                'recipe_ingredients__ingredient__name',
                'amount',
                'recipe_ingredients__ingredient__measurement_unit',
            ).order_by(
                'recipe_ingredients__ingredient__name',
            )
        return super().get_queryset()

    def get_permissions(self):
        if self.action in self.ACTIONS_AUTHENTICATED:
            return [permissions.IsAuthenticated()]
        if self.action in self.ACTIONS_AUTHOR:
            return [IsAuthor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        self.get_object().recipe_ingredients.all().delete()
        return super().perform_update(serializer)

    def _get_short_recipe(self, recipe: Recipe) -> dict[str, Any]:
        """Вернуть короткую версию рецепта в виде словаря."""
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image.url,
            'cooking_time': recipe.cooking_time,
        }

    def _add_to_list(
        self,
        related_name: str,
        error_message: str,
    ) -> Response:
        """Добавить рецепт в список."""
        user = self.request.user
        recipe = self.get_object()
        is_exists = getattr(user, related_name).filter(recipe=recipe).exists()
        if is_exists:
            raise serializers.ValidationError(
                {
                    'recipe_id': error_message,
                },
                code='already_exist',
            )
        getattr(user, related_name).create(user=user, recipe=recipe)
        return Response(
            self._get_short_recipe(recipe),
            status=status.HTTP_201_CREATED,
        )

    def _delete_from_list(
        self,
        related_name: str,
        error_message: str,
    ) -> Response:
        """Удалить рецепт из списка."""
        user = self.request.user
        recipe = self.get_object()
        is_exists = getattr(user, related_name).filter(recipe=recipe).exists()
        if not is_exists:
            raise serializers.ValidationError(
                {
                    'recipe_id': error_message,
                },
                code='not_exist',
            )
        getattr(user, related_name).filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _add_to_list_delete_from_list(
        self,
        request: Request,
        related_name: str,
        error_message_add: str,
        error_message_delete: str,
    ):
        """Добавить рецепт в список/ удалить рецепт из списка."""
        if request.method == 'POST':
            return self._add_to_list(
                related_name=related_name,
                error_message=error_message_add,
            )
        if request.method == 'DELETE':
            return self._delete_from_list(
                related_name=related_name,
                error_message=error_message_delete,
            )

    def _shopping_cart_qs_to_dataset(
        self,
        queryset: QuerySet,
    ) -> list[dict[str, Any]]:
        """Преобразовать набор ингредиентов в список словарей."""
        return [
            {
                '№': elem[0],
                'Наименование': elem[1].get(
                    'recipe_ingredients__ingredient__name',
                ),
                'Количество': elem[1].get(
                    'amount',
                ),
                'Единицы измерения': elem[1].get(
                    'recipe_ingredients__ingredient__measurement_unit',
                ),
            }
            for elem in enumerate(queryset, 1)
        ]

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        """Добавить рецепт в избранное/ удалить из избранного."""
        return self._add_to_list_delete_from_list(
            request=request,
            related_name='favoriteslist_related',
            error_message_add=_('Рецепт уже в избранном'),
            error_message_delete=_('Рецепта нет в избранном.'),
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """Добавить рецепт в список покупок/ удалить из списка покупок."""
        return self._add_to_list_delete_from_list(
            request=request,
            related_name='shoppingcart_related',
            error_message_add=_('Рецепт уже в списке покупок.'),
            error_message_delete=_('Рецепта нет в списке покупок.'),
        )

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачать ингредиенты для рецептов из списка покупок."""
        qs = self.get_queryset()
        data = self._shopping_cart_qs_to_dataset(qs)
        response = HttpResponse(content_type='text/csv')
        writer = csv.DictWriter(
            response,
            fieldnames=[
                '№',
                'Наименование',
                'Количество',
                'Единицы измерения',
            ],
        )
        writer.writeheader()
        writer.writerows(data)
        current_date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = f'shopping_cart_{current_date}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
