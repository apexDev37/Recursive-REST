import re

from rest_framework.request import Request

class GreetingPathValidator:
  @staticmethod
  def validate_param_key_present(request: Request) -> None:
    query_param_key = '?greeting='
    url_path = request.build_absolute_uri()
    if query_param_key not in url_path:
      raise ValueError("Key for required query param: greeting is missing.")

class GreetingParamValidator:  
  @staticmethod
  def validate_not_blank(value: str) -> None:
    if value.strip() == '':
      raise ValueError("Value for query param: greeting cannot be blank or empty.")

class GreetingValueValidator:
  @staticmethod
  def validate_param_value(value: str) -> None:
    pattern = r'^[a-zA-Z]+$'
    if not re.match(pattern, value):
      raise ValueError("Value for query param: greeting cannot contain non alphabetic chars.")
