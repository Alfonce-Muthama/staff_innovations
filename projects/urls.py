from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_projects, name="list_projects"),
    path("<uuid:pk>/", views.project_detail, name="project_detail"),
    path("<uuid:pk>/update/", views.update_project, name="update_project"),
    path("<uuid:pk>/delete/", views.delete_project, name="delete_project"),

    path("<uuid:project_id>/phases/create/", views.create_phase, name="create_phase"),
    path("phases/<uuid:phase_id>/tasks/create/", views.create_task, name="create_task"),
    path("tasks/<uuid:task_id>/complete/", views.mark_task_complete, name="mark_task_complete"),
]


