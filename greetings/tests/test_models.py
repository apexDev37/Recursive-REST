from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from greetings.models import Greeting


class GreetingTestCase(TestCase):
    """Tests for the Greeting model"""

    def setUp(self) -> None:
        BASE_GREETING_TEXT = "Hello, tests!"
        self.base_greeting = Greeting.objects.create(greeting_text=BASE_GREETING_TEXT)

    def test_should_raise_exception_when_creating_instance_without_greeting_text_field(
        self,
    ) -> None:
        """Validation test on model to ensure that the greeting_text field is valid."""

        with self.assertRaises(ValidationError):
            invalid_greeting = Greeting.objects.create()

    def test_should_generate_unique_uuid_for_new_greeting_instance(self) -> None:
        """Validation test to ensure that all new instances have a unique uuid field."""

        # given
        existing_uuid = self.base_greeting.greeting_id

        # when
        new_greeting = Greeting.objects.create(greeting_text="new greeting")
        new_uuid = new_greeting.greeting_id

        # then
        self.assertNotEqual(new_uuid, existing_uuid)

    def test_should_raise_exception_when_trying_to_save_a_non_unique_greeting_text(
        self,
    ) -> None:
        """Validation test to ensure that all persisted greetings have a unique `greeting_text`."""

        # Given
        duplicate_greeting_text = "Hello, tests!"

        # Then
        with self.assertRaises(IntegrityError):
            Greeting.objects.create(greeting_text=duplicate_greeting_text)
