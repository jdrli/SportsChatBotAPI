from django.db import models
from datetime import datetime

class ScrapingJob(models.Model):
    """
    Model to track scraping jobs
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.status}"

class ScrapedData(models.Model):
    """
    Generic model for scraped sports data
    """
    source_url = models.URLField(max_length=500)
    data_type = models.CharField(max_length=100)  # basketball, football, etc.
    season = models.CharField(max_length=9)  # e.g., "2023-24"
    raw_data = models.JSONField()  # Store raw scraped data as JSON
    processed_data = models.JSONField(null=True, blank=True)  # Store processed data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    scraped_at = models.DateTimeField()
    source = models.CharField(max_length=100)  # ncaa, espn, etc.
    checksum = models.CharField(max_length=64, unique=True)  # To prevent duplicates
    
    def __str__(self):
        return f"{self.data_type} - {self.season} - {self.source}"

class BasketballStats(models.Model):
    """
    Model for basketball statistics
    """
    player_name = models.CharField(max_length=200)
    team_name = models.CharField(max_length=100)
    season = models.CharField(max_length=9)  # e.g., "2023-24"
    games_played = models.IntegerField(null=True, blank=True)
    points_per_game = models.FloatField(null=True, blank=True)
    field_goal_percentage = models.FloatField(null=True, blank=True)
    three_point_percentage = models.FloatField(null=True, blank=True)
    free_throw_percentage = models.FloatField(null=True, blank=True)
    rebounds_per_game = models.FloatField(null=True, blank=True)
    assists_per_game = models.FloatField(null=True, blank=True)
    steals_per_game = models.FloatField(null=True, blank=True)
    blocks_per_game = models.FloatField(null=True, blank=True)
    turnovers_per_game = models.FloatField(null=True, blank=True)
    minutes_per_game = models.FloatField(null=True, blank=True)
    is_demo_data = models.BooleanField(default=False)  # Flag for demo data
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player_name} - {self.team_name} ({self.season})"

class FootballStats(models.Model):
    """
    Model for football statistics
    """
    player_name = models.CharField(max_length=200)
    team_name = models.CharField(max_length=100)
    position = models.CharField(max_length=10, null=True, blank=True)  # QB, RB, WR, etc.
    season = models.CharField(max_length=9)  # e.g., "2023-24"
    games_played = models.IntegerField(null=True, blank=True)
    passing_yards = models.IntegerField(null=True, blank=True)
    passing_touchdowns = models.IntegerField(null=True, blank=True)
    interceptions_thrown = models.IntegerField(null=True, blank=True)
    rushing_yards = models.IntegerField(null=True, blank=True)
    rushing_touchdowns = models.IntegerField(null=True, blank=True)
    receiving_yards = models.IntegerField(null=True, blank=True)
    receiving_touchdowns = models.IntegerField(null=True, blank=True)
    total_tackles = models.IntegerField(null=True, blank=True)
    sacks = models.FloatField(null=True, blank=True)
    interceptions = models.IntegerField(null=True, blank=True)
    fumbles_recovered = models.IntegerField(null=True, blank=True)
    is_demo_data = models.BooleanField(default=False)  # Flag for demo data
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player_name} - {self.team_name} ({self.season})"
