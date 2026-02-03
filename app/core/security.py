from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass(frozen=True)
class Principal:
    caller_id: str
    org_id: int
    roles: tuple[str, ...]
    scopes: tuple[str, ...]


# Demo mapping
API_KEY_TO_PRINCIPAL = {
    # api_key: (org_id, roles, scopes)
    "dev-key-1": (1, ("hr",), ("employee.read",)),
    "dev-key-2": (2, ("admin",), ("employee.read", "employee.write")),
}


def authenticate_api_key(api_key: str) -> Principal:
    cfg = API_KEY_TO_PRINCIPAL.get(api_key)
    if cfg is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    org_id, roles, scopes = cfg
    return Principal(
        caller_id=api_key,  # stable id for rate limiting + logging
        org_id=org_id,
        roles=roles,
        scopes=scopes,
    )
