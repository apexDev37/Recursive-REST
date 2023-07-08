from django.test import TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from greetings.utils.constants import GreetingsPathConstants as path

class GreetingViewRequestTestCase(TestCase):
    """Tests for the Greeting view request, routing and response behavior"""

    def setUp(self) -> None:
        self.client = Client(
            headers={
                "user-agent": "curl/7.79.1",
                "accept": "application/json",
            },
        )

    def test_should_return_400_BAD_REQUEST_for_request_without_a_greeting_query_param(
        self,
    ) -> None:
        """Given no query param is provided, on a post request, return a 400 response."""

        # Given
        url = str(path.GREETING_ENDPOINT)

        # When
        response = self.client.post(path=url)

        # Then
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(
            response, status_code=status.HTTP_400_BAD_REQUEST, text="error"
        )
        self.assertContains(
            response, status_code=status.HTTP_400_BAD_REQUEST, text="Invalid greeting"
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
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIsInstance(error_detail, ErrorDetail)
        self.assertIn("not allowed", error_detail)

    def test_should_return_201_CREATED_for_request_with_valid_greeting_query_param(
        self,
    ) -> None:
        """Given a valid query param, on a post request, return a 201 response."""

        # Given
        value = "hey, am not blank or null"
        url = str(path.GREETING_URI) + value

        # When
        response = self.client.post(path=url)

        # Then
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(value)
        self.assertIsNot(value, "")
        self.assertContains(
            response, status_code=status.HTTP_201_CREATED, text="message"
        )
        self.assertContains(
            response, status_code=status.HTTP_201_CREATED, text="Greeting saved"
        )
