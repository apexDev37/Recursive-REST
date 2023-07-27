"""
Module for OAuth2 services for the greetings app.
"""

import requests
from rest_framework.response import Response

from greetings.auth.constants import *
from greetings.auth.credentials import CredentialManagerService


class OAuth2CredentialsService:
    """
    Singleton service to encapsulate logic to get an access token.
    """

    _instance = None
    _credential_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OAuth2CredentialsService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._credential_service = CredentialManagerService()

    def get_access_token(self) -> dict:
        encoded_credential = self._credential_service.get_encoded_credential()
        response = self._request_access_token(encoded_credential)
        return response.json()["access_token"]

    def _request_access_token(self, encoded_credential: str) -> Response:
        response = requests.post(
            url=TOKEN_ENDPOINT,
            headers=self._get_headers(encoded_credential),
            data=self._get_data(),
            timeout=10,
        )
        return response

    def _get_headers(self, credential: str) -> dict[str, str]:
        return {
            # Add request headers here
            "Content-Type": CONTENT_TYPE,
            "Cache-Control": CACHE_CONTROL,
            "Authorization": AUTHORIZATION.format(credential),
        }

    def _get_data(self) -> dict[str, str]:
        return {"grant_type": GRANT_TYPE}
