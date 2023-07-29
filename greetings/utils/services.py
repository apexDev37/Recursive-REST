"""
This module provides singleton service classes for reusable Model services.
The Singleton Pattern supports a centralized and reusable design. It avoids
unnecessary instantiation and ensures that only a single instance is reused
throughout an application.

@see  /add/reference
"""

import logging
from typing import Self

from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory
from rest_framework.request import Request
from rest_framework.response import Response
from greetings.auth.services import OAuth2CredentialsService
from greetings.models import Greeting


CUSTOM_GOODBYE: str = "Kwaheri"

logger = logging.getLogger(__name__)


class GreetingService:
    """
    Singleton service to encapsulate custom logic for the Greeting model.
    """

    instance = None

    def __new__(cls) -> Self:
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def create_and_save(custom_greeting: str) -> None:
        greeting = Greeting(greeting_text=custom_greeting)
        greeting.save()
        logger.info(f'Save custom greeting "{greeting.greeting_text}" from user.')


class RecursiveViewService:
  """
  Service to encapsulate logic for making a recursive view call.
  """

  @staticmethod
  def try_make_recursive_call(initial_param: str, initial_request: Request) -> None:
    request = RecursiveViewService._update_request_query_param(initial_param, initial_request)
    logger.debug("recursive call to api_view: views.save_custom_greeting.")
    return RecursiveViewService._make_recursive_call(request)


  def _make_recursive_call(request: WSGIRequest) -> Response:
    from greetings.views import save_custom_greeting

    oauth_service = OAuth2CredentialsService()
    access_token = oauth_service.get_access_token()
    request = RecursiveViewService._authorize_request(access_token, request)
    return save_custom_greeting(request)


  def _authorize_request(token: str, request: WSGIRequest) -> WSGIRequest:
    auth = "Bearer {0}".format(token)
    request.environ.setdefault("HTTP_AUTHORIZATION", auth)
    return request


  def _update_request_query_param(
      initial_param: str, initial_request: Request
  ) -> WSGIRequest:
    path: str = initial_request.build_absolute_uri()
    updated_path = path.replace(f"={initial_param}", f"={CUSTOM_GOODBYE}", 1)
    factory = RequestFactory()
    return factory.post(path=updated_path)
