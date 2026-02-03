from fastapi import Header, HTTPException

from app.core.security import authenticate_api_key


# API Key
def get_principal(x_api_key: str | None = Header(default=None)):
    """
    Minimal principal extraction.
    Replace this with real API-key validation later.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key")
    return authenticate_api_key(x_api_key)
