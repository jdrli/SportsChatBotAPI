from django.urls import path
from . import views

urlpatterns = [
    path('run/', views.run_scraper, name='run-scraper'),
    path('status/<int:job_id>/', views.get_job_status, name='job-status'),
    path('ncaa/basketball/', views.run_ncaa_basketball_scraper, name='ncaa-basketball-scraper'),
    path('ncaa/football/', views.run_ncaa_football_scraper, name='ncaa-football-scraper'),
]
