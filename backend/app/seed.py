"""幂等创建初始 admin。

用法: python -m app.seed
密码取 env SEED_ADMIN_PASSWORD，默认 lims-admin-1。
"""
import os

from . import security
from .db import SessionLocal
from .models.user import User


def seed(db=None):
    own = db is None
    if own:
        db = SessionLocal()
    try:
        pw = os.environ.get("SEED_ADMIN_PASSWORD", "lims-admin-1")
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    name="管理员",
                    role="admin",
                    password_hash=security.hash_password(pw),
                )
            )
            db.commit()
            print("created admin")
        else:
            print("admin exists, skipped")
    finally:
        if own:
            db.close()


if __name__ == "__main__":
    seed()
