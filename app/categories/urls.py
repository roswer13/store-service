from django.urls import path

from .views import create, get_categories


urlpatterns = [
    path('', create),
    path('/getCategories', get_categories),
]