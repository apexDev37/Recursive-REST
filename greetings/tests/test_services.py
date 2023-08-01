import unittest
from unittest.mock import patch

from django.http import HttpRequest
from django.test import RequestFactory
from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.services import RecursiveViewService
from greetings.utils.constants import CUSTOM_GOODBYE


BASE_MODULE = 'greetings.views'


class RecursiveTestCase(unittest.TestCase):
    """
    Test case to test behavior for recursive view call.
    """

    def setUp(self) -> None:
        self.under_test = RecursiveViewService
        factory = RequestFactory()
        self.query_param = 'greeting'
        url = str(path.GREETING_URI) + self.query_param
        self.initial_request = factory.post(
          path=url
        )

    def test_should_update_initial_request_query_param_value_with_custom_goodbye(self) -> None:
        # Given
        expected = CUSTOM_GOODBYE

        # When
        request = self.under_test._update_query_param(self.query_param, self.initial_request)
        actual = request.META['QUERY_STRING']

        # Then
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, str)
        self.assertIn(expected, actual)

    def test_should_log_debug_alert_message_when_making_recursive_call(self) -> None:
        # Given
        service_logger = 'greetings.utils.services'
        expected = 'recursive call'

        # Then
        with self.assertLogs(service_logger, level="DEBUG") as cm:
            self.under_test.make_recursive_call(self.query_param, self.initial_request)  # When
            self.assertGreaterEqual(len(cm.output), 1)
            self.assertIn(expected, str(cm.output))
        
    @patch(f'{BASE_MODULE}.save_custom_greeting')
    def test_should_make_recursive_view_call_with_http_request_instance_argument(self, mock_view) -> None:
        # Given
        expected = HttpRequest
        
        # When
        self.under_test._call_view(self.initial_request)
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
        self.under_test._call_view(self.initial_request)
        actual = mock_view.call_args[0][0]

        # Then
        self.assertEqual(actual.path, expected['path'])
        self.assertEqual(actual.method, expected['method'])
    
    @patch(f'{BASE_MODULE}.save_custom_greeting')
    def test_should_make_recursive_view_call_with_goodbye_query_param_value(self, mock_view) -> None:
      # Given
      expected = CUSTOM_GOODBYE
      
      # When
      self.under_test.make_recursive_call(self.query_param, self.initial_request)
      request = mock_view.call_args[0][0]
      actual = request.META['QUERY_STRING'].removeprefix('greeting=')
      
      # Then
      self.assertEqual(actual, expected)

    @patch(f"{BASE_MODULE}.save_custom_greeting")
    def test_should_make_recursive_view_call_with_authorized_request_argument(self, mock_view) -> None:
      # Given
      expected = "Authorization"

      # When
      self.under_test._call_view(self.initial_request)
      actual = mock_view.call_args[0][0]

      # Then
      mock_view.assert_called_once()
      mock_view.assert_called_once_with(self.initial_request)
      self.assertTrue(actual.environ.get("HTTP_AUTHORIZATION"))
      self.assertIn(expected, actual.headers)
