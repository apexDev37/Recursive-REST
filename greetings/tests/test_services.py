import unittest
from unittest.mock import patch

from django.http import HttpRequest
from django.urls import reverse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from greetings.utils.constants import CUSTOM_GOODBYE
from greetings.utils.services import RecursiveViewService

BASE_MODULE = "greetings.views"
DRF_VIEW = 'save_custom_greeting'


class RecursiveTestCase(unittest.TestCase):
    """
    Test case to test behavior for recursive view call.
    """

    def setUp(self) -> None:
        self.under_test = RecursiveViewService
        self.initial_request = prepare_initial_request()


    def test_should_log_debug_alert_message_when_making_recursive_call(self) -> None:
        # Given
        service_logger = "greetings.utils.services"
        expected = "recursive call"

        # Then
        with self.assertLogs(service_logger, level="DEBUG") as cm:
            self.under_test.make_recursive_call(self.initial_request)  # When
            self.assertGreaterEqual(len(cm.output), 1)
            self.assertIn(expected, str(cm.output))

    @patch(f"{BASE_MODULE}.{DRF_VIEW}")
    def test_should_make_recursive_view_call_with_http_request_instance_argument(
        self, mock_view
    ) -> None:
        # Given
        request = self.initial_request
        expected = HttpRequest

        # When
        self.under_test.make_recursive_call(request)
        actual = mock_view.call_args[0][0]

        # Then
        mock_view.assert_called_once()
        self.assertIsInstance(actual, expected)

    @patch(f"{BASE_MODULE}.{DRF_VIEW}")
    def test_should_make_recursive_view_call_with_clone_of_initial_request(
        self, mock_view
    ) -> None:
        # Given
        request = self.initial_request
        expected = {
            "path": request.path,
            "method": request.method,
        }

        # When
        self.under_test.make_recursive_call(request)
        actual = mock_view.call_args[0][0]

        # Then
        self.assertEqual(actual.path, expected["path"])
        self.assertEqual(actual.method, expected["method"])

    @patch(f"{BASE_MODULE}.{DRF_VIEW}")
    def test_should_make_recursive_view_call_with_goodbye_query_param_value(
        self, mock_view
    ) -> None:
        # Given
        request = self.initial_request
        expected: dict = get_query_param(request, greeting=CUSTOM_GOODBYE)

        # When
        self.under_test.make_recursive_call(request)
        request = mock_view.call_args[0][0]
        actual: str = request.META["QUERY_STRING"]

        # Then
        self.assertEqual(actual.split('=')[0], expected['key'])
        self.assertEqual(actual.split('=')[1], expected['value'])

    @patch(f"{BASE_MODULE}.{DRF_VIEW}")
    def test_should_make_recursive_view_call_with_authorized_request_argument(
        self, mock_view
    ) -> None:
        # Given
        request = self.initial_request
        expected = "Authorization"

        # When
        self.under_test.make_recursive_call(request)
        actual = mock_view.call_args[0][0]

        # Then
        mock_view.assert_called_once()
        self.assertTrue(actual.environ.get("HTTP_AUTHORIZATION"))
        self.assertIn(expected, actual.headers)

    @patch(f"{BASE_MODULE}.{DRF_VIEW}")
    def test_should_make_recursive_view_call_with_custom_greeting_data(self, mock_view) -> None:
      # Given
      request = self.initial_request
      expected: dict = get_query_param(request)

      # When
      self.under_test.make_recursive_call(request)
      actual = mock_view.call_args[0][0]

      # Then
      mock_view.assert_called_once()
      self.assertTrue(actual.POST)
      self.assertIn(expected['key'], actual.POST.keys())
      self.assertIsInstance(actual.POST['greeting'], str)
      self.assertEqual(actual.POST['greeting'], expected['value'])


# -------------------------------------------------------------------------------  
# Test utility functions 
# -------------------------------------------------------------------------------

def prepare_initial_request() -> Request:
  """ 
  Create and mimic request passed to service from view.
  NB: Should be instance of `rest_framework.request.Request`
  """

  factory = APIRequestFactory()  
  url = reverse('greetings:save_custom_greeting')
  request = factory.post(path=url, QUERY_STRING="greeting=tests", format='json')
  return Request(request=request)

def get_query_param(request: Request, greeting: str = None) -> dict:
  query_param: str = request.META['QUERY_STRING']
  key = query_param.split('=')[0]
  value = query_param.split('=')[1] if greeting == None else greeting
  return {'key': key, 'value': value}
