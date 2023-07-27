import os
import logging
from pathlib import Path

import environ


DIR = Path(__file__).resolve().parent.parent.parent.parent
CREDENTIALS_ENV: str = 'credentials.env'

logger = logging.getLogger(__name__)
env = environ.Env(
  # set casting, default value
  CLIENT_ID=(str, None),
  CLIENT_SECRET=(str, None)
)

def main() -> None:
  
  client_id, client_secret = load_from_host()
  
  if not credentials_set(client_id, client_secret):
    logger.warning('Credentials not found on host machine!')
    client_id, client_secret = load_from_env_file()
  
    if not credentials_set(client_id, client_secret):
      logger.warning('Credentials not found in env file!')
      logger.info('Configure required client credentials on host machine or env file.')
    else:
      logger.info('Credentials loaded from env file.')
  
  logger.info(f'Credentials -> client_id: {client_id}, client secret: {client_secret}')     

def credentials_set(id: str, secret: str) -> bool:
  return id is not None and secret is not None

def load_from_host() -> str:
  logger.debug('Loading client credentials from host machine.')
  return load_env_credentials()

def load_from_env_file() -> str:
  logger.debug('Loading client credentials from env file.')
  environ.Env.read_env(os.path.join(DIR, ".envs", CREDENTIALS_ENV))
  return load_env_credentials()
  
def load_env_credentials() -> str:
  client_id = env('CLIENT_ID')
  client_secret = env('CLIENT_SECRET')
  return client_id, client_secret

if __name__ == "__main__":
  main()
