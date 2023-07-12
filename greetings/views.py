import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.validators import * 

CUSTOM_GOODBYE: str = 'Kwaheri'

logger = logging.getLogger(__name__)
factory = RequestFactory()

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
    
  try:            
    custom_greeting = validate_query_param(request)
    if custom_greeting == CUSTOM_GOODBYE:
      return custom_greeting_response(custom_greeting, request)

    try_create_and_save(custom_greeting)    
    return try_make_recursive_call(custom_greeting, request)

  except Exception as exc:
    return Response({
    "status_code": status.HTTP_400_BAD_REQUEST,
    "message": "error",
    "description": "Failed to save custom greeting from user.",
    }, status=status.HTTP_400_BAD_REQUEST, exception=exc)  


def validate_query_param(request: Request) -> str:
  GreetingPathValidator.validate_param_key_present(request)
  custom_greeting = request.query_params['greeting']
  GreetingParamValidator.validate_not_blank(custom_greeting)
  GreetingValueValidator.validate_param_value(custom_greeting)
  return custom_greeting


def custom_greeting_response(custom_greeting, request) -> Response:
  return Response({
    "status_code": status.HTTP_201_CREATED,
    "message": "Success",
    "description": "Saved custom greeting from user.",
    "greeting": custom_greeting,
    "goodbye": request.query_params['greeting'],
  }, status=status.HTTP_201_CREATED)    


def try_create_and_save(greeting: str) -> None:
  greeting = Greeting(greeting_text=greeting)
  greeting.save()
  logger.info(f'Save custom greeting "{greeting.greeting_text}" from user.')


def try_make_recursive_call(initial_param: str, initial_request: Request) -> None:
  request = update_request_query_param(initial_param, initial_request)
  logger.debug('recursive call to api_view: views.save_custom_greeting.')
  return save_custom_greeting(request)


def update_request_query_param(initial_param: str, initial_request: Request) -> WSGIRequest:
  path: str = initial_request.build_absolute_uri()
  updated_path = path.replace(f'={initial_param}', f'={CUSTOM_GOODBYE}', 1)
  return factory.post(path=updated_path)
