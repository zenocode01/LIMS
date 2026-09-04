from conftest import auth_hdr


def test_login_ok(client):
    r = client.post("/api/auth/login", json={"username": "eng", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_login_bad_password(client):
    r = client.post("/api/auth/login", json={"username": "eng", "password": "nope"})
    assert r.status_code == 401


def test_me_with_token(client):
    tok = client.post("/api/auth/login", json={"username": "eng", "password": "pw"}).json()["access_token"]
    r = client.get("/api/auth/me", headers=auth_hdr(tok))
    assert r.status_code == 200
    assert r.json()["role"] == "engineer"


def test_me_without_token(client):
    assert client.get("/api/auth/me").status_code == 401
