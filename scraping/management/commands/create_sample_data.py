"""
Management command to create sample sports data for out-of-the-box functionality
"""
from django.core.management.base import BaseCommand
from scraping.models import BasketballStats, FootballStats
import random

class Command(BaseCommand):
    help = 'Create sample sports data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--basketball',
            action='store_true',
            help='Create sample basketball data',
        )
        parser.add_argument(
            '--football',
            action='store_true',
            help='Create sample football data',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create all sample data (default)',
        )

    def handle(self, *args, **options):
        create_basketball = options.get('basketball', False)
        create_football = options.get('football', False)
        create_all = options.get('all', False)
        
        # If no specific option is provided, default to all
        if not any([create_basketball, create_football, create_all]):
            create_all = True

        if create_basketball or create_all:
            self.create_sample_basketball_data()
            self.stdout.write(
                self.style.SUCCESS('Successfully created sample basketball data')
            )
        
        if create_football or create_all:
            self.create_sample_football_data()
            self.stdout.write(
                self.style.SUCCESS('Successfully created sample football data')
            )

    def create_sample_basketball_data(self):
        """Create sample basketball data for demonstration"""
        # Clear existing demo data to avoid duplicates
        BasketballStats.objects.filter(is_demo_data=True).delete()
        
        # Sample teams and players
        teams = ['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bucks', 'Suns', 'Nets', '76ers']
        first_names = ['LeBron', 'Stephen', 'Jayson', 'Jimmy', 'Giannis', 'Chris', 'Kevin', 'Joel', 'Luka', 'Damian']
        last_names = ['James', 'Curry', 'Tatum', 'Butler', 'Antetokounmpo', 'Paul', 'Durant', 'Embiid', 'Doncic', 'Lillard']
        
        # Generate unique player names to avoid conflicts
        used_names = set()
        i = 0
        
        while i < 20:  # Create 20 sample players
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            player_name = f"{first_name} {last_name} Demo {i+1}"  # Unique name with number
            
            # Check for uniqueness before adding
            if player_name not in used_names:
                used_names.add(player_name)
                team_name = random.choice(teams)
                season = "2023"
                
                # Generate realistic stats
                games_played = random.randint(65, 82)
                points_per_game = round(random.uniform(10.0, 30.0), 1)
                field_goal_percentage = round(random.uniform(0.40, 0.55), 3)
                three_point_percentage = round(random.uniform(0.30, 0.45), 3)
                free_throw_percentage = round(random.uniform(0.70, 0.95), 3)
                rebounds_per_game = round(random.uniform(4.0, 12.0), 1)
                assists_per_game = round(random.uniform(3.0, 9.0), 1)
                steals_per_game = round(random.uniform(0.5, 2.5), 1)
                blocks_per_game = round(random.uniform(0.5, 3.0), 1)
                turnovers_per_game = round(random.uniform(1.0, 4.0), 1)
                minutes_per_game = round(random.uniform(25.0, 38.0), 1)
                
                BasketballStats.objects.create(
                    player_name=player_name,
                    team_name=team_name,
                    season=season,
                    games_played=games_played,
                    points_per_game=points_per_game,
                    field_goal_percentage=field_goal_percentage,
                    three_point_percentage=three_point_percentage,
                    free_throw_percentage=free_throw_percentage,
                    rebounds_per_game=rebounds_per_game,
                    assists_per_game=assists_per_game,
                    steals_per_game=steals_per_game,
                    blocks_per_game=blocks_per_game,
                    turnovers_per_game=turnovers_per_game,
                    minutes_per_game=minutes_per_game,
                    is_demo_data=True  # Mark as demo data
                )
                i += 1

    def create_sample_football_data(self):
        """Create sample football data for demonstration"""
        # Clear existing demo data to avoid duplicates
        FootballStats.objects.filter(is_demo_data=True).delete()
        
        # Sample teams and players
        teams = ['Chiefs', 'Eagles', 'Cowboys', 'Patriots', 'Ravens', 'Bills', '49ers', 'Packers']
        first_names = ['Patrick', 'Jalen', 'Dak', 'Mac', 'Lamar', 'Josh', 'Brock', 'Aaron', 'Justin', 'Kyler']
        last_names = ['Mahomes', 'Hurts', 'Prescott', 'Jones', 'Jackson', 'Allen', 'Purdy', 'Rodgers', 'Herbert', 'Murray']
        positions = ['QB', 'RB', 'WR', 'TE', 'FB']
        
        # Generate unique player names to avoid conflicts
        used_names = set()
        i = 0
        
        while i < 20:  # Create 20 sample players
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            player_name = f"{first_name} {last_name} Demo {i+1}"  # Unique name with number
            
            # Check for uniqueness before adding
            if player_name not in used_names:
                used_names.add(player_name)
                team_name = random.choice(teams)
                position = random.choice(positions)
                season = "2023"
                
                # Generate realistic stats based on position
                games_played = random.randint(10, 17)
                
                # Generate different stats based on position
                if position == 'QB':
                    # Quarterback stats
                    passing_yards = random.randint(2000, 5000)
                    passing_touchdowns = random.randint(20, 45)
                    interceptions_thrown = random.randint(5, 15)
                    rushing_yards = random.randint(100, 500)
                    rushing_touchdowns = random.randint(0, 8)
                    receiving_yards = 0
                    receiving_touchdowns = 0
                    total_tackles = random.randint(0, 3)
                    sacks = round(random.uniform(0, 2), 1)
                    interceptions = random.randint(0, 2)
                    fumbles_recovered = random.randint(0, 2)
                elif position == 'RB':
                    # Running back stats
                    passing_yards = 0
                    passing_touchdowns = 0
                    interceptions_thrown = 0
                    rushing_yards = random.randint(800, 1800)
                    rushing_touchdowns = random.randint(5, 18)
                    receiving_yards = random.randint(100, 800)
                    receiving_touchdowns = random.randint(1, 8)
                    total_tackles = random.randint(0, 2)
                    sacks = 0
                    interceptions = 0
                    fumbles_recovered = random.randint(0, 3)
                elif position in ['WR', 'TE']:
                    # Receiver stats
                    passing_yards = 0
                    passing_touchdowns = 0
                    interceptions_thrown = 0
                    rushing_yards = random.randint(0, 100)
                    rushing_touchdowns = random.randint(0, 3)
                    receiving_yards = random.randint(400, 1500)
                    receiving_touchdowns = random.randint(2, 15)
                    total_tackles = random.randint(0, 1)
                    sacks = 0
                    interceptions = 0
                    fumbles_recovered = random.randint(0, 2)
                else:  # FB or other
                    passing_yards = random.randint(0, 50)
                    passing_touchdowns = random.randint(0, 1)
                    interceptions_thrown = random.randint(0, 1)
                    rushing_yards = random.randint(50, 300)
                    rushing_touchdowns = random.randint(1, 6)
                    receiving_yards = random.randint(50, 400)
                    receiving_touchdowns = random.randint(0, 5)
                    total_tackles = random.randint(0, 2)
                    sacks = round(random.uniform(0, 0.5), 1)
                    interceptions = random.randint(0, 1)
                    fumbles_recovered = random.randint(0, 2)
                
                FootballStats.objects.create(
                    player_name=player_name,
                    team_name=team_name,
                    position=position,
                    season=season,
                    games_played=games_played,
                    passing_yards=passing_yards,
                    passing_touchdowns=passing_touchdowns,
                    interceptions_thrown=interceptions_thrown,
                    rushing_yards=rushing_yards,
                    rushing_touchdowns=rushing_touchdowns,
                    receiving_yards=receiving_yards,
                    receiving_touchdowns=receiving_touchdowns,
                    total_tackles=total_tackles,
                    sacks=sacks,
                    interceptions=interceptions,
                    fumbles_recovered=fumbles_recovered,
                    is_demo_data=True  # Mark as demo data
                )
                i += 1