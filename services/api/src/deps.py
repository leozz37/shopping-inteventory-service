from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from security.jwt import decode_token

security = HTTPBearer()


def require_user(creds=Depends(security)):
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload
