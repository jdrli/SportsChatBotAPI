from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def run_scraper(request):
    print("Scraper is running...")
    return Response({"message": "Scraper run successfully!"})