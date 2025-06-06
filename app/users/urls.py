from django.urls import path

from users.views import update, update_image, get_user, get_all_users


urlpatterns = [
    path('/<user_id>', update),
    path('/findById/<user_id>', get_user),
    path('/', get_all_users),
    path('/upload/<user_id>', update_image),
]