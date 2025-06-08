from django.urls import path
from .views import espnproxy

urlpatterns = [
    path("espn/", espnproxy),
]
