import inspect

from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken
from rest_framework.test import APIClient, APISimpleTestCase
from rest_framework import status
from rest_framework.response import Response

from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.responses import CustomGreetingResponse, ErrorGreetingResponse


BASE_MODULE = "greetings.views"


class RequestTestCase(TestCase):
    """
    Test case for the API view routing, request, and response behavior
    """

    def setUp(self) -> None:
        # Create custom access token for testing purposes only
        test_token = AccessToken.objects.create(
          token='test_access_token', 
          user=None, 
          expires=timezone.now() + timezone.timedelta(seconds=60), 
          scope='read write',
        )        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(test_token.token))

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
            text="Failed to save custom greeting submitted by user.",
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

    def _should_return_201_CREATED_for_request_with_valid_greeting_query_param(
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

class CustomResponseTestCase(APISimpleTestCase):
  """
  Test case to test custom wrapper response instances from DRF view.
  """
  
  def setUp(self) -> None:
    pass
  
  def test_should_return_rest_frameworks_response_instance_to_client(self) -> None:
    # Given
    expected = Response

    # When
    actual = CustomGreetingResponse(
      status_code=200, message='test message', description='test description')
    
    # Then
    self.assertIsInstance(actual, expected)

  def test_should_omit_data_from_json_response_if_not_provided(self) -> None:
    # Given
    expected = 3

    # When
    actual = CustomGreetingResponse(
      status_code=200, message='test message', description='test description',)
    
    # Then
    self.assertEqual(len(actual.data), expected)

  def test_should_raise_exception_if_required_arguments_are_missing(self) -> None:
    # # Get the signature of the constructor
    # constructor = CustomGreetingResponse.__init__
    # signature = inspect.signature(constructor)

    # # Count the number of parameters without default values
    # required_args_count = sum(
    #     1 for param in signature.parameters.values()
    #     if param.default in [inspect.Parameter.empty, None]
    # )

    # Then
    with self.assertRaisesMessage(
      TypeError, 'required positional arguments'):
      CustomGreetingResponse() # When
    
  def test_should_return_base_response_with_provided_actual_arguments(self) -> None:
    # Given
    expected = {
      'status_code': 200, 
      'message': 'test message', 
      'description': 'test description', 
      'some-key': 'some_value'}

    actual = CustomGreetingResponse(
      status_code=expected['status_code'], 
      message=expected['message'], 
      description=expected['description'], 
      data={'some-key': 'some_value'})
    
    self.assertEqual(len(actual.data), len(expected))
    self.assertDictEqual(actual.data, expected)

  def test_should_return_error_default_values_on_non_provided_actual_arguments(self) -> None:
    # Given
    expected = {'message': 'Error', 
                'description': 'Failed to save custom greeting submitted by user.'}

    # When
    actual = ErrorGreetingResponse()

    self.assertEqual(actual.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(actual.data['message'], expected['message'])
    self.assertEqual(actual.data['description'], expected['description'])
