"""
Data Visualization Module
Generates visualizations for sports statistics using matplotlib
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.conf import settings
import os
from scraping.models import BasketballStats, FootballStats
import logging

# Configure matplotlib to work without GUI backend
plt.switch_backend('Agg')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportsDataVisualizer:
    def __init__(self):
        """
        Initialize the visualizer
        """
        # Set style for better-looking plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_basketball_leaderboard(self, season='2023', top_n=10):
        """
        Generate a leaderboard visualization for basketball stats
        
        Args:
            season (str): Season to visualize
            top_n (int): Number of top players to show
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            # Get data from the database
            stats_qs = BasketballStats.objects.filter(season=season)[:top_n*5]  # Get more than needed for filtering
            
            if not stats_qs.exists():
                logger.warning(f"No basketball data found for season {season}")
                return None
            
            # Convert to DataFrame
            data = []
            for stat in stats_qs:
                if stat.points_per_game is not None and stat.player_name and stat.team_name:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'points_per_game': float(stat.points_per_game),
                        'rebounds_per_game': float(stat.rebounds_per_game) if stat.rebounds_per_game else 0,
                        'assists_per_game': float(stat.assists_per_game) if stat.assists_per_game else 0,
                    })
            
            if not data:
                logger.warning("No valid data found after filtering")
                return None
                
            df = pd.DataFrame(data)
            
            # Get top performers by different categories
            top_scorers = df.nlargest(top_n, 'points_per_game')
            top_rebounders = df.nlargest(top_n, 'rebounds_per_game')
            top_assists = df.nlargest(top_n, 'assists_per_game')
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'NCAA Basketball Leaders - Season {season}', fontsize=16)
            
            # Top Scorers
            axes[0, 0].barh(range(len(top_scorers)), top_scorers['points_per_game'], color='skyblue')
            axes[0, 0].set_yticks(range(len(top_scorers)))
            axes[0, 0].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                        for _, row in top_scorers.iterrows()])
            axes[0, 0].set_xlabel('Points Per Game')
            axes[0, 0].set_title('Top Scorers')
            
            # Top Rebounders
            axes[0, 1].barh(range(len(top_rebounders)), top_rebounders['rebounds_per_game'], color='lightcoral')
            axes[0, 1].set_yticks(range(len(top_rebounders)))
            axes[0, 1].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                        for _, row in top_rebounders.iterrows()])
            axes[0, 1].set_xlabel('Rebounds Per Game')
            axes[0, 1].set_title('Top Rebounders')
            
            # Top Assists
            axes[1, 0].barh(range(len(top_assists)), top_assists['assists_per_game'], color='lightgreen')
            axes[1, 0].set_yticks(range(len(top_assists)))
            axes[1, 0].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                        for _, row in top_assists.iterrows()])
            axes[1, 0].set_xlabel('Assists Per Game')
            axes[1, 0].set_title('Top Assists')
            
            # Correlation scatter plot
            axes[1, 1].scatter(df['points_per_game'], df['rebounds_per_game'], alpha=0.6, color='purple')
            axes[1, 1].set_xlabel('Points Per Game')
            axes[1, 1].set_ylabel('Rebounds Per Game')
            axes[1, 1].set_title('Points vs Rebounds Correlation')
            
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            
            plt.close()  # Close the figure to free memory
            
            return graphic
        except Exception as e:
            logger.error(f"Error generating basketball leaderboard: {str(e)}")
            return None
    
    def generate_football_leaderboard(self, season='2023', top_n=10):
        """
        Generate a leaderboard visualization for football stats
        
        Args:
            season (str): Season to visualize
            top_n (int): Number of top players to show
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            # Get data from the database
            stats_qs = FootballStats.objects.filter(season=season)[:top_n*5]  # Get more than needed for filtering
            
            if not stats_qs.exists():
                logger.warning(f"No football data found for season {season}")
                return None
            
            # Convert to DataFrame
            data = []
            for stat in stats_qs:
                if stat.player_name and stat.team_name:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'position': stat.position or 'N/A',
                        'passing_yards': stat.passing_yards or 0,
                        'rushing_yards': stat.rushing_yards or 0,
                        'receiving_yards': stat.receiving_yards or 0,
                        'passing_touchdowns': stat.passing_touchdowns or 0,
                        'rushing_touchdowns': stat.rushing_touchdowns or 0,
                        'receiving_touchdowns': stat.receiving_touchdowns or 0,
                    })
            
            if not data:
                logger.warning("No valid data found after filtering")
                return None
                
            df = pd.DataFrame(data)
            
            # Filter for different positions based on stats
            # For quarterbacks (if they have passing yards)
            qb_df = df[df['passing_yards'] > 0].nlargest(top_n, 'passing_yards')
            # For running backs (if they have rushing yards)
            rb_df = df[df['rushing_yards'] > 0].nlargest(top_n, 'rushing_yards')
            # For receivers (if they have receiving yards)
            wr_df = df[df['receiving_yards'] > 0].nlargest(top_n, 'receiving_yards')
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'NCAA Football Leaders - Season {season}', fontsize=16)
            
            # Top Passers
            if not qb_df.empty:
                axes[0, 0].barh(range(len(qb_df)), qb_df['passing_yards'], color='skyblue')
                axes[0, 0].set_yticks(range(len(qb_df)))
                axes[0, 0].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                            for _, row in qb_df.iterrows()])
                axes[0, 0].set_xlabel('Passing Yards')
                axes[0, 0].set_title('Top Passers')
            else:
                axes[0, 0].text(0.5, 0.5, 'No passing data available', 
                                horizontalalignment='center', verticalalignment='center',
                                transform=axes[0, 0].transAxes)
                axes[0, 0].set_title('Top Passers')
            
            # Top Rushers
            if not rb_df.empty:
                axes[0, 1].barh(range(len(rb_df)), rb_df['rushing_yards'], color='lightcoral')
                axes[0, 1].set_yticks(range(len(rb_df)))
                axes[0, 1].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                            for _, row in rb_df.iterrows()])
                axes[0, 1].set_xlabel('Rushing Yards')
                axes[0, 1].set_title('Top Rushers')
            else:
                axes[0, 1].text(0.5, 0.5, 'No rushing data available', 
                                horizontalalignment='center', verticalalignment='center',
                                transform=axes[0, 1].transAxes)
                axes[0, 1].set_title('Top Rushers')
            
            # Top Receivers
            if not wr_df.empty:
                axes[1, 0].barh(range(len(wr_df)), wr_df['receiving_yards'], color='lightgreen')
                axes[1, 0].set_yticks(range(len(wr_df)))
                axes[1, 0].set_yticklabels([f"{row['player_name']} ({row['team_name']})" 
                                            for _, row in wr_df.iterrows()])
                axes[1, 0].set_xlabel('Receiving Yards')
                axes[1, 0].set_title('Top Receivers')
            else:
                axes[1, 0].text(0.5, 0.5, 'No receiving data available', 
                                horizontalalignment='center', verticalalignment='center',
                                transform=axes[1, 0].transAxes)
                axes[1, 0].set_title('Top Receivers')
            
            # Touchdown comparison
            axes[1, 1].plot(range(len(df[:top_n])), df[:top_n]['passing_touchdowns'], label='Passing TDs', marker='o')
            axes[1, 1].plot(range(len(df[:top_n])), df[:top_n]['rushing_touchdowns'], label='Rushing TDs', marker='s')
            axes[1, 1].plot(range(len(df[:top_n])), df[:top_n]['receiving_touchdowns'], label='Receiving TDs', marker='^')
            axes[1, 1].set_xlabel('Player Index')
            axes[1, 1].set_ylabel('Touchdowns')
            axes[1, 1].set_title('Touchdown Comparison')
            axes[1, 1].legend()
            
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            
            plt.close()  # Close the figure to free memory
            
            return graphic
        except Exception as e:
            logger.error(f"Error generating football leaderboard: {str(e)}")
            return None
    
    def generate_trend_analysis(self, sport='basketball', season='2023'):
        """
        Generate trend analysis visualization
        
        Args:
            sport (str): Sport to analyze ('basketball' or 'football')
            season (str): Season to analyze
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            if sport.lower() == 'basketball':
                stats_qs = BasketballStats.objects.filter(season=season)
                
                if not stats_qs.exists():
                    logger.warning(f"No basketball data found for season {season}")
                    return None
                
                # Convert to DataFrame
                data = []
                for stat in stats_qs:
                    if stat.points_per_game is not None:
                        data.append({
                            'player_name': stat.player_name,
                            'team_name': stat.team_name,
                            'points_per_game': float(stat.points_per_game),
                            'rebounds_per_game': float(stat.rebounds_per_game) if stat.rebounds_per_game else 0,
                            'assists_per_game': float(stat.assists_per_game) if stat.assists_per_game else 0,
                        })
                
                if not data:
                    return None
                    
                df = pd.DataFrame(data)
                
                # Create trend analysis
                fig, axes = plt.subplots(1, 2, figsize=(15, 6))
                fig.suptitle(f'{sport.capitalize()} Trend Analysis - Season {season}', fontsize=16)
                
                # Points vs Rebounds scatter
                axes[0].scatter(df['points_per_game'], df['rebounds_per_game'], alpha=0.6, color='blue')
                axes[0].set_xlabel('Points Per Game')
                axes[0].set_ylabel('Rebounds Per Game')
                axes[0].set_title('Points vs Rebounds')
                
                # Distribution of points
                axes[1].hist(df['points_per_game'], bins=20, color='skyblue', edgecolor='black')
                axes[1].set_xlabel('Points Per Game')
                axes[1].set_ylabel('Frequency')
                axes[1].set_title('Distribution of Points Per Game')
                
            elif sport.lower() == 'football':
                stats_qs = FootballStats.objects.filter(season=season)
                
                if not stats_qs.exists():
                    logger.warning(f"No football data found for season {season}")
                    return None
                
                # Convert to DataFrame
                data = []
                for stat in stats_qs:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'position': stat.position or 'N/A',
                        'passing_yards': stat.passing_yards or 0,
                        'rushing_yards': stat.rushing_yards or 0,
                        'receiving_yards': stat.receiving_yards or 0,
                    })
                
                if not data:
                    return None
                    
                df = pd.DataFrame(data)
                
                # Create trend analysis
                fig, axes = plt.subplots(1, 2, figsize=(15, 6))
                fig.suptitle(f'{sport.capitalize()} Trend Analysis - Season {season}', fontsize=16)
                
                # Yards comparison
                x_pos = range(len(df[:20]))  # Only show top 20 players
                width = 0.25
                
                if len(df) > 0:
                    axes[0].bar([i - width for i in x_pos], df[:20]['passing_yards'], width, label='Passing Yards', alpha=0.8)
                    axes[0].bar([i for i in x_pos], df[:20]['rushing_yards'], width, label='Rushing Yards', alpha=0.8)
                    axes[0].bar([i + width for i in x_pos], df[:20]['receiving_yards'], width, label='Receiving Yards', alpha=0.8)
                    
                    # Set x-axis labels
                    axes[0].set_xticks(x_pos)
                    axes[0].set_xticklabels([row['player_name'][:10] for _, row in df[:20].iterrows()], rotation=45, ha='right')
                    axes[0].set_xlabel('Players')
                    axes[0].set_ylabel('Yards')
                    axes[0].set_title('Yards Comparison')
                    axes[0].legend()
                
                # Distribution of total yards
                df['total_yards'] = df['passing_yards'] + df['rushing_yards'] + df['receiving_yards']
                axes[1].hist(df['total_yards'], bins=20, color='lightgreen', edgecolor='black')
                axes[1].set_xlabel('Total Yards')
                axes[1].set_ylabel('Frequency')
                axes[1].set_title('Distribution of Total Yards')
            
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')
            
            plt.close()  # Close the figure to free memory
            
            return graphic
        except Exception as e:
            logger.error(f"Error generating {sport} trend analysis: {str(e)}")
            return None

def get_visualization_data(sport='basketball', season='2023', chart_type='leaderboard'):
    """
    Helper function to get visualization data
    
    Args:
        sport (str): Sport to visualize
        season (str): Season to visualize
        chart_type (str): Type of chart ('leaderboard' or 'trend')
        
    Returns:
        str: Base64 encoded image string
    """
    visualizer = SportsDataVisualizer()
    
    if chart_type == 'leaderboard':
        if sport.lower() == 'basketball':
            return visualizer.generate_basketball_leaderboard(season=season, top_n=10)
        elif sport.lower() == 'football':
            return visualizer.generate_football_leaderboard(season=season, top_n=10)
    elif chart_type == 'trend':
        return visualizer.generate_trend_analysis(sport=sport, season=season)
    
    return None