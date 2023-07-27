from unittest import TestCase
from unittest.mock import call, patch

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.test.client import RequestFactory

from greetings.auth.constants import *
from greetings.auth.credentials import CredentialManagerService
from greetings.auth.services import OAuth2CredentialsService
from greetings.tests.constants import *
from greetings.utils.constants import GreetingsPathConstants as path
from greetings.views import authorize_request, make_recursive_call

BASE_MODULE: str = "greetings.auth"
AUTH_MODULE: str = BASE_MODULE + ".services"
CREDENTIAL_MODULE: str = BASE_MODULE + ".credentials"


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
        self.credential = TEST_CREDENTIAL
        self.encoded_credential = TEST_ENCODED_CREDENTIAL
        self.under_test = CredentialManagerService()

    @patch(f"{CREDENTIAL_MODULE}.os.environ")
    def test_should_raise_exception_for_missing_credentials_on_both_host_and_env_file(
        self, mock_environ
    ) -> None:
        # Given
        mock_environ.get.side_effect = [
            # Not found on host or env
            None,
            None,
            None,
            None,
        ]

        # Then
        with self.assertRaises(ImproperlyConfigured):
            self.under_test._load_env_credentials()  # When

    @patch(f"{CREDENTIAL_MODULE}.os.environ")
    @patch(f"{CREDENTIAL_MODULE}.environ.Env", autospec=True)
    def test_should_prefer_load_client_credentials_from_host_machine(
        self, mock_env, mock_environ
    ) -> None:
        # Given
        expected = {"CLIENT_ID": self.client_id, "CLIENT_SECRET": self.client_secret}
        mock_environ.get.side_effect = [
            # Found on host machine
            expected["CLIENT_ID"],
            expected["CLIENT_SECRET"],
        ]

        # When
        actual = self.under_test._load_env_credentials()

        # Then
        mock_env.read_env.assert_not_called()
        mock_environ.get.assert_has_calls(
            [call("CLIENT_ID", None), call("CLIENT_SECRET", None)]
        )
        self.assertEqual(actual, expected)

    @patch(f"{CREDENTIAL_MODULE}.os.environ")
    @patch(f"{CREDENTIAL_MODULE}.environ.Env", autospec=True)
    def test_should_fallback_to_load_client_credentials_from_env_file(
        self, mock_env, mock_environ
    ) -> None:
        # Given
        expected = {"CLIENT_ID": self.client_id, "CLIENT_SECRET": self.client_secret}
        mock_environ.get.side_effect = [
            # Not found on host machine
            None,
            None,
            # Found in env file
            expected["CLIENT_ID"],
            expected["CLIENT_SECRET"],
        ]

        # When
        actual = self.under_test._load_env_credentials()

        # Then
        mock_env.read_env.assert_called_once()
        mock_environ.get.assert_has_calls(
            [
                # Try load from host
                call("CLIENT_ID", None),
                call("CLIENT_SECRET", None),
                # Try load from env file
                call("CLIENT_ID", None),
                call("CLIENT_SECRET", None),
            ]
        )
        self.assertEqual(actual, expected)

    @patch(f"{CREDENTIAL_MODULE}.base64.b64encode")
    def test_should_base64_encode_the_provided_client_id_and_secret(
        self, mock_b64_encode
    ) -> None:
        # Given
        expected = self.encoded_credential

        # When
        mock_b64_encode.return_value.decode.return_value = expected
        actual = self.under_test._encode_credentials(self.client_id, self.client_secret)

        # Then
        self.assertIsInstance(actual, str)
        mock_b64_encode.assert_called_once_with(self.credential.encode("utf-8"))
        self.assertEqual(actual, expected)


class AuthenticationTestCase(TestCase):
    """
    Test case to test the auth flow process for a DRF view
    to acquire an access token of grant type: "client credentials".

    Behavior:
      GIVEN a registered application's client ID and secret
      WHEN credentials are loaded into the application context
      THEN generate a base64 encoded credential.

      GIVEN a valid base64 encoded credential
      WHEN making an auth request to the Auth server
      THEN include credential in the HTTP Basic Authorization Header.

      GIVEN the expected HTTP requirements from the Auth server
      WHEN provided in an auth request for an access token
      THEN verify a successful JSON response with an access token.
    """

    def setUp(self) -> None:
        self.client_id = TEST_CLIENT_ID
        self.client_secret = TEST_CLIENT_SECRET
        self.credential = TEST_CREDENTIAL
        self.encoded_credential = TEST_ENCODED_CREDENTIAL
        self.under_test = OAuth2CredentialsService()

    @patch(f"{AUTH_MODULE}.requests")
    def test_should_provide_minimum_required_arguments_for_access_token_request(
        self, mock_requests
    ) -> None:
        # Given
        expected = {
            "url": TOKEN_ENDPOINT,
            "headers": {
                "Content-Type": CONTENT_TYPE,
                "Authorization": AUTHORIZATION.format(self.encoded_credential),
            },
            "data": {"grant_type": GRANT_TYPE},
        }

        # When
        self.under_test._request_access_token(self.encoded_credential)
        actual = mock_requests.post.call_args_list[0][1]

        # Then
        mock_requests.post.assert_called_once()
        self.assertEqual(actual["url"], expected["url"])
        self.assertDictContainsSubset(expected["headers"], actual["headers"])
        self.assertDictEqual(actual["data"], expected["data"])

    @patch(f"{AUTH_MODULE}.requests")
    def test_should_retrieve_access_token_response_from_valid_client_request(
        self, mock_requests
    ) -> None:
        # Given
        expected = {
            "access_token": "valid_access_token_from_server",
            "expires_in": 36000,
            "token_type": "Bearer",
            "scope": "read write",
        }

        # When
        mock_requests.post.return_value.json.return_value = expected
        response = self.under_test._request_access_token(self.encoded_credential)
        actual = response.json()

        # Then
        mock_requests.post.assert_called_once()
        self.assertIsInstance(actual, dict)
        self.assertIn("access_token", actual)
        self.assertEqual(actual, expected)


class AuthorizationTestCase(TestCase):
    """
    Test case to test request instances should be authorized with
    the expected Authorization 'Bearer <token>' HTTP header for
    request instances passed to protected DRF API views.
    """

    def setUp(self) -> None:
        factory = RequestFactory()
        self.access_token = TEST_ACCESS_TOKEN
        # Mimic initial request
        self.initial_request = factory.post(
            path=str(path.GREETING_URI) + "greeting",
            headers={"Accept": "application/json"},
        )

    def test_should_authorize_request_argument_for_recursive_view_call(self) -> None:
        # Given
        expected = {"type": "Bearer", "token": self.access_token}

        # When
        actual = authorize_request(self.access_token, self.initial_request)
        auth = actual.environ.get("HTTP_AUTHORIZATION")

        # Then
        self.assertIsInstance(actual, HttpRequest)
        self.assertIsNotNone(auth)
        self.assertEqual(auth.split(" ")[0], expected["type"])
        self.assertEqual(auth.split(" ")[1], expected["token"])

    @patch(f"greetings.views.save_custom_greeting")
    def test_should_make_recursive_view_call_with_authorized_request_argument(
        self, mock_view
    ) -> None:
        # Given
        expected = "Authorization"

        # When
        make_recursive_call(self.initial_request)
        actual = mock_view.call_args[0][0]

        # Then
        mock_view.assert_called_once()
        mock_view.assert_called_once_with(self.initial_request)
        self.assertTrue(actual.environ.get("HTTP_AUTHORIZATION"))
        self.assertIn(expected, actual.headers)
