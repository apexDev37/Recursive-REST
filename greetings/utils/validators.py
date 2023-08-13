import re

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from greetings.utils.constants import GreetingsPathConstants as path
from greetings.utils.exceptions import RequiredParamMissing


class GreetingParamValidator:
    """
    Custom validator class to validate that given request URL
    has the query parameter key (`?greeting=`) for a custom greeting.

    Behavior::
      Check if `greeting` query param key is in request URL.
      Raise `exception` if query param key is not found in URL.
      Return the `greeting` query param value if key is found in URL.
    """

    def __new__(self, request: Request) -> str:
        url = request.build_absolute_uri()
        if str(path.GREETING_PARAM_KEY) not in url:
            raise RequiredParamMissing("Required query param key `greeting` is missing in URL.")
        return request.query_params["greeting"]


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
