from django.urls import path

from .views import create, get_products_by_category, delete, update


urlpatterns = [
    path('', create),
    path('/category/<int:category_id>', get_products_by_category),
    path('/upload/<int:id_product>', update),
    path('/<int:id_product>', delete),
]