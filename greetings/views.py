import base64
import logging
import os

import environ
import requests
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory
from oauth2_provider.decorators import protected_resource
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from config.settings.base import BASE_DIR
from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.services import GreetingService
from greetings.utils.validators import GreetingPathValidator

CUSTOM_GOODBYE: str = "Kwaheri"

logger = logging.getLogger(__name__)
factory = RequestFactory()


@api_view(["GET"])
@protected_resource(scopes=['read'])
def list_greetings(request: Request) -> Response:
    """List all the greetings from the db."""
    if request.method == "GET":
        greetings = Greeting.objects.all()
        serializer = GreetingSerializer(greetings, many=True)
        return Response(serializer.data)

    return Response(serializer.errors)


@api_view(["POST"])
@protected_resource(scopes=['write'])
def save_custom_greeting(request: Request) -> Response:
    """Save a custom greeting from a user."""

    try:
        custom_greeting = validate_query_param(request)
        if custom_greeting == CUSTOM_GOODBYE:
            return custom_greeting_response(custom_greeting, request)

        GreetingService.create_and_save(custom_greeting)
        return try_make_recursive_call(custom_greeting, request)

    except Exception as exc:
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "error",
                "description": "Failed to save custom greeting from user.",
            },
            status=status.HTTP_400_BAD_REQUEST,
            exception=exc,
        )


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


def try_make_recursive_call(initial_param: str, initial_request: Request) -> None:
    # Logic to get token and make authorized request
    ## load_env_credentials()
    ## encode_credentials()  
    ## request_access_token()  

    
    request = update_request_query_param(initial_param, initial_request)
    logger.debug("recursive call to api_view: views.save_custom_greeting.")
    return save_custom_greeting(request)


def load_env_credentials() -> tuple[str]:
  client_id, client_secret = load_envs()
  
  if not is_credentials_set(client_id, client_secret):
    environ.Env.read_env(os.path.join(BASE_DIR, ".envs", "credentials.env"))
    client_id, client_secret = load_envs()

  if not is_credentials_set(client_id, client_secret):
    raise ImproperlyConfigured('Client credentials not found on host machine or env file.')

  return {'CLIENT_ID': client_id, 'CLIENT_SECRET': client_secret}

def load_envs() -> str:
  client_id = os.environ.get('CLIENT_ID', None)
  client_secret = os.environ.get('CLIENT_SECRET', None)
  return client_id, client_secret

def is_credentials_set(id: str, secret: str) -> bool:
  return id is not None and secret is not None

def encode_credentials(client_id: str, client_secret: str) -> str:
  credential = f'{client_id}:{client_secret}'
  encoded_credential = base64.b64encode(credential.encode('utf-8'))
  return encoded_credential.decode()

def request_access_token(encoded_credential: str) -> Response:

  response = requests.post(
    url='http://127.0.0.1:8000/o/token/',
    headers={
      'Content-Type': 'application/x-www-form-urlencoded', 
      'Cache-Control': 'no-cache',
      'Authorization': f'Basic {encoded_credential}'
    },
    data={'grant_type': 'client_credentials'},
    timeout=10
  )
  return response

def update_request_query_param(
    initial_param: str, initial_request: Request
) -> WSGIRequest:
    path: str = initial_request.build_absolute_uri()
    updated_path = path.replace(f"={initial_param}", f"={CUSTOM_GOODBYE}", 1)
    return factory.post(path=updated_path)
