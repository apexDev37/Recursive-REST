from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.test.client import RequestFactory

from rest_framework import status
from rest_framework.response import Response

from unittest import TestCase
from unittest.mock import call, patch

from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.services import CredentialManagerService, OAuth2CredentialsService
from greetings.views import (
  authorize_request,
  make_recursive_call,
  try_make_recursive_call,
)


BASE_MODULE: str = 'greetings.utils.services'

TEST_CLIENT_ID: str = 'test_id'
TEST_CLIENT_SECRET: str = 'test_secret'
TEST_ACCESS_TOKEN: str = 'test_access_token'

TOKEN_ENDPOINT: str = 'http://127.0.0.1:8000/o/token/'
CONTENT_TYPE: str = "application/x-www-form-urlencoded"
CACHE_CONTROL: str = "no-cache"
AUTHORIZATION: str = "Basic {0}"
GRANT_TYPE: str = "client_credentials"


class CredentialsTestCase(TestCase):
  """
  Test case to test that client credentials env 
  variables are provided and loaded from either the 
  host machine or a defined env file.
  
  Behavior: 
    GIVEN credentials are set on the host machine
    WHEN env variables are found in host environ
    THEN load and return the credentials (client ID and SECRET).
    
    GIVEN credentials are set in an env file
    WHEN credentials not found in host environ
    THEN read provided env_file and return client credentials.
    
    GIVEN credentials not set by user
    WHEN credentials are not found on host machine and env file
    THEN raise exception on required credentials not configured.
  """

  def setUp(self) -> None:
    self.client_id = TEST_CLIENT_ID
    self.client_secret = TEST_CLIENT_SECRET
    self.credential = f'{self.client_id}:{self.client_secret}'
    self.encoded_credential = 'dGVzdF9pZDp0ZXN0X3NlY3JldA=='
    self.under_test = CredentialManagerService()
  
  @patch(f'{BASE_MODULE}.os.environ')
  def test_should_raise_exception_for_missing_credentials_on_both_host_and_env_file(self, mock_environ) -> None:
    # Given
    mock_environ.get.side_effect = [
      None, None,   # Not found on host
      None, None    # Not found in env file
    ]    
    
    # Then
    with self.assertRaises(ImproperlyConfigured):
      self.under_test._load_env_credentials()  # When

  @patch(f'{BASE_MODULE}.os.environ')
  @patch(f'{BASE_MODULE}.environ.Env', autospec=True)
  def test_should_prefer_load_client_credentials_from_host_machine(self, mock_env, mock_environ) -> None:
    # Given
    expected = {'CLIENT_ID': self.client_id, 'CLIENT_SECRET': self.client_secret}
    mock_environ.get.side_effect = [
      expected['CLIENT_ID'], expected['CLIENT_SECRET']    # Found on host
    ]
    
    # When
    actual = self.under_test._load_env_credentials()
    
    # Then    
    mock_env.read_env.assert_not_called()
    mock_environ.get.assert_has_calls([
      call('CLIENT_ID', None),
      call('CLIENT_SECRET', None)
    ])
    self.assertEqual(actual['CLIENT_ID'], expected['CLIENT_ID'])
    self.assertEqual(actual['CLIENT_SECRET'], expected['CLIENT_SECRET'])

  @patch(f'{BASE_MODULE}.os.environ')
  @patch(f'{BASE_MODULE}.environ.Env', autospec=True)
  def test_should_fallback_to_load_client_credentials_from_env_file(self,  mock_env, mock_environ) -> None:
    # Given
    expected = {'CLIENT_ID': self.client_id, 'CLIENT_SECRET': self.client_secret}
    mock_environ.get.side_effect = [
      None, None,                                         # Not found on host
      expected['CLIENT_ID'], expected['CLIENT_SECRET']    # Found in env file
    ]
    
    # When
    actual = self.under_test._load_env_credentials()
    
    # Then    
    mock_env.read_env.assert_called_once()
    mock_environ.get.assert_has_calls([
      call('CLIENT_ID', None), call('CLIENT_SECRET', None),   # Try load from host
      call('CLIENT_ID', None),call('CLIENT_SECRET', None)     # Try load from env file
    ])
    self.assertEqual(actual['CLIENT_ID'], expected['CLIENT_ID'])
    self.assertEqual(actual['CLIENT_SECRET'], expected['CLIENT_SECRET'])
  
  @patch(f'{BASE_MODULE}.base64.b64encode')
  def test_should_base64_encode_the_provided_client_id_and_secret(self, mock_b64_encode) -> None:
    # Given
    expected = self.encoded_credential
    
    # When
    mock_b64_encode.return_value.decode.return_value = expected
    actual = self.under_test._encode_credentials(self.client_id, self.client_secret)
    
    # Then
    self.assertIsInstance(actual, str)
    mock_b64_encode.assert_called_once_with(self.credential.encode('utf-8'))
    self.assertEqual(actual, expected)


