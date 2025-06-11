from django.urls import path
from .views import espnproxy
from .views import fetch_nba_data_view

urlpatterns = [
    path("get/", espnproxy),
    path('fetch-nba-data/', fetch_nba_data_view, name='fetch-nba-data'),
]
