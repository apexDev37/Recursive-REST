from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response

from greetings.utils.constants import GreetingsPathConstants as path

BASE_MODULE = "greetings.views"


class RequestTestCase(TestCase):
    """
    Test case for the API view routing, request, and response behavior
    """

    def setUp(self) -> None:
        # Create custom access token for testing purposes only
        test_token = AccessToken.objects.create(
          token='test_access_token', 
          user=None, 
          expires=timezone.now() + timezone.timedelta(seconds=60), 
          scope='read write',
        )        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(test_token.token))

    def test_should_return_400_BAD_REQUEST_for_request_without_a_greeting_query_param_key(
        self,
    ) -> None:
        """Given no query param key is provided, on a post request, return a 400 response."""

        # Given
        url = str(path.GREETING_ENDPOINT)

        # When
        response = self.client.post(path=url)

        # Then
        self.assertIsInstance(response, Response)
        self.assertContains(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            text="Failed to save custom greeting from user.",
        )

    def test_should_return_405_METHOD_NOT_ALLOWED_for_request_with_wrong_http_method(
        self,
    ) -> None:
        """Given a request with a not allowed HTTP method return a 405 response."""

        # Given
        not_allowed = "PUT"
        url = str(path.GREETING_URI)

        # When
        response = self.client.generic(method=not_allowed, path=url)
        error_detail = response.data["detail"]

        # Then
        self.assertIsInstance(response, Response)
        self.assertContains(
            response,
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            text="not allowed.",
        )

    def test_should_return_201_CREATED_for_request_with_valid_greeting_query_param(
        self,
    ) -> None:
        """Given a valid query param, on a post request, return a 201 response."""

        # Given
        value = "valid"
        url = str(path.GREETING_URI) + value

        # When
        response = self.client.post(path=url)

        # Then
        self.assertIsInstance(response, Response)
        self.assertContains(
            response,
            status_code=status.HTTP_201_CREATED,
            text="Saved custom greeting from user.",
        )
