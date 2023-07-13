import re

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from greetings.utils.constants import GreetingsPathConstants as path


class GreetingPathValidator:
    """
    Validator class to ensure that a required param key
    is present in the request path.
    """

    @staticmethod
    def validate_param_key_present(request: Request) -> None:
        url_path = request.build_absolute_uri()
        if str(path.GREETING_PARAM_KEY) not in url_path:
            raise ValueError("Key for required query param: greeting is missing.")


class AlphaCharsValidator:
    """
    Callable validator class for the greeting model.
    Validate that a models.CharField() only contains alphabetical chars.
    """

    def __call__(self, value: str) -> None:
        pattern = r"^[a-zA-Z]+$"
        if not re.match(pattern, value):
            raise ValidationError(
                detail={"greeting_text": "This field can only contain alphabet chars."},
                code="invalid_greeting_text",
            )
