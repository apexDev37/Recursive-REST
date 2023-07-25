"""
This module provides singleton service classes for reusable Model services.
The Singleton Pattern supports a centralized and reusable design. It avoids
unnecessary instantiation and ensures that only a single instance is reused
throughout an application.

@see  /add/reference
"""

import os
import base64
import environ
import logging
import requests
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response
from typing import Self

from config.settings.base import BASE_DIR
from greetings.models import Greeting


TOKEN_ENDPOINT: str = 'http://127.0.0.1:8000/o/token/'
CONTENT_TYPE: str = "application/x-www-form-urlencoded"
CACHE_CONTROL: str = "no-cache"
AUTHORIZATION: str = "Basic {0}"
GRANT_TYPE: str = "client_credentials"

logger = logging.getLogger(__name__)

class GreetingService:
    """
    Singleton service to encapsulate custom logic for the Greeting model.
    """

    instance = None

    def __new__(cls) -> Self:
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def create_and_save(custom_greeting: str) -> None:
        greeting = Greeting(greeting_text=custom_greeting)
        greeting.save()
        logger.info(f'Save custom greeting "{greeting.greeting_text}" from user.')


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
    return response.json()['access_token']

  def _request_access_token(self, encoded_credential: str) -> Response:
    response = requests.post(
      url=TOKEN_ENDPOINT,
      headers=self._get_headers(encoded_credential),
      data=self._get_data(),
      timeout=10
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


class CredentialManagerService:
  """
  Singleton service to load, encode, and manage OAuth client credentials.
  """

  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(CredentialManagerService, cls).__new__(cls)
      cls._instance._initialize()
    return cls._instance

  def _initialize(self):
    pass
  
  def get_encoded_credential(self) -> str:
    credentials = self._load_env_credentials()
    encoded_credential = self._encode_credentials(
      credentials['CLIENT_ID'], credentials['CLIENT_SECRET'])
    return encoded_credential
  
  def _load_env_credentials(self) -> tuple[str]:
    client_id, client_secret = self._load_envs()
    
    if not self._is_credentials_set(client_id, client_secret):
      environ.Env.read_env(os.path.join(BASE_DIR, ".envs", "credentials.env"))
      client_id, client_secret = self._load_envs()

    if not self._is_credentials_set(client_id, client_secret):
      raise ImproperlyConfigured('Client credentials not found on host machine or env file.')
    
    return {'CLIENT_ID': client_id, 'CLIENT_SECRET': client_secret}

  def _load_envs(self) -> str:
    client_id = os.environ.get('CLIENT_ID', None)
    client_secret = os.environ.get('CLIENT_SECRET', None)
    return client_id, client_secret

  def _is_credentials_set(self, id: str, secret: str) -> bool:
    return id is not None and secret is not None

  def _encode_credentials(self, client_id: str, client_secret: str) -> str:
    credential = f'{client_id}:{client_secret}'
    encoded_credential = base64.b64encode(credential.encode('utf-8'))
    return encoded_credential.decode()
