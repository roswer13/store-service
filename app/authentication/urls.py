from django.urls import path
from .views import register, login


urlpatterns = [
    path('/register', register),
    path('/login', login)
    # Add other app URLs here
]