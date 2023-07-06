from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer


@api_view(["GET"])
def list_greetings(request):
    """List all the greetings from the db."""

    if request.method == "GET":
        greetings = Greeting.objects.all()
        serializer = GreetingSerializer(greetings, many=True)
        return Response(serializer.data)

    return Response(serializer.errors)


@api_view(["POST"])
def save_custom_greeting(request):
    """Save a custom greeting from a user."""

    if not is_query_param_present(request=request):
      raise ValueError("Greeting query param is missing.")

    custom_greeting = request.GET.get("greeting")

    if custom_greeting:
        greeting = Greeting(greeting_text=custom_greeting)
        greeting.save()
        return Response(
            {"message": "Greeting saved"}, status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "Invalid greeting"}, status=status.HTTP_400_BAD_REQUEST
    )

def is_query_param_present(request) -> bool:
  query_param = '?greeting='
  url_path = request.META.get("PATH_INFO")
  return query_param in url_path
