from enum import Enum

from config.settings.base import API_VERSION

api_version: str = API_VERSION.GREETINGS


class GreetingsPathConstants(Enum):
    """
    Enum to define url paths, endpoints, and params
    in a centralized location for the 'greetings' app

    @upgrade  `StrEnum` in python 3.11.
    """

    GREETING_ENDPOINT: str = f"/greetings/{api_version}greeting/"
    GREETING_PARAM_KEY: str = "?greeting="
    GREETING_URI: str = f"/greetings/{api_version}greeting/?greeting="

    def __str__(self) -> str:
        return self.value
