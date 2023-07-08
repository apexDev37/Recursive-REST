from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.validators import * 

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

  custom_greeting = validate_query_param(request)

  try:    
    greeting = Greeting(greeting_text=custom_greeting)
    greeting.save()
    return Response(
      {"message": "Greeting saved"}, status=status.HTTP_201_CREATED)

  except Exception:
    return Response(
      {"error": "Invalid greeting"}, status=status.HTTP_400_BAD_REQUEST)


def validate_query_param(request: Request) -> str:
  GreetingPathValidator.validate_param_key_present(request)
  custom_greeting = request.query_params['greeting']
  GreetingParamValidator.validate_not_blank(custom_greeting)
  GreetingValueValidator.validate_param_value(custom_greeting)
  return custom_greeting
  