from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import ChatSession, ChatMessage
from .visualizations import get_visualization_data
from scraping.models import BasketballStats, FootballStats, ScrapedData
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
import uuid
import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Llama2LLM:
    """
    Wrapper for Meta's Llama 2 model
    For now, using OpenAI compatible interface as placeholder
    In a real implementation, you would connect to Meta's Llama 2 API
    """
    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")  # Using OpenAI as placeholder
            
        if not api_key:
            raise ImproperlyConfigured("API key is required for LLM")
            
        # In real implementation, this would connect to Meta's Llama 2
        # For now, using OpenAI as a placeholder
        self.llm = OpenAI(api_token=api_key)
    
    def query(self, df, prompt):
        """
        Query the LLM with a DataFrame and prompt
        """
        try:
            smart_df = SmartDataframe(df, config={"llm": self.llm, "enable_cache": False})
            result = smart_df.chat(prompt)
            return result
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            return f"Error processing your request: {str(e)}"

@api_view(["POST"])
def chatbot(request):
    """
    Main chatbot endpoint that processes user queries about sports data
    """
    try:
        user_message = request.data.get('message', '')
        session_id = request.data.get('session_id', None)
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or retrieve chat session
        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id)
        else:
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                return Response({"error": "Invalid session"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save user message
        user_chat_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Process the user query using PandasAI with sports data
        response = process_sports_query(user_message)
        
        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response
        )
        
        return Response({
            "response": response,
            "session_id": session_id,
            "message_id": assistant_message.id
        })
        
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def process_sports_query(query):
    """
    Process a sports-related query using PandasAI and available data
    """
    try:
        # Identify the type of query and load relevant data
        query_lower = query.lower()
        
        # For demonstration, we'll load some sample data
        # In a real implementation, you would analyze the query to determine 
        # which data tables to load
        
        # Check if query is about basketball
        if any(term in query_lower for term in ['basketball', 'nba', 'points', 'rebounds', 'assists', 'player', 'team']):
            # Load basketball stats data
            basketball_qs = BasketballStats.objects.all()[:100]  # Limit to 100 records for performance
            
            if basketball_qs.exists():
                # Convert to DataFrame
                data = []
                for stat in basketball_qs:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'season': stat.season,
                        'games_played': stat.games_played,
                        'points_per_game': float(stat.points_per_game) if stat.points_per_game else 0,
                        'field_goal_percentage': float(stat.field_goal_percentage) if stat.field_goal_percentage else 0,
                        'three_point_percentage': float(stat.three_point_percentage) if stat.three_point_percentage else 0,
                        'free_throw_percentage': float(stat.free_throw_percentage) if stat.free_throw_percentage else 0,
                        'rebounds_per_game': float(stat.rebounds_per_game) if stat.rebounds_per_game else 0,
                        'assists_per_game': float(stat.assists_per_game) if stat.assists_per_game else 0,
                    })
                
                df = pd.DataFrame(data)
                
                # Initialize PandasAI with LLM
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    # For demo purposes, return a simple response if no API key
                    return "I can analyze basketball statistics. Please provide your query about basketball data."
                
                llm_wrapper = Llama2LLM(api_key=api_key)
                result = llm_wrapper.query(df, query)
                
                return str(result) if result else "I couldn't process your request. Please try rephrasing."
            else:
                return "No basketball data available in the database."
        
        # Check if query is about football
        elif any(term in query_lower for term in ['football', 'nfl', 'yards', 'touchdowns', 'passing', 'rushing', 'player', 'team']):
            # Load football stats data
            football_qs = FootballStats.objects.all()[:100]  # Limit to 100 records for performance
            
            if football_qs.exists():
                # Convert to DataFrame
                data = []
                for stat in football_qs:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'position': stat.position,
                        'season': stat.season,
                        'games_played': stat.games_played,
                        'passing_yards': stat.passing_yards or 0,
                        'passing_touchdowns': stat.passing_touchdowns or 0,
                        'rushing_yards': stat.rushing_yards or 0,
                        'rushing_touchdowns': stat.rushing_touchdowns or 0,
                        'receiving_yards': stat.receiving_yards or 0,
                        'receiving_touchdowns': stat.receiving_touchdowns or 0,
                        'total_tackles': stat.total_tackles or 0,
                        'sacks': float(stat.sacks) if stat.sacks else 0,
                        'interceptions': stat.interceptions or 0,
                    })
                
                df = pd.DataFrame(data)
                
                # Initialize PandasAI with LLM
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    # For demo purposes, return a simple response if no API key
                    return "I can analyze football statistics. Please provide your query about football data."
                
                llm_wrapper = Llama2LLM(api_key=api_key)
                result = llm_wrapper.query(df, query)
                
                return str(result) if result else "I couldn't process your request. Please try rephrasing."
            else:
                return "No football data available in the database."
        
        else:
            # General query - return a helpful response
            return f"I can help you analyze sports statistics. Your query was: '{query}'. Please be more specific about basketball or football statistics."
    
    except Exception as e:
        logger.error(f"Error processing sports query: {str(e)}")
        return f"Error processing your request: {str(e)}"