class AuthenticationTestCase(TestCase):
  """
  Test case to test the auth flow process to acquire an
  access token for the grant type: "client credentials".
  
  Behavior:
    GIVEN a registered application's client ID and secret
    WHEN credentials are loaded into the application context
    THEN generate a base64 encoded credential.
    
    GIVEN a valid base64 encoded credential
    WHEN making an auth request to the Auth server
    THEN include credential in the HTTP Basic Authorization Header. 
    
    GIVEN the expected HTTP requirements from the Auth server
    WHEN making a valid auth request for an access token
    THEN verify a JSON response with an access token. 
  """
  
  def setUp(self) -> None:
    self.client_id = TEST_CLIENT_ID
    self.client_secret = TEST_CLIENT_SECRET
    self.credential = f'{self.client_id}:{self.client_secret}'
    # generated by script: ./utility/scripts/oauth/encoder.py
    self.encoded_credential = 'dGVzdF9pZDp0ZXN0X3NlY3JldA=='
    self.under_test = OAuth2CredentialsService()

  
  @patch(f'{BASE_MODULE}.requests')
  def test_should_provide_minimum_required_arguments_for_access_token_request(self, mock_requests) -> None:    
    # Given
    expected = {
      'url': TOKEN_ENDPOINT,
      'headers': {
        "Content-Type": CONTENT_TYPE,
        "Authorization": AUTHORIZATION.format(self.encoded_credential),
      },
      'data': {"grant_type": GRANT_TYPE},
    }
    
    # When
    self.under_test._request_access_token(self.encoded_credential)
    actual = mock_requests.post.call_args_list[0][1]
        
    # Then
    mock_requests.post.assert_called_once()
    self.assertIn('url', actual)
    self.assertEqual(actual['url'], expected['url'])

    self.assertDictContainsSubset(expected['headers'], actual['headers'])
    self.assertDictEqual(actual['data'], expected['data'])
    
  @patch(f'{BASE_MODULE}.requests')
  def test_should_retrieve_access_token_response_from_valid_client_request(self, mock_requests) -> None:
    # Given
    expected = {
      'access_token': 'valid_access_token_from_server', 
      'expires_in': 36000, 
      'token_type': 'Bearer', 
      'scope': 'read write'
    }
    
    # When
    mock_requests.post.return_value.json.return_value = expected
    response = self.under_test._request_access_token(self.encoded_credential)
    actual = response.json()
    
    # Then
    mock_requests.post.assert_called_once()
    self.assertIsInstance(actual, dict)
    self.assertIn('access_token', actual)
    self.assertEqual(actual, expected)
        

class AuthorizationTestCase(TestCase):
  """
  Test case to test that request instances have the expected
  authorization 'Bearer <token>' for request instances passed
  to protected DRF API views. 
  """

  def setUp(self) -> None:
    factory = RequestFactory()
    self.access_token = TEST_ACCESS_TOKEN
    self.initial_request = factory.post(    # Mimic initial request
      path=str(path.GREETING_URI) + 'yellow',
      headers={'Accept': 'application/json'}
    )

  def test_should_authorize_request_argument_for_recursive_view_call(self) -> None:
    # Given
    expected = {'type': 'Bearer', 'token': self.access_token}

    # When
    actual = authorize_request(self.access_token, self.initial_request)
    auth = actual.environ.get('HTTP_AUTHORIZATION')
    
    # Then
    self.assertIsInstance(actual, HttpRequest)
    self.assertIsNotNone(auth)
    self.assertEqual(auth.split(' ')[0], expected['type'])
    self.assertEqual(auth.split(' ')[1], expected['token'])
  
  @patch(f'greetings.views.save_custom_greeting')
  def test_should_make_recursive_view_call_with_authorized_request_argument(self, mock_view) -> None:
    # Given
    authorized_request = authorize_request(self.access_token, self.initial_request)
    expected = 'Authorization'

    # When
    make_recursive_call(authorized_request)
    actual = mock_view.call_args[0][0]

    # Then
    mock_view.assert_called_once()
    mock_view.assert_called_once_with(authorized_request)
    self.assertTrue(actual.environ.get('HTTP_AUTHORIZATION'))
    self.assertIn(expected, actual.headers)
  
  def test_should_return_success_message_from_authorized_recursive_view_call(self) -> None:
    # Given
    # Bad Practice WARNING: remove dependency in tests by refactoring 
    #                       function into `make_recursive_call`
    authorized_request = authorize_request(self.access_token, self.initial_request)
    expected = {'status_code': 201, 'message': 'Success'}
    
    # When
    actual = try_make_recursive_call('yellow', self.initial_request)
    
    # Then
    self.assertIsInstance(actual, Response)
    self.assertEqual(actual.status_code, status.HTTP_201_CREATED)
    self.assertEqual(actual.data['message'], expected['message'])