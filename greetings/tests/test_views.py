from django.test import RequestFactory, TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.response import Response

from greetings.utils.constants import GreetingsPathConstants as path
from greetings.views import logger as view_logger
from greetings.views import save_custom_greeting


class RequestTestCase(TestCase):
    """
    Test case for the API view routing, request, and response behavior
    """

    def setUp(self) -> None:
        self.client = Client(
            headers={
                "user-agent": "curl/7.79.1",
                "accept": "application/json",
            },
        )

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


class RecursiveTestCase(TestCase):
    """
    Test case to test behavior for recursive view call.
    """

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client(
            headers={
                "user-agent": "curl/7.79.1",
                "accept": "application/json",
            },
        )

    def test_should_make_recursive_call_with_cloned_request_instance(self) -> None:
        # Given
        param = "clone"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)

        # When
        response = self.client.post(url)
        recursive_request = response.wsgi_request

        # Then
        self.assertEqual(type(recursive_request), type(initial_request))
        self.assertEqual(recursive_request.path_info, initial_request.path_info)
        self.assertEqual(recursive_request.method, "POST")
        self.assertIn("QUERY_STRING", response.request)

    def test_should_log_debug_alert_message_when_making_recursive_call(self) -> None:
        # Given
        param = "clone"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)

        # Then
        with self.assertLogs(view_logger, level="DEBUG") as cm:
            response = save_custom_greeting(initial_request)  # When
            self.assertGreaterEqual(len(cm.output), 1)
            self.assertIn("DEBUG:greetings.views:recursive call", str(cm.output))

    def test_should_make_recursive_call_with_updated_query_param_value(self) -> None:
        # Given
        param = "clone"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)

        # When
        response = save_custom_greeting(initial_request)

        # Then
        self.assertIsInstance(response, Response)
        self.assertContains(
            response, status_code=status.HTTP_201_CREATED, text="goodbye"
        )
        self.assertNotEqual(response.data["goodbye"], param)
