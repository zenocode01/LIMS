from conftest import auth_hdr

ITEMS = [
    {"item_name": "辐射发射", "qty": 2, "unit_price": 3000},
    {"item_name": "辐射抗扰度", "qty": 1, "unit_price": 5000},
]  # 合计 11000


def _tok(client, u="biz"):
    return client.post("/api/auth/login", json={"username": u, "password": "pw"}).json()["access_token"]


def _mk_customer(client, tok, name="测试客户"):
    r = client.post("/api/customers", json={"name": name}, headers=auth_hdr(tok))
    assert r.status_code == 201
    return r.json()["id"]


def _mk_quote(client, tok, cust, items=None):
    r = client.post(
        "/api/quotations",
        json={"customer_id": cust, "items": items or ITEMS},
        headers=auth_hdr(tok),
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_rbac(client):
    cust = _mk_customer(client, _tok(client, "biz"))
    # 工程师无权限
    h_eng = auth_hdr(_tok(client, "eng"))
    assert client.get("/api/quotations", headers=h_eng).status_code == 403
    assert client.post("/api/quotations", json={"customer_id": cust, "items": ITEMS}, headers=h_eng).status_code == 403
    # 管理只读
    h_adm = auth_hdr(_tok(client, "admin"))
    q = _mk_quote(client, _tok(client, "biz"), cust)
    assert client.get(f"/api/quotations/{q['id']}", headers=h_adm).status_code == 200
    assert client.post(f"/api/quotations/{q['id']}/issue", headers=h_adm).status_code == 403
    assert client.patch(f"/api/quotations/{q['id']}", json={"items": ITEMS, "remark": "x"}, headers=h_adm).status_code == 403
    # 未认证
    assert client.get("/api/quotations").status_code == 401


def test_create_numbering_and_amounts(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    q1 = _mk_quote(client, tok, cust)
    assert q1["code"].startswith("Q-") and q1["code"].endswith("-001")
    assert q1["status"] == "draft"
    assert [i["amount"] for i in q1["items"]] == [6000.0, 5000.0]
    assert q1["total"] == 11000.0
    q2 = _mk_quote(client, tok, cust)
    assert q2["code"].endswith("-002")
    # 客户不存在
    assert client.post("/api/quotations", json={"customer_id": 9999, "items": ITEMS}, headers=auth_hdr(tok)).status_code == 404
    # 空明细 422
    assert client.post("/api/quotations", json={"customer_id": cust, "items": []}, headers=auth_hdr(tok)).status_code == 422


def test_state_machine(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    q = _mk_quote(client, tok, cust)
    h = auth_hdr(tok)
    # 非法迁移: 草稿直接落单 / 草稿取消后再发出
    assert client.post(f"/api/quotations/{q['id']}/finalize", headers=h).status_code == 409
    # happy path: 草稿 → 发出 → 落单
    r = client.post(f"/api/quotations/{q['id']}/issue", headers=h)
    assert r.json()["status"] == "issued" and r.json()["issued_at"]
    assert client.post(f"/api/quotations/{q['id']}/issue", headers=h).status_code == 409
    r = client.post(f"/api/quotations/{q['id']}/finalize", headers=h)
    assert r.json()["status"] == "finalized" and r.json()["finalized_at"]
    assert client.post(f"/api/quotations/{q['id']}/cancel", headers=h).status_code == 409

    # 取消: 草稿/已发出可取消，取消为终态
    q2 = _mk_quote(client, tok, cust)
    assert client.post(f"/api/quotations/{q2['id']}/cancel", headers=h).json()["status"] == "cancelled"
    assert client.post(f"/api/quotations/{q2['id']}/issue", headers=h).status_code == 409
    q3 = _mk_quote(client, tok, cust)
    client.post(f"/api/quotations/{q3['id']}/issue", headers=h)
    assert client.post(f"/api/quotations/{q3['id']}/cancel", headers=h).json()["status"] == "cancelled"


def test_edit_draft_only(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    q = _mk_quote(client, tok, cust)
    h = auth_hdr(tok)
    r = client.patch(
        f"/api/quotations/{q['id']}",
        json={"items": [{"item_name": "传导发射", "qty": 1, "unit_price": 2500}], "remark": "改过"},
        headers=h,
    )
    assert r.json()["items"][0]["item_name"] == "传导发射"
    assert r.json()["total"] == 2500.0 and r.json()["remark"] == "改过"
    # 发出后不可编辑
    client.post(f"/api/quotations/{q['id']}/issue", headers=h)
    assert client.patch(f"/api/quotations/{q['id']}", json={"items": ITEMS, "remark": "x"}, headers=h).status_code == 409


def test_search_and_filter(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok, "搜索目标客户")
    _mk_quote(client, tok, cust)
    h = auth_hdr(tok)
    r = client.get("/api/quotations", params={"q": "搜索目标客户"}, headers=h)
    assert len(r.json()) == 1 and r.json()[0]["customer_name"] == "搜索目标客户"
    r = client.get("/api/quotations", params={"q": "Q-"}, headers=h)
    assert len(r.json()) >= 1
    client.post(f"/api/quotations/{r.json()[0]['id']}/issue", headers=h)
    r = client.get("/api/quotations", params={"status": "issued"}, headers=h)
    assert all(x["status"] == "issued" for x in r.json()) and len(r.json()) >= 1
