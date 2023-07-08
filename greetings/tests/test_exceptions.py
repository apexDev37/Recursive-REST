from django.test import RequestFactory, TestCase

from greetings.views import save_custom_greeting

# Constant String Literals
GREETING_ENDPOINT = "/greetings/api/v1/greeting/"
GREETING_PARAM = "?greeting="
GREETING_URI = GREETING_ENDPOINT + GREETING_PARAM

class GreetingsExceptionsTestCase(TestCase):
  """
  Testcase for error handling and custom exception behavior in views.
  """
  
  def setUp(self) -> None:
    self.factory = RequestFactory()
  
  def test_should_raise_exception_for_absent_query_param_key_in_request_url(self) -> None:
    # Given
    request = self.factory.post(GREETING_ENDPOINT)

    # Then
    with self.assertRaises(ValueError):
      save_custom_greeting(request) # When
  
  def test_should_raise_exception_when_query_param_value_is_blank_or_none(self) -> None:
    # Given
    value = ''    
    request = self.factory.post(GREETING_URI + value)
    
    # Then
    with self.assertRaisesMessage(
      ValueError, 
      "Value for query param: greeting cannot be blank or empty."):
        save_custom_greeting(request) # When
  
  def test_should_raise_exception_if_query_param_value_has_non_alphabetical_chars(self) -> None:
    # Given
    value = '_greeting@37'
    request = self.factory.post(GREETING_URI + value)
    
    # Then
    self.assertIsInstance(value, str)
    with self.assertRaisesMessage(
      ValueError, 
      "Value for query param: greeting cannot contain non alphabetic chars."):
        save_custom_greeting(request) # When
