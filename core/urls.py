from django.urls import path

from core import views

urlpatterns = [
    path("", views.home_view, name="home"),
]
