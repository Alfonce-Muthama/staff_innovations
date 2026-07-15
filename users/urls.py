from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_user),
    path("login/", views.login_user),

    path("update/<uuid:pk>/", views.update_user),
    path("delete/<uuid:pk>/", views.delete_user),
]

