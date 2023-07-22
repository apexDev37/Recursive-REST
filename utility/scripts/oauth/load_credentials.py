import os
from pathlib import Path

import environ


def main() -> None:
  
  # Load dir
  DIR = Path(__file__).resolve().parent.parent.parent.parent
  print('path: ', DIR)
  
  # Prefer load from host machine
  client_id = os.environ.get('CLIENT_ID', None)
  client_secret = os.environ.get('CLIENT_SECRET', None)
  
  if client_id is None and client_secret is None:
    print('Credentials not found on host machine.')
    
    # Load from env file
    print('Try \load credentials from env file...')
    environ.Env.read_env(os.path.join(DIR, ".envs", "credentials.env"))
    client_id = os.environ.get('CLIENT_ID', None)
    client_secret = os.environ.get('CLIENT_SECRET', None)
  
    if client_id is None and client_secret is None:
      print('Credentials not found on both host machine or env file',
            'Set required env credentials on either your host machine or env file.')
    else:
      print('Credentials found in env file.')
      print(f'client_id: {client_id} \nclient_secret: {client_secret}')
  
  else:
    print('Credentials found on host machine.')
    print(f'client_id: {client_id} \nclient_secret: {client_secret}')
    

if __name__ == "__main__":
  main()
