import logging

from django.test import RequestFactory
from oauth2_provider.decorators import protected_resource
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.constants import CUSTOM_GOODBYE
from greetings.utils.services import GreetingService, RecursiveViewService
from greetings.utils.validators import GreetingPathValidator


logger = logging.getLogger(__name__)


@api_view(["GET"])
@protected_resource(scopes=["read"])
def list_greetings(request: Request) -> Response:
    """List all the greetings from the db."""

    greetings = Greeting.objects.all()
    serializer = GreetingSerializer(greetings, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@protected_resource(scopes=["write"])
def save_custom_greeting(request: Request) -> Response:
    """Save a custom greeting from a user."""

    try:
        custom_greeting = validate_query_param(request)
        if custom_greeting == CUSTOM_GOODBYE:
            return custom_greeting_response(custom_greeting, request)

        GreetingService.create_and_save(custom_greeting)
        return RecursiveViewService.make_recursive_call(custom_greeting, request)

    except Exception as exc:
        logger.warning("Error on saving custom greeting!", exc_info=exc)
        return custom_error_response(exc)  


def validate_query_param(request: Request) -> str:
    GreetingPathValidator.validate_param_key_present(request)
    custom_greeting = request.query_params["greeting"]
    return custom_greeting


def custom_greeting_response(custom_greeting, request) -> Response:
    return Response(
        {
            "status_code": status.HTTP_201_CREATED,
            "message": "Success",
            "description": "Saved custom greeting from user.",
            "greeting": custom_greeting,
            "goodbye": request.query_params["greeting"],
        },
        status=status.HTTP_201_CREATED,
    )


def custom_error_response(exception: Exception) -> Response:
  return Response(
      {
          "status_code": status.HTTP_400_BAD_REQUEST,
          "message": "error",
          "description": "Failed to save custom greeting from user.",
      },
      status=status.HTTP_400_BAD_REQUEST,
      exception=exception,
  )
