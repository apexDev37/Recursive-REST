"""
This module provides singleton service classes for reusable Model services.
The Singleton Pattern supports a centralized and reusable design. It avoids
unnecessary instantiation and ensures that only a single instance is reused
throughout an application.

@see  /add/reference
"""

import logging
from typing import Any, Self

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from greetings.auth.services import OAuth2CredentialsService
from greetings.models import Greeting
from greetings.utils.constants import CUSTOM_GOODBYE

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

    Behavior::
      Receives an rest_framework `Request` instance argument.
      Prepares a `HttpRequest` instance to be passed to given view.
      Updates the query_param to a constant custom_goodbye `string`.
      Authorizes the request to authenticate with OAuth2 layer.
      Returns a view with a prepared `WSGIRequest` instance argument.
    """

    @staticmethod
    def make_recursive_call(initial_request: Request) -> None:
        request = RecursiveViewService._prepare_request(initial_request)
        request = RecursiveViewService._authenticate_and_authorize(request)
        return RecursiveViewService._call_view(request)

    def _prepare_request(request: Request) -> WSGIRequest:
        request = RecursiveViewService._get_request_data(request)
        factory = APIRequestFactory(format="json")
        return factory.post(
            path=request["path"], data=request["data"], QUERY_STRING=request["param"]
        )

    def _get_request_data(request: Request) -> dict[str, Any]:
        initial_greeting = request.query_params["greeting"]
        data = {"greeting": initial_greeting}
        goodbye = "greeting={0}".format(CUSTOM_GOODBYE)
        return {"path": request.path, "data": data, "param": goodbye}

    def _authenticate_and_authorize(request: WSGIRequest) -> WSGIRequest:
        oauth_service = OAuth2CredentialsService()
        request = oauth_service.authorize_request(request)
        return request

    def _call_view(request: WSGIRequest) -> Response:
        # Method-import to prevent circular dependency error
        from greetings.views import save_custom_greeting

        logger.debug("recursive call to api_view: views.save_custom_greeting.")
        return save_custom_greeting(request)
