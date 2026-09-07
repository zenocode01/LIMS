import jwt
import pytest

from app import security


def test_password_roundtrip():
    h = security.hash_password("s3cret")
    assert security.verify_password("s3cret", h)
    assert not security.verify_password("wrong", h)


def test_password_hash_not_plaintext():
    assert security.hash_password("s3cret") != "s3cret"


def test_jwt_roundtrip():
    tok = security.create_access_token(42)
    payload = security.decode_token(tok)
    assert payload["sub"] == "42"


def test_jwt_expired():
    old = security._make_token(1, exp_seconds=-10)
    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_token(old)
