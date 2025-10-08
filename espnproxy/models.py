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

    class League(models.Model):
        id = models.IntegerField(primary_key=True)
        name = models.CharField(max_length=100)
        abbreviation = models.CharField(max_length=10)

        def __str__(self):
            return self.name

    class Meta:
        verbose_name = "Player Stat"
        verbose_name_plural = "Player Stats"
        ordering = ['player_name']

    def __str__(self):
        return f"{self.player_name} ({self.team_name}) - {self.points} pts, {self.rebounds} reb, {self.assists} ast"    

# Note: The PlayerStat model is designed to store player statistics.
# You can extend it with more fields as needed, such as steals, blocks, etc.
# Ensure to run migrations after modifying the models.  