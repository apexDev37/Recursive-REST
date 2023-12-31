from unittest import TestCase

from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from greetings.utils.validators import AlphaCharsValidator, GreetingParamValidator


class CustomValidatorTestCase(TestCase):
    """
    Test case to test all custom validators for `greetings` app
    """

    def setUp(self) -> None:
        self.factory = APIRequestFactory(format="json")

    def test_should_raise_exception_when_greeting_param_key_not_found_in_url(
        self,
    ) -> None:
        # Given
        request = prepare_request(greeting=None)
        expected = ValueError

        # Then
        self.assertFalse(request.META["QUERY_STRING"])
        with self.assertRaises(expected):
            GreetingParamValidator(request)  # When

    def test_should_return_greeting_when_greeting_param_key_found_in_url(self) -> None:
        # Given
        expected = "testing"
        request = prepare_request(greeting=expected)

        # When
        actual = GreetingParamValidator(request)

        # Then
        self.assertTrue(request.META["QUERY_STRING"])
        self.assertIsInstance(actual, str)
        self.assertEqual(actual, expected)

    def test_should_raise_exception_for_string_with_non_alphabetic_chars(self) -> None:
        # Given
        greeting = "$_greeting37"
        expected = ValidationError
        validator = AlphaCharsValidator()

        # Then
        self.assertIsInstance(greeting, str)
        with self.assertRaises(expected):
            validator(value=greeting)


# -------------------------------------------------------------------------------
# Test utility functions
# -------------------------------------------------------------------------------


def prepare_request(greeting: str = None) -> Request:
    """
    Create and mimic request instance passed to validator from view.
    NB: Should be instance of `rest_framework.request.Request`
    """

    factory = APIRequestFactory(format="json")
    url = reverse("greetings:save_custom_greeting")
    request = factory.post(path=url)

    if greeting:
        query_string = f"greeting={greeting}"
        request = factory.post(path=url, QUERY_STRING=query_string)

    return Request(request=request)
