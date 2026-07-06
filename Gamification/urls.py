from django.urls import path
from . import views

urlpatterns = [
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("my-badges/", views.my_badges, name="my_badges"),

]

