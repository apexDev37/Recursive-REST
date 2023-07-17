from unittest import TestCase
from unittest.mock import call, patch

from greetings.views import encode_credentials, load_env_credentials


class AuthenticationTestCase(TestCase):
  """
  Test case to test the auth flow process to acquire an
  access token for the grant type: "client credentials".
  """
  
  def setUp(self) -> None:
    self.client_id = 'test_id'
    self.client_secret = 'test_secret'
    self.credential = f'{self.client_id}:{self.client_secret}'
    
  @patch('greetings.views.base64.b64encode')
  def test_should_base64_encode_the_provided_client_id_and_secret(self, mock_b64_encode) -> None:
    # Given
    # generated by script: ./utility/scripts/oauth/encoder.py
    expected = 'dGVzdF9pZDp0ZXN0X3NlY3JldA=='
    
    # When
    mock_b64_encode.return_value.decode.return_value = expected
    actual = encode_credentials(self.client_id, self.client_secret)
    
    # Then
    self.assertIsInstance(actual, str)
    mock_b64_encode.assert_called_once_with(self.credential.encode('utf-8'))
    self.assertEqual(actual, expected)

  @patch('greetings.views.os.environ')
  def test_should_raise_exception_for_missing_credentials_on_both_host_and_env_file(self, mock_environ) -> None:
    # Given
    mock_environ.get.side_effect = [
      None, None,   # Not found on host
      None, None    # Not found in env file
    ]    
    
    # Then
    with self.assertRaises(ValueError):
      load_env_credentials()  # When

  @patch('greetings.views.os.environ')
  @patch('greetings.views.environ.Env', autospec=True)
  def test_should_prefer_load_client_credentials_from_host_machine(self, mock_env, mock_environ) -> None:
    # Given
    expected = {'CLIENT_ID': self.client_id, 'CLIENT_SECRET': self.client_secret}
    mock_environ.get.side_effect = [
      expected['CLIENT_ID'], expected['CLIENT_SECRET']    # Found on host
    ]
    
    # When
    actual = load_env_credentials()
    
    # Then    
    mock_env.read_env.assert_not_called()
    mock_environ.get.assert_has_calls([
      call('CLIENT_ID', None),
      call('CLIENT_SECRET', None)
    ])
    self.assertEqual(actual['CLIENT_ID'], expected['CLIENT_ID'])
    self.assertEqual(actual['CLIENT_SECRET'], expected['CLIENT_SECRET'])

  @patch('greetings.views.os.environ')
  @patch('greetings.views.environ.Env', autospec=True)
  def test_should_fallback_to_load_client_credentials_from_env_file(self,  mock_env, mock_environ) -> None:
    # Given
    expected = {'CLIENT_ID': self.client_id, 'CLIENT_SECRET': self.client_secret}
    mock_environ.get.side_effect = [
      None, None,                                         # Not found on host
      expected['CLIENT_ID'], expected['CLIENT_SECRET']    # Found in env file
    ]
    
    # When
    actual = load_env_credentials()
    
    # Then    
    mock_env.read_env.assert_called_once()
    mock_environ.get.assert_has_calls([
      call('CLIENT_ID', None), call('CLIENT_SECRET', None),   # Try load from host
      call('CLIENT_ID', None),call('CLIENT_SECRET', None)     # Try load from env file
    ])
    self.assertEqual(actual['CLIENT_ID'], expected['CLIENT_ID'])
    self.assertEqual(actual['CLIENT_SECRET'], expected['CLIENT_SECRET'])

  