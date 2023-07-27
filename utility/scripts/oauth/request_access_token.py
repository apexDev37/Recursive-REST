# pylint: disable=C0116

"""
Python script to request an access token using the
grant_type: `client credentials`.

[Requirements]
  - base64 encoded "CREDENTIAL" env variable.

Make an access token request from an Auth server. Uses encoded 
credential for a HTTP basic authentication request.

[Example curl request]

  curl
    -X POST
    -H "Authorization: Basic ${CREDENTIAL}"
    -H "Cache-Control: no-cache"
    -H "Content-Type: application/x-www-form-urlencoded"
    "http://127.0.0.1:8000/o/token/"
    -d "grant_type=client_credentials"

@see    
"""

import os

import requests
from requests.models import Response

TOKEN_ENDPOINT: str = "http://127.0.0.1:8000/o/token/"
CONTENT_TYPE: str = "application/x-www-form-urlencoded"
CACHE_CONTROL: str = "no-cache"
AUTHORIZATION: str = "Basic {0}"
GRANT_TYPE: str = "client_credentials"


def main() -> None:
    encoded_cred = os.environ.get("CREDENTIAL", None)
    if not is_credential_set(encoded_cred):
        print("Set environment variable CREDENTIAL.")
        return

    # Make request
    response = requests.post(
        url=TOKEN_ENDPOINT,
        headers=get_headers(encoded_cred),
        data=get_data(),
        timeout=10,
    )

    output_formatted_response(response)


def is_credential_set(credential: str) -> bool:
    return credential is not None or not credential.strip()


def get_headers(credential: str) -> dict[str, str]:
    return {
        "Content-Type": CONTENT_TYPE,
        "Cache-Control": CACHE_CONTROL,
        "Authorization": AUTHORIZATION.format(credential),
    }


def get_data() -> dict[str, str]:
    return {"grant_type": GRANT_TYPE}


def output_formatted_response(response: Response) -> None:
    data = response.json()
    print("response: ", data)


if __name__ == "__main__":
    main()
