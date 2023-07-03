from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import IngredientViewSet, TagViewSet


app_name = 'api_v1_recipes'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
