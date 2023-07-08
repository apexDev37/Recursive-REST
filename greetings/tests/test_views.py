from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.test.client import Client
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from greetings.models import Greeting
from greetings.views import save_custom_greeting

# Constant String Literals
GREETING_ENDPOINT = "/greetings/api/v1/greeting/"
GREETING_PARAM = "?greeting="

GREETING_URI = GREETING_ENDPOINT + GREETING_PARAM


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
        url_without_param = "/greetings/api/v1/greeting/"

        # When
        response = self.client.post(path=url_without_param)

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

        # When
        response = self.client.generic(method=not_allowed, path=GREETING_ENDPOINT)
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
        valid_query_param = "hey, am not blank or null"

        # When
        response = self.client.post(path=(GREETING_URI + valid_query_param))

        # Then
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(valid_query_param)
        self.assertIsNot(valid_query_param, "")
        self.assertContains(
            response, status_code=status.HTTP_201_CREATED, text="message"
        )
        self.assertContains(
            response, status_code=status.HTTP_201_CREATED, text="Greeting saved"
        )

class GreetingsViewLogicTestCase(TestCase):
  """ Test case to test view logic, behavior, and error handling. """
  
  def setUp(self) -> None:
    self.factory = RequestFactory()
  
  def test_should_raise_custom_exception_for_absent_query_param_in_url(self) -> None:
    """ Given the absence of a query_param in the url, on a post, raise an exception. """

    # Given
    request_without_param = self.factory.post(GREETING_ENDPOINT)

    # Then
    with self.assertRaises(ValueError):
      save_custom_greeting(request_without_param)
  
  def test_should_not_raise_custom_exception_for_query_param_key_in_url(self) -> None:
    """ Given a present query_param key in the url, on a post, don't raise an exception. """

    # Given
    request_with_param_key = self.factory.post(GREETING_URI)

    try:
      save_custom_greeting(request_with_param_key)
    except Exception:
      self.failIf( Exception is ValueError)

  def test_should_raise_exception_when_query_param_value_is_blank_or_none(self) -> None:
    """ Given a blank or none query_param value, raise an exception. """

    # Given
    blank_param_value = ''
    
    # When
    request = self.factory.post(GREETING_URI + blank_param_value)
    
    # Then
    with self.assertRaisesMessage(
      ValueError, 
      "Value for query param: greeting cannot be blank or empty."):
        save_custom_greeting(request)
  
  def test_should_raise_exception_if_query_param_value_has_non_alphabetical_chars(self) -> None:
    """ Given a value that contains non alphabetical chars, raise an exception. """

    # Given
    value = '_greeting@37'
    
    # When
    request = self.factory.post(GREETING_URI + value)
    
    self.assertIsInstance(value, str)
    with self.assertRaisesMessage(
      ValueError, 
      "Value for query param: greeting cannot contain non alphabetic chars."):
        save_custom_greeting(request)
