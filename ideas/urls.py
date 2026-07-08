from django.urls import path
from . import views

urlpatterns = [
    path("create/",  views.create_new_idea,  name="create_idea" ),
    path("list/", views.list_ideas, name="list_ideas" ),
    path("detail/<uuid:pk>/", views.idea_detail, name="idea_detail" ),
    path("update/<uuid:pk>/",views.update_idea, name="update_idea"),
    path("delete/<uuid:pk>/", views.delete_idea, name="delete_idea"),
    path("approve/<uuid:pk>/", views.approve_idea, name="approve_idea"),
    path("reject/<uuid:pk>/", views.reject_idea, name="reject_idea"),
]

