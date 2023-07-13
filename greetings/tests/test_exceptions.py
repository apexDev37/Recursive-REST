from django.test import RequestFactory, TestCase

from rest_framework.exceptions import ValidationError

from greetings.views import save_custom_greeting
from greetings.utils.constants import GreetingsPathConstants as path

class GreetingsExceptionsTestCase(TestCase):
  """
  Testcase for error handling and custom exception behavior in views.
  """
  
  def setUp(self) -> None:
    self.factory = RequestFactory()
  
  def test_should_raise_exception_for_absent_query_param_key_in_request_url(self) -> None:
    # Given
    url = str(path.GREETING_ENDPOINT)
    request = self.factory.post(url)

    # Then
    with self.assertRaises(ValueError):
      save_custom_greeting(request) # When
  
  def test_should_raise_exception_when_query_param_value_is_blank_or_none(self) -> None:
    # Given
    value = ''    
    url = str(path.GREETING_URI) + value
    request = self.factory.post(url)
    
    # Then
    with self.assertRaisesMessage(
      ValidationError, 
      "Value for query param: greeting cannot be blank or empty."):
        save_custom_greeting(request) # When
  
  def test_should_raise_exception_if_query_param_value_has_non_alphabetical_chars(self) -> None:
    # Given
    value = '_greeting@37'
    url = str(path.GREETING_URI) + value
    request = self.factory.post(url)
    
    # Then
    self.assertIsInstance(value, str)
    with self.assertRaisesMessage(
      ValidationError, 
      "Value for query param: greeting cannot contain non alphabetic chars."):
        save_custom_greeting(request) # When
