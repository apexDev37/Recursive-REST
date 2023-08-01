"""
Module that defines custom response DTO classes to
send customizable JSON responses to client. 
"""

from typing import Any

class CustomGreetingResponse:
  """
  Custom DTO class to define a general custom JSON response object.
  """
  
  def __init__(
    self,
    status_code: int,
    message: str,
    description: str,
    data: dict = None) -> None:
      self.status_code = status_code
      self.message = message
      self.description = description
      self.data = data or {}

  def prepare(self) -> dict[str, Any]:
    return {
      'status_code': self.status_code,
      'message': self.message,
      'description': self.description,
      **self.data,
    }