@api_view(["GET"])
def get_chat_history(request, session_id):
    """
    Get chat history for a specific session
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all().order_by('timestamp')
        
        history = []
        for msg in messages:
            history.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return Response({
            "session_id": session_id,
            "messages": history
        })
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET", "POST"])
def start_chat_session(request):
    """
    Start a new chat session
    """
    try:
        session = ChatSession.objects.create()
        return Response({
            "session_id": session.session_id,
            "message": "New chat session started"
        })
    except Exception as e:
        logger.error(f"Error starting chat session: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def analyze_data(request):
    """
    Endpoint for specialized data analysis
    """
    try:
        analysis_type = request.GET.get('type', 'basketball')
        season = request.GET.get('season', '2023')
        
        if analysis_type.lower() == 'basketball':
            # Load basketball data for analysis
            basketball_qs = BasketballStats.objects.filter(season=season)
            
            if basketball_qs.exists():
                data = []
                for stat in basketball_qs:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'points_per_game': float(stat.points_per_game) if stat.points_per_game else 0,
                        'rebounds_per_game': float(stat.rebounds_per_game) if stat.rebounds_per_game else 0,
                        'assists_per_game': float(stat.assists_per_game) if stat.assists_per_game else 0,
                    })
                
                df = pd.DataFrame(data)
                
                # Perform analysis based on request parameters
                analysis = {
                    'total_players': len(df),
                    'avg_points': float(df['points_per_game'].mean()),
                    'top_scorer': df.loc[df['points_per_game'].idxmax()]['player_name'] if not df.empty else 'None',
                    'top_rebounder': df.loc[df['rebounds_per_game'].idxmax()]['player_name'] if not df.empty else 'None',
                    'top_assist': df.loc[df['assists_per_game'].idxmax()]['player_name'] if not df.empty else 'None',
                }
                
                return Response(analysis)
            else:
                return Response({"message": f"No basketball data for season {season}"})
        
        elif analysis_type.lower() == 'football':
            # Load football data for analysis
            football_qs = FootballStats.objects.filter(season=season)
            
            if football_qs.exists():
                data = []
                for stat in football_qs:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'position': stat.position,
                        'passing_yards': stat.passing_yards or 0,
                        'rushing_yards': stat.rushing_yards or 0,
                        'receiving_yards': stat.receiving_yards or 0,
                    })
                
                df = pd.DataFrame(data)
                
                # Perform analysis based on request parameters
                analysis = {
                    'total_players': len(df),
                    'total_passing_yards': int(df['passing_yards'].sum()),
                    'total_rushing_yards': int(df['rushing_yards'].sum()),
                    'top_passer': df.loc[df['passing_yards'].idxmax()]['player_name'] if not df.empty and df['passing_yards'].max() > 0 else 'None',
                    'top_rusher': df.loc[df['rushing_yards'].idxmax()]['player_name'] if not df.empty and df['rushing_yards'].max() > 0 else 'None',
                }
                
                return Response(analysis)
            else:
                return Response({"message": f"No football data for season {season}"})
        else:
            return Response({"error": "Invalid analysis type"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in data analysis: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_visualization(request):
    """
    Endpoint to generate visualizations for sports data
    """
    try:
        sport = request.GET.get('sport', 'basketball')
        season = request.GET.get('season', '2023')
        chart_type = request.GET.get('chart_type', 'leaderboard')
        
        # Generate the visualization
        image_data = get_visualization_data(sport=sport, season=season, chart_type=chart_type)
        
        if image_data:
            return Response({
                "image": f"data:image/png;base64,{image_data}",
                "sport": sport,
                "season": season,
                "chart_type": chart_type
            })
        else:
            return Response({
                "error": f"Could not generate visualization for {sport} {chart_type} chart for season {season}"
            }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_sports_trends(request):
    """
    Endpoint to get sports trends and insights
    """
    try:
        sport = request.GET.get('sport', 'basketball')
        season = request.GET.get('season', '2023')
        
        # Generate trend visualization
        trend_image = get_visualization_data(sport=sport, season=season, chart_type='trend')
        
        # Get basic analysis
        if sport.lower() == 'basketball':
            stats_qs = BasketballStats.objects.filter(season=season)
        elif sport.lower() == 'football':
            stats_qs = FootballStats.objects.filter(season=season)
        else:
            return Response({"error": "Invalid sport"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not stats_qs.exists():
            return Response({
                "message": f"No data available for {sport} season {season}",
                "trend_image": None
            })
        
        # Convert to DataFrame for analysis
        data = []
        if sport.lower() == 'basketball':
            for stat in stats_qs:
                if stat.points_per_game is not None:
                    data.append({
                        'player_name': stat.player_name,
                        'team_name': stat.team_name,
                        'points_per_game': float(stat.points_per_game),
                        'rebounds_per_game': float(stat.rebounds_per_game) if stat.rebounds_per_game else 0,
                        'assists_per_game': float(stat.assists_per_game) if stat.assists_per_game else 0,
                    })
        elif sport.lower() == 'football':
            for stat in stats_qs:
                data.append({
                    'player_name': stat.player_name,
                    'team_name': stat.team_name,
                    'position': stat.position or 'N/A',
                    'passing_yards': stat.passing_yards or 0,
                    'rushing_yards': stat.rushing_yards or 0,
                    'receiving_yards': stat.receiving_yards or 0,
                })
        
        if data:
            df = pd.DataFrame(data)
            
            # Calculate some general trends
            avg_values = df.select_dtypes(include=['number']).mean().to_dict()
            
            # Identify top performers
            if sport.lower() == 'basketball':
                top_performers = {
                    'highest_scorer': df.loc[df['points_per_game'].idxmax()]['player_name'] if 'points_per_game' in df.columns and not df.empty else 'N/A',
                    'best_rebounder': df.loc[df['rebounds_per_game'].idxmax()]['player_name'] if 'rebounds_per_game' in df.columns and not df.empty else 'N/A',
                    'best_assist': df.loc[df['assists_per_game'].idxmax()]['player_name'] if 'assists_per_game' in df.columns and not df.empty else 'N/A',
                }
            elif sport.lower() == 'football':
                top_performers = {
                    'top_passer': df.loc[df['passing_yards'].idxmax()]['player_name'] if 'passing_yards' in df.columns and not df.empty and df['passing_yards'].max() > 0 else 'N/A',
                    'top_rusher': df.loc[df['rushing_yards'].idxmax()]['player_name'] if 'rushing_yards' in df.columns and not df.empty and df['rushing_yards'].max() > 0 else 'N/A',
                    'top_receiver': df.loc[df['receiving_yards'].idxmax()]['player_name'] if 'receiving_yards' in df.columns and not df.empty and df['receiving_yards'].max() > 0 else 'N/A',
                }
            
            trends_analysis = {
                'total_players': len(df),
                'avg_values': avg_values,
                'top_performers': top_performers
            }
        else:
            trends_analysis = {
                'total_players': 0,
                'avg_values': {},
                'top_performers': {}
            }
        
        response_data = {
            "sport": sport,
            "season": season,
            "trends_analysis": trends_analysis,
            "trend_image": f"data:image/png;base64,{trend_image}" if trend_image else None
        }
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting sports trends: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

