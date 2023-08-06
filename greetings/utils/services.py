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
    """

    @staticmethod
    def make_recursive_call(greeting: str, initial_request: Request) -> None:
        """
        @update Consider removing <greeting: str> parameter to mitigate risk
                of user passing data inconsistent with request. Depend on
                source of truth, <initial_request: Request>, for query param: greeting.
        """
        
        request = RecursiveViewService._update_query_param(greeting, initial_request)
        logger.debug("recursive call to api_view: views.save_custom_greeting.")
        return RecursiveViewService._call_view(request)

    def _call_view(request: WSGIRequest) -> Response:
        from greetings.views import save_custom_greeting

        oauth_service = OAuth2CredentialsService()
        request = oauth_service.authorize_request(request)
        return save_custom_greeting(request)

    def _update_query_param(greeting: str, initial_request: Request) -> WSGIRequest:
        path: str = initial_request.build_absolute_uri()
        updated_path = path.replace(f"={greeting}", f"={CUSTOM_GOODBYE}", 1)
        data = {'greeting': greeting}
        factory = RequestFactory()
        return factory.post(path=updated_path, data=data)
