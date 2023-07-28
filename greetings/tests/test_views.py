import unittest
from unittest.mock import patch

from django.http import HttpRequest
from django.test import RequestFactory, TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.response import Response
from greetings.utils.constants import GreetingsPathConstants as path
from greetings.views import logger as view_logger
from greetings.views import CUSTOM_GOODBYE
from greetings.views import (
  make_recursive_call,
  try_make_recursive_call,
  update_request_query_param,
)

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
        self.client = Client(
            headers={
                "user-agent": "curl/7.79.1",
                "accept": "application/json",
            },
        )
        
    @patch('greetings.views.save_custom_greeting')
    def test_should_make_recursive_view_call_with_http_request_instance_argument(self, mock_view) -> None:
        # Given
        param = "greeting"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)

        # When
        make_recursive_call(initial_request)
        actual = mock_view.call_args[0][0]
        
        # Then
        mock_view.assert_called_once()
        self.assertIsInstance(actual, HttpRequest)

    @patch('greetings.views.save_custom_greeting')
    def test_should_make_recursive_view_call_with_clone_of_initial_request(self, mock_view) -> None:
        # Given
        param = "greeting"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)
        expected = {'path': str(path.GREETING_ENDPOINT), 'method': 'POST', 'param_key': str(path.GREETING_PARAM_KEY)}

        # When
        make_recursive_call(initial_request)
        
        actual = mock_view.call_args[0][0]

        # Then
        self.assertEqual(actual.path_info, expected['path'])
        self.assertEqual(actual.method, expected['method'])
        self.assertIsNotNone(actual.META['QUERY_STRING'])
        self.assertIn(expected['param_key'].removeprefix('?'), actual.META['QUERY_STRING'])

    def test_should_log_debug_alert_message_when_making_recursive_call(self) -> None:
        # Given
        param = "clone"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)
        expected = 'recursive call'

        # Then
        with self.assertLogs(view_logger, level="DEBUG") as cm:
            try_make_recursive_call(param, initial_request)  # When
            self.assertGreaterEqual(len(cm.output), 1)
            self.assertIn(expected, str(cm.output))

    def test_should_update_initial_request_query_param_value_with_custom_goodbye(self) -> None:
        # Given
        param = "clone"
        url = str(path.GREETING_URI) + param
        initial_request = self.factory.post(url)
        expected = CUSTOM_GOODBYE

        # When
        request = update_request_query_param(param, initial_request)
        actual = request.META['QUERY_STRING']

        # Then
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, str)
        self.assertIn(expected, actual)
    
    @patch('greetings.views.save_custom_greeting')
    def test_should_make_recursive_view_call_with_goodbye_query_param_value(self, mock_view) -> None:
      # Given
      param = "clone"
      url = str(path.GREETING_URI) + param
      initial_request = self.factory.post(url)
      expected = CUSTOM_GOODBYE
      
      # When
      try_make_recursive_call(param, initial_request)
      actual = mock_view.call_args[0][0]
      
      # Then
      self.assertIsNotNone(actual.META['QUERY_STRING'])
      self.assertIn(expected, actual.META['QUERY_STRING'])

      

