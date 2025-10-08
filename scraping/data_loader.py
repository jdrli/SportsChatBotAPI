"""
Data Loader Module
Handles loading of processed data into PostgreSQL database using SQLAlchemy
"""
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class SportsDataLoader:
    def __init__(self, db_connection_string: str):
        """
        Initialize the data loader with database connection
        
        Args:
            db_connection_string (str): PostgreSQL database connection string
        """
        self.engine = create_engine(db_connection_string)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        self.create_tables()
    
    def create_tables(self):
        """
        Create all required tables in the database
        """
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created/verified")
    
    def load_dataframe_to_table(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """
        Load a pandas DataFrame to a database table
        
        Args:
            df (pandas.DataFrame): DataFrame to load
            table_name (str): Target table name
            if_exists (str): What to do if table exists ('fail', 'replace', 'append')
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False, method='multi')
            logger.info(f"Loaded {len(df)} records into {table_name}")
        except Exception as e:
            logger.error(f"Error loading DataFrame to {table_name}: {str(e)}")
            raise
    
    def load_ncaa_basketball_stats(self, df: pd.DataFrame, season: str = "2023"):
        """
        Load NCAA basketball statistics to the appropriate table
        
        Args:
            df (pandas.DataFrame): DataFrame with basketball stats
            season (str): Season identifier
        """
        table_name = f"ncaa_basketball_stats_{season}"
        
        # Define expected columns for basketball stats
        expected_cols = [
            'player_name', 'team_name', 'games_played', 'points_per_game',
            'field_goals_made', 'field_goals_attempted', 'free_throws_made',
            'free_throws_attempted', 'three_pointers_made', 'three_pointers_attempted',
            'rebounds_per_game', 'assists_per_game', 'steals_per_game',
            'blocks_per_game', 'turnovers_per_game'
        ]
        
        # Ensure DataFrame has expected structure
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None  # Add missing columns with null values
        
        # Select only the expected columns
        df = df[expected_cols]
        
        self.load_dataframe_to_table(df, table_name)
    
    def load_ncaa_football_stats(self, df: pd.DataFrame, season: str = "2023"):
        """
        Load NCAA football statistics to the appropriate table
        
        Args:
            df (pandas.DataFrame): DataFrame with football stats
            season (str): Season identifier
        """
        table_name = f"ncaa_football_stats_{season}"
        
        # Define expected columns for football stats
        expected_cols = [
            'player_name', 'team_name', 'position', 'games_played', 'passing_yards',
            'passing_touchdowns', 'interceptions_thrown', 'rushing_yards', 'rushing_touchdowns',
            'receiving_yards', 'receiving_touchdowns', 'total_tackles', 'sacks', 'fumbles_recovered'
        ]
        
        # Ensure DataFrame has expected structure
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None  # Add missing columns with null values
        
        # Select only the expected columns
        df = df[expected_cols]
        
        self.load_dataframe_to_table(df, table_name)

# Define specific table models for different sports data
class BasketballStats(Base):
    __tablename__ = 'ncaa_basketball_player_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String(200), nullable=False)
    team_name = Column(String(100), nullable=False)
    season = Column(String(9), nullable=False)  # e.g., "2023-24"
    games_played = Column(Integer)
    points_per_game = Column(Float)
    field_goal_percentage = Column(Float)
    three_point_percentage = Column(Float)
    free_throw_percentage = Column(Float)
    rebounds_per_game = Column(Float)
    assists_per_game = Column(Float)
    steals_per_game = Column(Float)
    blocks_per_game = Column(Float)
    turnovers_per_game = Column(Float)
    minutes_per_game = Column(Float)
    created_at = Column(DateTime, default=lambda: pd.Timestamp.now())

class FootballStats(Base):
    __tablename__ = 'ncaa_football_player_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String(200), nullable=False)
    team_name = Column(String(100), nullable=False)
    position = Column(String(10), nullable=True)  # QB, RB, WR, etc.
    season = Column(String(9), nullable=False)  # e.g., "2023-24"
    games_played = Column(Integer)
    passing_yards = Column(Integer)
    passing_touchdowns = Column(Integer)
    interceptions_thrown = Column(Integer)
    rushing_yards = Column(Integer)
    rushing_touchdowns = Column(Integer)
    receiving_yards = Column(Integer)
    receiving_touchdowns = Column(Integer)
    total_tackles = Column(Integer)
    sacks = Column(Float)
    interceptions = Column(Integer)
    fumbles_recovered = Column(Integer)
    created_at = Column(DateTime, default=lambda: pd.Timestamp.now())

class Team(Base):
    __tablename__ = 'ncaa_teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(200), nullable=False, unique=True)
    conference = Column(String(100), nullable=True)
    division = Column(String(50), nullable=True)  # D1, D2, D3
    sport = Column(String(50), nullable=False)  # basketball, football
    location = Column(String(200), nullable=True)
    established_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: pd.Timestamp.now())

class Game(Base):
    __tablename__ = 'ncaa_games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(String(9), nullable=False)
    date = Column(DateTime, nullable=False)
    home_team_id = Column(Integer, nullable=False)  # Foreign key to teams
    away_team_id = Column(Integer, nullable=False)  # Foreign key to teams
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    venue = Column(String(200), nullable=True)
    attendance = Column(Integer, nullable=True)
    is_postseason = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: pd.Timestamp.now())

def load_processed_data_to_db(df: pd.DataFrame, table_type: str, db_connection_string: str, season: str = "2023"):
    """
    Convenience function to load processed data to database
    
    Args:
        df (pandas.DataFrame): Processed DataFrame to load
        table_type (str): Type of data ('basketball_stats', 'football_stats', etc.)
        db_connection_string (str): PostgreSQL database connection string
        season (str): Season identifier
        
    Returns:
        bool: Success status
    """
    loader = SportsDataLoader(db_connection_string)
    
    try:
        if table_type == 'basketball_stats':
            loader.load_ncaa_basketball_stats(df, season)
        elif table_type == 'football_stats':
            loader.load_ncaa_football_stats(df, season)
        else:
            # Generic loading for other table types
            table_name = f"ncaa_{table_type}_{season}"
            loader.load_dataframe_to_table(df, table_name)
        
        logger.info(f"Successfully loaded {len(df)} records to {table_type} table")
        return True
    except Exception as e:
        logger.error(f"Error loading data to database: {str(e)}")
        return False

# Example usage
def example_data_loading():
    """
    Example of how to use the data loader
    """
    # Sample connection string - adjust for your PostgreSQL setup
    db_connection_string = "postgresql://username:password@localhost:5432/sportsdb"
    
    # Create loader instance
    loader = SportsDataLoader(db_connection_string)
    
    # Example DataFrame (in practice, this would come from the scraping/transform process)
    sample_data = pd.DataFrame({
        'player_name': ['Player 1', 'Player 2', 'Player 3'],
        'team_name': ['Team A', 'Team B', 'Team C'],
        'games_played': [10, 12, 8],
        'points_per_game': [15.2, 18.7, 12.5]
    })
    
    # Load the data
    loader.load_ncaa_basketball_stats(sample_data, season="2023")
    
    logger.info("Example data loading completed")

if __name__ == "__main__":
    example_data_loading()