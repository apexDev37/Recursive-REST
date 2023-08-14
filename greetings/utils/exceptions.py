"""
Module that defines custom API exceptions and exception
handler for the `greetings` app. 
"""

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from greetings.utils.responses import GreetingErrorResponse


# -------------------------------------------------------------------------------
# Custom DRF Exceptions
# -------------------------------------------------------------------------------

class RequiredParamMissing(APIException):
  """
  Custom `APIException` raised when a client request does not 
  include required `greeting` param.
  """
  
  status_code = 400
  default_detail = 'Required query param key is missing in URL.'
  default_code = 'required_param_missing'


# -------------------------------------------------------------------------------
# Custom DRF Exception Handler
# -------------------------------------------------------------------------------

def custom_exception_handler(exc: APIException, context: dict) -> Response:
  # Call REST framework's default exception handler first,
  # to get the standard error response.
  # response = exception_handler(exc, context)

  if isinstance(exc, APIException):
    return GreetingErrorResponse(
      status_code=exc.status_code,
      message=exc.default_code,
      description=str(exc.detail))
  
  # if response is None:
  #   # If DRF's default response is not generated, handle custom exception
    
  #   if isinstance(exc, RequiredParamMissing):
  #     return GreetingErrorResponse(
  #       status_code=exc.status_code,
  #       message=exc.get_codes(),
  #       description=str(exc.detail))

  return exception_handler(exc, context)   # Return the DRF-generated response if applicable