from unittest import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from greetings.utils.validators import GreetingPathValidator


class ValidatorsTestCase(TestCase):
  """
  Test case to test all custom validators for `greetings` app
  """

  def setUp(self) -> None:
    self.factory = APIRequestFactory(format='json')
  
  def test_should_raise_exception_when_greeting_param_key_not_found_in_url(self) -> None:
    # Given
    path = reverse('greetings:save_custom_greeting')
    request = self.factory.post(path=path)
    rest_request = Request(request=request)
    
    # Then
    self.assertFalse(rest_request.META['QUERY_STRING'])
    with self.assertRaises(ValueError):
      GreetingPathValidator(rest_request)   # When

  def test_should_return_greeting_when_greeting_param_key_found_in_url(self) -> None:
    # Given
    path = reverse('greetings:save_custom_greeting')
    request = self.factory.post(path=path, QUERY_STRING='greeting=test')
    rest_request = Request(request=request)

    # When
    actual = GreetingPathValidator(rest_request)
    
    # Then
    self.assertTrue(rest_request.META['QUERY_STRING'])
    self.assertIsInstance(actual, str)
    self.assertEqual(actual, 'test')
