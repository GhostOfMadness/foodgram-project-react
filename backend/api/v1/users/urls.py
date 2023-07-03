from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import UserViewSet


app_name = 'api_v1_users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
