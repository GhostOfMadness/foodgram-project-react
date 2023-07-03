from rest_framework import permissions, viewsets

from recipes.models import Ingredient, Tag
from .serializers import IngredientSeralizer, TagSeralizer


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
