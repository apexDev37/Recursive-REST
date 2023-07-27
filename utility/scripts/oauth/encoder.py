"""
Simple python script to encode client credentials: 
>>> client_id and client_secret.

Utility tool to base64 encode credentials from host 
environment variables. Use encoded credential for 
HTTP base authentication request.

[Example]

  1. Set env variables
    $ export CLIENT_ID=your_client_id
    $ export CLIENT_SECRET=your_client_secret
  2. Run script with command: `python3 encoder.py`
    $ python3 encoder.py
  3. Set output as env variable
    $ export CREDENTIAL=generated_encoded_credential
"""

import base64
import binascii
import os


def main():
    """Load env variables and print base64 encoded credential."""

    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    if not is_credentials_set(client_id, client_secret):
        print('Set credentials "CLIENT_ID" and "CLIENT_SECRET" as env variables.')
        return

    try:
        credential = f"{client_id}:{client_secret}"
        encoded_credential = base64.b64encode(credential.encode("utf-8"))
        print("credential: ", encoded_credential.decode())
    except binascii.Error as exc:
        print("Failure on encoding credentials! ", exc)


def is_credentials_set(client_id: str, client_secret: str) -> bool:
    """Verify env loaded variables are set and not empty."""
    return client_id is not None or client_secret is not None


if __name__ == "__main__":
    main()
