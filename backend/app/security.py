import time
from typing import Any

import bcrypt
import jwt

from .config import get_settings


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def _make_token(user_id: int, exp_seconds: int) -> str:
    s = get_settings()
    return jwt.encode(
        {"sub": str(user_id), "exp": int(time.time()) + exp_seconds},
        s.jwt_secret,
        algorithm="HS256",
    )


def create_access_token(user_id: int) -> str:
    return _make_token(user_id, get_settings().jwt_expire_min * 60)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
