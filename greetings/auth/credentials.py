"""
Module for the Credential Manager service.
"""

import os
import base64
import environ
import logging
from django.core.exceptions import ImproperlyConfigured

from config.settings.base import BASE_DIR

logger = logging.getLogger(__name__)

class CredentialManagerService:
  """
  Singleton service to manage OAuth client credentials.

  Behavior::
    - Loads client credentials from host machine or env file.
    - Raises ImproperlyConfigured exception for credentials not found.
    - Returns a base64 encoded client id and secret credential.  
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
    client_id, client_secret = self._load_from_host()
    
    if not self._is_credentials_set(client_id, client_secret):
      client_id, client_secret = self._load_from_env_file()
    if not self._is_credentials_set(client_id, client_secret):
      raise ImproperlyConfigured('Client credentials not found on host machine or env file.')
    
    return {'CLIENT_ID': client_id, 'CLIENT_SECRET': client_secret}

  def _load_from_host(self) -> str:
    logger.debug('Loading client credentials from host machine.')
    return self._load_envs()

  def _load_from_env_file(self) -> str:
    logger.debug('Loading client credentials from env file.')
    environ.Env.read_env(os.path.join(BASE_DIR, ".envs", "credentials.env"))
    return self._load_envs()

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
