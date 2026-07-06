from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_user),
    path("login/", views.login_user),
    path("update/", views.update_user),
    path("delete/", views.delete_user),
]

