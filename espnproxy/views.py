from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def espnproxy(request):
    print("ESPN Proxy is running...")
    return Response({"message": "ESPN Proxy ran successfully!"})
