import os
from hmac import compare_digest

from fastapi import Header, HTTPException, status

API_KEY_HEADER = "X-API-KEY"

def get_api_key(x_api_key: str = Header(None, alias="X-API-Key", description="API key for mutating endpoints")):
    """FastAPI dependency that validates the API key.

    * In development (ENV != "production") the dependency is a no‑op – the
      endpoint remains publicly accessible.
    * In production (ENV == "production") the environment variable
      ``CORTANA_API_KEY`` **must** be set. Missing or mismatched keys result in
      ``401 Unauthorized`` or ``403 Forbidden`` respectively.
    """
    env = os.getenv("ENV", "development")
    expected_key = os.getenv("CORTANA_API_KEY")
    if env != "production":
        # Development mode – allow unauthenticated access
        return None
    if expected_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration error: CORTANA_API_KEY not set",
        )
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    if not compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return x_api_key
