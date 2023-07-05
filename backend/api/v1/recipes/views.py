from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from recipes.models import Ingredient, Tag, Recipe
from .serializers import IngredientSeralizer, TagSeralizer, RecipeSerializer
from .permissions import IsAuthor
from api.v1.pagination import PageLimitPagination
from .filters import RecipeFilterSet


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
        Возвращает набор объектов в зависимости от парамета запроса.

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

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthor()]
        return [permissions.AllowAny()]
