"""
Module that defines custom response DTO classes to
send customizable JSON responses to client. 
"""

from rest_framework import status
from rest_framework.response import Response


class GreetingBaseResponse(Response):
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
            "status_code": status_code,
            "message": message,
            "description": description,
            **(data or {}),
        }


class GreetingErrorResponse(GreetingBaseResponse):
    """
    Specialized wrapper class for a generic error `Response`.
    Use default values, if no arguments are passed to the class.

    @inherits  CustomGreetingResponse
    """

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "Error",
        description: str = "Failed to save custom greeting submitted by user.",
        data: dict = None,
    ) -> None:
        super().__init__(status_code, message, description, data)


class GreetingSuccessResponse(GreetingBaseResponse):
    """
    Specialized wrapper class for a generic success `Response`.

    @inherits  CustomGreetingResponse
    """

    def __init__(
        self,
        status_code: int = status.HTTP_200_OK,
        message: str = "Success",
        description: str = "Saved custom greeting submitted by user.",
        data: dict = None,
    ) -> None:
        super().__init__(status_code, message, description, data)
