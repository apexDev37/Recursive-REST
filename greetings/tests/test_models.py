import uuid

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from greetings.models import Greeting


class GreetingTestCase(TestCase):
    """
    Tests for the Greeting model
    """

    def setUp(self) -> None:
        self.BASE_GREETING_TEXT = "Hello"
        self.base_greeting = Greeting.objects.create(
            greeting_text=self.BASE_GREETING_TEXT
        )

    def test_should_raise_exception_when_creating_instance_without_greeting_text_field_set(
        self,
    ) -> None:
        """Test to validate that a value is assigned to the greeting_text field."""

        # Then
        with self.assertRaises(ValidationError):
            invalid_greeting = Greeting.objects.create()  # When

    def test_should_generate_unique_uuid_for_new_greeting_instance(self) -> None:
        """Test to validate all new instances have a unique uuid field."""

        # given
        existing_uuid = self.base_greeting.greeting_id

        # when
        greeting = Greeting.objects.create(greeting_text="new")
        new_uuid = greeting.greeting_id

        # then
        self.assertIsInstance(new_uuid, uuid.UUID)
        self.assertNotEqual(new_uuid, existing_uuid)

    def test_should_raise_exception_when_trying_to_save_a_non_unique_greeting_text(
        self,
    ) -> None:
        """Validation test to ensure that all persisted greetings have a unique `greeting_text`."""

        # Given
        duplicate = self.BASE_GREETING_TEXT

        # Then
        with self.assertRaises(ValidationError):
            Greeting.objects.create(greeting_text=duplicate)
