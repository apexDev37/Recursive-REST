import re

from rest_framework.request import Request
from rest_framework.exceptions import ValidationError

from greetings.utils.constants import GreetingsPathConstants as path 

class GreetingPathValidator:
  @staticmethod
  def validate_param_key_present(request: Request) -> None:
    url_path = request.build_absolute_uri()
    if str(path.GREETING_PARAM_KEY) not in url_path:
      raise ValueError("Key for required query param: greeting is missing.")

class GreetingParamValidator:  
  def __call__(self, value: str) -> None:
    if value.strip() == '':
      raise ValidationError("Value for query param: greeting cannot be blank or empty.")

class GreetingValueValidator:
  def __call__(self, value: str) -> None:
    pattern = r'^[a-zA-Z]+$'
    if not re.match(pattern, value):
      raise ValidationError(
        detail={'greeting_text': 'This field can only contain alphabet chars.'},
        code='invalid_greeting_text')
