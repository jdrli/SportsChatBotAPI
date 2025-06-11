import requests
from .models import PlayerStat

def fetch_nba_stats():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Example parsing: Navigate through data to find player stats (you'll want to adapt this to the exact structure)
    # For demo, assuming player stats in data['players'] (replace with actual keys)
    players = data.get('players', [])

    # Clear existing data to avoid duplicates (optional)
    PlayerStat.objects.all().delete()

    for player in players:
        PlayerStat.objects.create(
            player_id=player.get('id', ''),
            player_name=player.get('fullName', ''),
            team_name=player.get('team', {}).get('displayName', ''),
            points=player.get('stats', {}).get('points', 0),
            rebounds=player.get('stats', {}).get('rebounds', 0),
            assists=player.get('stats', {}).get('assists', 0),
        )
