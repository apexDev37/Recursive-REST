import unittest

from django.urls import reverse
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from greetings.utils.exceptions import RequiredParamMissing
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
