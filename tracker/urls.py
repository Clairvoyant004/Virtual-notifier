from django.urls import path
from . import views

urlpatterns = [
    path("leagues/", views.league_list, name="league-home"),
    path("leagues/<int:league_id>/", views.league_detail, name="league-detail"),
]
