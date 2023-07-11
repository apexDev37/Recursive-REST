import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.test import RequestFactory

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.validators import * 

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

  custom_greeting = validate_query_param(request)
  logger.debug(f'user passed query_param value: {custom_greeting}')
  if custom_greeting == 'Kwaheri':
    logger.debug(f'FINAL response')
    return Response(
      {
        "status_code": status.HTTP_201_CREATED,
        "message": "Success",
        "description": "Saved custom greeting from user.",
        "greeting": custom_greeting,
        "goodbye": request.query_params['greeting'],
      }, 
      status=status.HTTP_201_CREATED)    

  try:    
    greeting = Greeting(greeting_text=custom_greeting)
    greeting.save()
    logger.info(f'Save custom greeting "{greeting.greeting_text}" from user.')
        
    # Logic for making a cloned request with different param
    custom_goodbye = 'Kwaheri'
    path: str = request.build_absolute_uri()
    logger.debug(f'Path for initial request: {path}.')
    path = path.replace(f'={custom_greeting}', f'={custom_goodbye}', 1)
    recursive_request = factory.post(path=path)
    
    logger.debug(f'Path for recursive request: {path}.')
    logger.debug(f'Initial request query_param value: {request.query_params["greeting"]}.')
    logger.debug(f'Recursive request query_param value: {recursive_request.META["QUERY_STRING"]}.')
    
    logger.debug('recursive call to api_view: views.save_custom_greeting.')
    return save_custom_greeting(recursive_request)

  except Exception:
    return Response(
      {"error": "Invalid greeting"}, status=status.HTTP_400_BAD_REQUEST)  

def validate_query_param(request: Request) -> str:
  GreetingPathValidator.validate_param_key_present(request)
  custom_greeting = request.query_params['greeting']
  GreetingParamValidator.validate_not_blank(custom_greeting)
  GreetingValueValidator.validate_param_value(custom_greeting)
  return custom_greeting
  