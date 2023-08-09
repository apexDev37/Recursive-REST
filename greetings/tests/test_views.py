import inspect

from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APISimpleTestCase

from greetings.utils.constants import CUSTOM_GOODBYE
from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.responses import *

BASE_MODULE = "greetings.views"


class RequestTestCase(TestCase):
    """
    Test case for the API view routing, request, and response behavior
    """

    def setUp(self) -> None:
        # Create custom access token for testing purposes only
        test_token = AccessToken.objects.create(
            token="test_access_token",
            user=None,
            expires=timezone.now() + timezone.timedelta(seconds=60),
            scope="read write",
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer {0}".format(test_token.token)
        )

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
        self.assertNotEqual(response.data["greeting"], response.data["goodbye"])
        self.assertEqual(response.data["goodbye"], CUSTOM_GOODBYE)


class CustomResponseTestCase(APISimpleTestCase):
    """
    Test case to test custom wrapper response instances from DRF view.
    """

    def setUp(self) -> None:
        # Test data defined for all tests in single location
        self.typeerror_msg = "missing {0} required positional arguments"
        self.error_defaults = {
            "message": "Error",
            "description": "Failed to save custom greeting submitted by user.",
        }
        self.success_defaults = {
            "message": "Success",
            "description": "Saved custom greeting submitted by user.",
        }
        self.test_data = {
            "status_code": 200,
            "message": "test message",
            "description": "test description",
            "some-data-key": "some_data_value",
        }

    def test_should_return_rest_frameworks_response_instance_to_client(self) -> None:
        # Given
        expected = Response

        # When
        actual = GreetingBaseResponse(
            status_code=200, message="test message", description="test description"
        )

        # Then
        self.assertIsInstance(actual, expected)

    def test_should_omit_data_from_json_response_if_param_not_provided(self) -> None:
        # Given
        expected = count_required_params(GreetingBaseResponse)

        # When
        actual = GreetingBaseResponse(
            status_code=200,
            message="test message",
            description="test description",
        )

        # Then
        self.assertEqual(len(actual.data), expected)

    def test_should_raise_exception_if_required_arguments_are_missing(self) -> None:
        # Given
        required_params = count_required_params(GreetingBaseResponse)

        # Then
        with self.assertRaisesMessage(
            TypeError, self.typeerror_msg.format(required_params)
        ):
            GreetingBaseResponse()  # When

    def test_should_return_json_response_with_provided_actual_arguments(self) -> None:
        # Given
        expected = self.test_data

        actual = GreetingBaseResponse(
            status_code=expected["status_code"],
            message=expected["message"],
            description=expected["description"],
            data={"some-data-key": "some_data_value"},
        )

        self.assertEqual(len(actual.data), len(expected))
        self.assertDictEqual(actual.data, expected)

    def test_should_return_error_default_values_on_non_provided_actual_arguments(
        self,
    ) -> None:
        # Given
        expected = self.error_defaults

        # When
        actual = GreetingErrorResponse()

        self.assertEqual(actual.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(actual.data["message"], expected["message"])
        self.assertEqual(actual.data["description"], expected["description"])

    def test_should_return_success_default_values_on_non_provided_actual_arguments(
        self,
    ) -> None:
        # Given
        expected = self.success_defaults

        # When
        actual = GreetingSuccessResponse()

        # Then
        self.assertEqual(actual.status_code, status.HTTP_200_OK)
        self.assertEqual(actual.data["message"], expected["message"])
        self.assertEqual(actual.data["description"], expected["description"])


# -------------------------------------------------------------------------------
# Test utility functions
# -------------------------------------------------------------------------------


def count_required_params(cls: GreetingBaseResponse) -> int:
    constructor = cls.__init__
    signature = inspect.signature(constructor)
    return sum(
        1
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty and param.name != "self"
    )
