from django.urls import include, path


app_name = 'api_v1'

urlpatterns = [
    path('', include('api.v1.users.urls', namespace='api_v1_users')),
    path('', include('api.v1.recipes.urls', namespace='api_v1_recipes')),
]
