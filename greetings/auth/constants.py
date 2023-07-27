"""
Constants for the auth module. Defines all OAuth
related constants to be reused in the greetings app.

@refactor   Consider using an StrEnum class.
"""


# OAuth Endpoints
TOKEN_ENDPOINT: str = "http://127.0.0.1:8000/o/token/"

# Request Header values
CONTENT_TYPE: str = "application/x-www-form-urlencoded"
CACHE_CONTROL: str = "no-cache"
AUTHORIZATION: str = "Basic {0}"

# Request Data values
GRANT_TYPE: str = "client_credentials"
