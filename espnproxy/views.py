from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .espn_api import fetch_nba_stats

@api_view(["GET"])
def espnproxy(request):
    print("ESPN Proxy is running...")
    fetch_nba_data()
    return Response({"message": "ESPN Proxy ran successfully!"})

@require_GET
def fetch_nba_data_view(request):
    try:
        fetch_nba_stats()
        return JsonResponse({"status": "success", "message": "NBA stats fetched and stored."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
