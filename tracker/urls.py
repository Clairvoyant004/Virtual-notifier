from django.urls import path
from . import views

urlpatterns = [
    path("", views.leagues_overview, name="leagues-overview"),
]











