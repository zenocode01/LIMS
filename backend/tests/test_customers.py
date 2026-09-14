from conftest import auth_hdr


def _tok(client, u="biz"):
    return client.post("/api/auth/login", json={"username": u, "password": "pw"}).json()["access_token"]


def test_engineer_no_access(client):
    h = auth_hdr(_tok(client, "eng"))
    assert client.get("/api/customers", headers=h).status_code == 403
    assert client.post("/api/customers", json={"name": "X"}, headers=h).status_code == 403


def test_business_crud_and_numbering(client):
    h = auth_hdr(_tok(client, "biz"))
    r = client.post(
        "/api/customers",
        json={"name": "华为终端", "industry": "消费电子", "contact_name": "李工", "contact_phone": "13800000000"},
        headers=h,
    )
    assert r.status_code == 201
    c1 = r.json()
    assert c1["code"] == "CU-001"

    r = client.post("/api/customers", json={"name": "大疆创新", "industry": "无人机"}, headers=h)
    c2 = r.json()
    assert c2["code"] == "CU-002"

    # 同名 409
    assert client.post("/api/customers", json={"name": "华为终端"}, headers=h).status_code == 409

    # 列表 + 搜索
    r = client.get("/api/customers", headers=h)
    assert r.status_code == 200 and len(r.json()) == 2
    r = client.get("/api/customers", params={"q": "大疆"}, headers=h)
    assert [c["code"] for c in r.json()] == ["CU-002"]
    r = client.get("/api/customers", params={"q": "CU-001"}, headers=h)
    assert [c["name"] for c in r.json()] == ["华为终端"]
    assert client.get("/api/customers", params={"q": "不存在"}, headers=h).json() == []

    # 详情
    assert client.get(f"/api/customers/{c1['id']}", headers=h).json()["name"] == "华为终端"
    assert client.get("/api/customers/9999", headers=h).status_code == 404

    # 更新（含改名冲突 409）
    r = client.patch(f"/api/customers/{c1['id']}", json={"remark": "重点客户"}, headers=h)
    assert r.json()["remark"] == "重点客户"
    assert client.patch(f"/api/customers/{c1['id']}", json={"name": "大疆创新"}, headers=h).status_code == 409
    r = client.patch(f"/api/customers/{c1['id']}", json={"name": "华为终端科技"}, headers=h)
    assert r.json()["name"] == "华为终端科技"

    # 传 null = 清空字段（不是保留旧值）
    r = client.patch(f"/api/customers/{c1['id']}", json={"industry": None, "remark": None}, headers=h)
    assert r.json()["industry"] is None and r.json()["remark"] is None

    # 删除
    assert client.delete(f"/api/customers/{c2['id']}", headers=h).status_code == 204
    assert client.get(f"/api/customers/{c2['id']}", headers=h).status_code == 404
    assert client.delete(f"/api/customers/{c2['id']}", headers=h).status_code == 404


def test_admin_read_only(client):
    h = auth_hdr(_tok(client, "admin"))
    client.post("/api/customers", json={"name": "小米通讯"}, headers=auth_hdr(_tok(client, "biz")))
    r = client.get("/api/customers", headers=h)
    assert r.status_code == 200 and r.json()[0]["name"] == "小米通讯"
    # 管理不可写
    assert client.post("/api/customers", json={"name": "X"}, headers=h).status_code == 403
    assert client.patch(f"/api/customers/{r.json()[0]['id']}", json={"remark": "x"}, headers=h).status_code == 403
    assert client.delete(f"/api/customers/{r.json()[0]['id']}", headers=h).status_code == 403


def test_unauthenticated(client):
    # HTTPBearer auto_error=False → 无凭证时 deps 抛 401
    assert client.get("/api/customers").status_code == 401
