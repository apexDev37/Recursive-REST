"""
Module that defines custom response DTO classes to
send customizable JSON responses to client. 
"""

from rest_framework.response import Response

class CustomGreetingResponse(Response):
  """
  Custom DTO class to define a general custom JSON response object.
  """

  def __init__(
    self,
    status_code: int,
    message: str,
    description: str,
    data: dict = None,
  ) -> None:
    super().__init__(data=data, status=status_code)
    
    self.data = {
      'status_code': status_code,
      'message': message,
      'description': description,
      **(data or {}),
    }
