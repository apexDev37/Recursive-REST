from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer


@api_view(["GET"])
def list_greetings(request: Request) -> Response:
    """List all the greetings from the db."""

    if request.method == "GET":
        greetings = Greeting.objects.all()
        serializer = GreetingSerializer(greetings, many=True)
        return Response(serializer.data)

    return Response(serializer.errors)


@api_view(["POST"])
def save_custom_greeting(request: Request) -> Response:
    """Save a custom greeting from a user."""

    GreetingPathValidator.validate_query_param_present(request)
    custom_greeting = request.query_params['greeting']

    if custom_greeting:
        greeting = Greeting(greeting_text=custom_greeting)
        greeting.save()
        return Response(
            {"message": "Greeting saved"}, status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "Invalid greeting"}, status=status.HTTP_400_BAD_REQUEST
    )

class GreetingPathValidator:
  @staticmethod
  def validate_query_param_present(request: Request) -> None:
    query_param_key = '?greeting='
    url_path = request.build_absolute_uri()
    if query_param_key not in url_path:
      raise ValueError("Greeting query param key is missing.")
