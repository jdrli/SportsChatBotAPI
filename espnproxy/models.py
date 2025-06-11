from django.db import models

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    
class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=200)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)

class PlayerStat(models.Model):
    player_id = models.CharField(max_length=100)
    player_name = models.CharField(max_length=255)
    team_name = models.CharField(max_length=100)
    points = models.FloatField()
    rebounds = models.FloatField()
    assists = models.FloatField()
    # Add more fields as needed

    def __str__(self):
        return f"{self.player_name} - {self.team_name}"
