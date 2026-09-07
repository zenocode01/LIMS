from conftest import auth_hdr


def _tok(client, u="admin"):
    return client.post("/api/auth/login", json={"username": u, "password": "pw"}).json()["access_token"]


def test_admin_list_users(client):
    r = client.get("/api/users", headers=auth_hdr(_tok(client, "admin")))
    assert r.status_code == 200 and len(r.json()) >= 3
    assert "password" not in r.json()[0]  # 不泄漏密码


def test_engineer_forbidden(client):
    r = client.get("/api/users", headers=auth_hdr(_tok(client, "eng")))
    assert r.status_code == 403


def test_business_forbidden(client):
    r = client.post(
        "/api/users",
        json={"username": "x", "password": "p", "name": "x"},
        headers=auth_hdr(_tok(client, "biz")),
    )
    assert r.status_code == 403


def test_admin_create_and_patch(client):
    h = auth_hdr(_tok(client, "admin"))
    r = client.post(
        "/api/users",
        json={"username": "eng2", "password": "p2", "name": "E2", "role": "engineer"},
        headers=h,
    )
    assert r.status_code == 201
    uid = r.json()["id"]
    r = client.patch(f"/api/users/{uid}", json={"is_active": False}, headers=h)
    assert r.json()["is_active"] is False
    # 禁用后登录 403
    assert (
        client.post("/api/auth/login", json={"username": "eng2", "password": "p2"}).status_code
        == 403
    )


def test_seed_idempotent(db_session):
    from app.models.user import User
    from app.seed import seed

    seed(db_session)
    seed(db_session)
    assert db_session.query(User).filter(User.username == "admin").count() == 1
