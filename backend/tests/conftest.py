import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401  (确保全部 model 注册到 Base.metadata, create_all 不漏表)
from app import security
from app.db import Base, get_db
from app.main import create_app
from app.models.user import User


@pytest.fixture()
def db_session(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    eng = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    session = sessionmaker(bind=eng, expire_on_commit=False)
    s = session()
    yield s
    s.close()


@pytest.fixture()
def client(db_session):
    app = create_app()

    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    # seed 三个角色用户
    for uname, role in [("admin", "admin"), ("biz", "business"), ("eng", "engineer")]:
        db_session.add(
            User(username=uname, password_hash=security.hash_password("pw"), name=uname, role=role)
        )
    db_session.commit()
    return TestClient(app)


@pytest.fixture()
def admin_token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "pw"})
    return r.json()["access_token"]


def auth_hdr(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}"}
