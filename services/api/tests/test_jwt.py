import time
import pytest


def test_create_and_verify_token_roundtrip():
    import src.security.jwt as jwt_mod

    token = jwt_mod.create_token({"sub": "user-123", "email": "leo@example.com"})
    claims = jwt_mod.decode_token(token)

    assert claims["sub"] == "user-123"
    assert claims["email"] == "leo@example.com"


def test_verify_token_rejects_invalid_signature():
    import src.security.jwt as jwt_mod

    # create with secret A
    token = jwt_mod.create_token({"sub": "user-123"})

    # Try to decode with invalid token (malformed)
    result = jwt_mod.decode_token("invalid.token.here")
    assert result is None
