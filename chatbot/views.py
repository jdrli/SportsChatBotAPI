from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def chatbot(request):
    print("Chatbot is running...")
    return Response({"message": "Chatbot ran successfully!"})

