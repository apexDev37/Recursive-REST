import unittest
from unittest.mock import ANY, patch

from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIClient

from greetings.views import save_custom_greeting
from greetings.utils.exceptions import RequiredParamMissing, custom_exception_handler
from greetings.utils.responses import GreetingErrorResponse
from greetings.utils.validators import GreetingParamValidator

class CustomExceptionTestCase(unittest.TestCase):
  """
  Test case to test definition and data of custom DRF API exceptions.
  """
  
  def setUp(self) -> None:
    pass
  
  def test_should_provide_defaults_for_missing_param_in_request_url(self) -> None:
    # Given
    expected = {
      'status_code': 400,
      'code': 'required_param_missing'}
    
    # When
    exc = RequiredParamMissing()

    # Then
    self.assertIsInstance(exc, APIException)
    self.assertEqual(exc.status_code, expected['status_code'])
    self.assertTrue(exc.detail)
    self.assertEqual(exc.get_codes(), expected['code'])

class ExceptionHandlerTestCase(APITestCase):
  """
  Test case to test response objects returned by custom exception handler.
  """
  
  def setUp(self) -> None:
    self.url = reverse('greetings:save_custom_greeting')
    self.client = APIClient(format='json')
    test_token = AccessToken.objects.create(
      token="test_access_token",
      user=None,
      expires=timezone.now() + timezone.timedelta(seconds=60),
      scope="read write",
    )
    self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(test_token.token))
  
  @patch('greetings.utils.exceptions.custom_exception_handler')
  def test_should_invoke_custom_handler_on_raised_exception_inside_view(self, mock_handler) -> None:
    # Given
    context = {
      'view': ANY,
      'args': ANY,
      'kwargs': ANY, 
      'request': ANY}
    defaults = RequiredParamMissing()
    mock_handler.return_value = GreetingErrorResponse(
      status_code=defaults.status_code,
      message=defaults.default_code,
      description=defaults.default_detail
    )
    
    # When
    response = self.client.post(path=self.url, QUERY_STRING=None)
    actual = response.data

    # Then
    mock_handler.assert_called_once()
    # mock_handler.assert_called_once_with(RequiredParamMissing(ANY), context)

  def test_should_return_custom_error_response_format_for_raised_exceptions(self) -> None:
    # Given
    expected = ['status_code', 'message', 'description']
         
    # When
    response = self.client.post(path=self.url, QUERY_STRING=None)
    actual: dict = response.data

    # Then
    self.assertListEqual(list(actual.keys()), expected)

  def test_should_return_standard_500_response_for_unhandled_exception(self) -> None:
    # Given
    exception = ValueError('Non APIException instance')
    expected = None

    # When
    actual = custom_exception_handler(exception, {})
    
    # Then 
    self.assertNotIsInstance(exception, APIException)
    self.assertIsNone(actual)
    self.assertEqual(actual, expected)
