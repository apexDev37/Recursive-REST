"""
Module that defines custom API exceptions and exception
handler for the `greetings` app. 
"""

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


# -------------------------------------------------------------------------------
# Custom DRF Exception Handler
# -------------------------------------------------------------------------------

def custom_exception_handler(exc: APIException, context: dict) -> Response:
  # Call REST framework's default exception handler first,
  # to get the standard error response.
  response = exception_handler(exc, context)
  
  if response is None:
    # If DRF's default response is not generated, handle custom exception
    
    if isinstance(exc, APIException):
      return Response()

  return response   # Return the DRF-generated response if applicable