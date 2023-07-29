import unittest
from unittest.mock import patch

from django.http import HttpRequest
from django.test import RequestFactory, TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.response import Response
from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.services import RecursiveViewService
from greetings.views import CUSTOM_GOODBYE


BASE_MODULE = 'greetings.views'


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


class RecursiveTestCase(unittest.TestCase):
    """
    Test case to test behavior for recursive view call.
    """

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.query_param = 'greeting'
        url = str(path.GREETING_URI) + self.query_param
        self.initial_request = self.factory.post(
          path=url
        )
        
    @patch(f'{BASE_MODULE}.save_custom_greeting')
    def test_should_make_recursive_view_call_with_http_request_instance_argument(self, mock_view) -> None:
        # Given
        expected = HttpRequest
        
        # When
        RecursiveViewService._make_recursive_call(self.initial_request)
        actual = mock_view.call_args[0][0]
        
        # Then
        mock_view.assert_called_once()
        self.assertIsInstance(actual, expected)

    @patch(f'{BASE_MODULE}.save_custom_greeting')
    def test_should_make_recursive_view_call_with_clone_of_initial_request(self, mock_view) -> None:
        # Given
        expected = {
          'path': str(path.GREETING_ENDPOINT), 
          'method': 'POST', 
        }

        # When
        RecursiveViewService._make_recursive_call(self.initial_request)
        actual = mock_view.call_args[0][0]

        # Then
        self.assertEqual(actual.path, expected['path'])
        self.assertEqual(actual.method, expected['method'])

    def test_should_log_debug_alert_message_when_making_recursive_call(self) -> None:
        # Given
        service_logger = 'greetings.utils.services'
        expected = 'recursive call'

        # Then
        with self.assertLogs(service_logger, level="DEBUG") as cm:
            RecursiveViewService.try_make_recursive_call(self.query_param, self.initial_request)  # When
            self.assertGreaterEqual(len(cm.output), 1)
            self.assertIn(expected, str(cm.output))

    def test_should_update_initial_request_query_param_value_with_custom_goodbye(self) -> None:
        # Given
        expected = CUSTOM_GOODBYE

        # When
        request = RecursiveViewService._update_request_query_param(self.query_param, self.initial_request)
        actual = request.META['QUERY_STRING']

        # Then
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, str)
        self.assertIn(expected, actual)
    
    @patch(f'{BASE_MODULE}.save_custom_greeting')
    def test_should_make_recursive_view_call_with_goodbye_query_param_value(self, mock_view) -> None:
      # Given
      expected = CUSTOM_GOODBYE
      
      # When
      RecursiveViewService.try_make_recursive_call(self.query_param, self.initial_request)
      request = mock_view.call_args[0][0]
      actual = request.META['QUERY_STRING'].removeprefix('greeting=')
      
      # Then
      self.assertEqual(actual, expected)

