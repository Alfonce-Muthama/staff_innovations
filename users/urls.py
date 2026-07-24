from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.create_user),
    path("login/", views.login_user),

    path("update/<uuid:pk>/", views.update_user),
    path("delete/<uuid:pk>/", views.delete_user),
    path("list/", views.list_users),
    
]

