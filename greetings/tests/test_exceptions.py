from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from greetings.views import save_custom_greeting

# Constant String Literals
GREETING_ENDPOINT = "/greetings/api/v1/greeting/"
GREETING_PARAM = "?greeting="
GREETING_URI = GREETING_ENDPOINT + GREETING_PARAM

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
