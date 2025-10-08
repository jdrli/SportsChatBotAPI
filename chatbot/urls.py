from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chatbot, name='chatbot'),
    path('session/', views.start_chat_session, name='start-chat-session'),
    path('session/<str:session_id>/', views.get_chat_history, name='chat-history'),
    path('analyze/', views.analyze_data, name='analyze-data'),
    path('visualize/', views.get_visualization, name='get-visualization'),
    path('trends/', views.get_sports_trends, name='get-sports-trends'),
]
